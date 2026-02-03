from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Box, BoxImage
from .forms import BoxForm
from django.db.models import Q
from django.core.paginator import Paginator

@login_required
def dashboard(request):
    # 1. Suchbegriff aus der URL holen (z.B. ?q=Weihnachten)
    query = request.GET.get('q')
    
    # 2. Basis: Erstmal alle Boxen nehmen
    boxes = Box.objects.all().order_by('-updated_at')
    
    # 3. Wenn gesucht wurde, filtern wir die Liste
    if query:
        # Anpassung 1.5.3 Start
        # Wir bereinigen den Suchbegriff, indem wir eventuelle Punkte entfernen.
        # So funktioniert die Suche nach z.B. '94.123' und '94123' gleichermaßen.
        clean_query_for_label = query.replace('.', '')
        # Anpassung 1.5.3 Ende 

        boxes = boxes.filter(
                    Q(label__icontains=clean_query_for_label) | # Suche im Barcode 1.5.3 Anpassung alt: Q(label__icontains=query) |
            Q(description__icontains=query) |        # Suche in Beschreibung
            Q(location__name__icontains=query) |     # Suche im Lagerort-Namen
            Q(categories__name__icontains=query)     # Suche in Kategorien
        ).distinct() # distinct verhindert Duplikate, falls mehrere Kategorien treffen

    return render(request, 'inventory/dashboard.html', {
        'boxes': boxes,
        'total_count': boxes.count(), # Zählt jetzt nur die gefundenen Boxen
        'search_query': query         # Damit das Suchfeld gefüllt bleibt
    })
@login_required
def box_detail(request, label):
    box = get_object_or_404(Box, label=label)
    
    # --- Historie mit Diffs vorbereiten ---
    # Wir laden die gesamte Historie
    history_records = list(box.history.all().order_by('-history_date'))
    history_data = []

    # Mapping für schöne deutsche Feldnamen
    field_names_de = {
        'location': 'Lagerort',
        'status': 'Status',
        'description': 'Beschreibung',
        'label': 'Barcode',
        'image': 'Bild',
    }
    # Erstelle eine Map von DB-Wert zu Anzeige-Wert für den Status
    status_display_map = dict(Box.STATUS_CHOICES)

    for i, record in enumerate(history_records):
        changes = []
        
        # Wenn es einen 'change_reason' gibt, ist das eine spezielle Änderung.
        if record.history_change_reason:
            changes.append({
                'field': 'Aktion', # Wir nennen das Feld einfach "Aktion"
                'old': '',
                'new': record.history_change_reason,
                'is_reason': True # Ein Flag für das Template, falls wir es anders darstellen wollen
            })

        # Wenn es einen Vorgänger gibt (und es nicht der allererste Eintrag "Erstellt" ist)
        if i < len(history_records) - 1:
            prev_record = history_records[i+1]
            
            # Die Funktion .diff_against() vergleicht zwei Einträge
            delta = record.diff_against(prev_record)
            
            for change in delta.changes:
                # Wir übersetzen den Feldnamen ins Deutsche (falls vorhanden)
                field_label = field_names_de.get(change.field, change.field)
                
                old_value = change.old
                new_value = change.new

                # Wenn sich der Status ändert, übersetzen wir die Werte
                if change.field == 'status':
                    old_value = status_display_map.get(change.old, change.old) # .get() verhindert Fehler, falls Wert nicht existiert
                    new_value = status_display_map.get(change.new, change.new)


                changes.append({
                    'field': field_label,
                    'old': old_value,
                    'new': new_value
                })

        history_data.append({
            'record': record,
            'changes': changes
        })

    return render(request, 'inventory/box_detail.html', {
        'box': box,
        'history_data': history_data, # <-- Wir übergeben jetzt unsere schlauen Daten
    })

@login_required
def box_edit(request, label):
    box = get_object_or_404(Box, label=label)
    original_label = box.label
    
    if request.method == 'POST':
        # Wenn Daten gesendet wurden (Speichern Button gedrückt)
        form = BoxForm(request.POST, request.FILES, instance=box)
        if form.is_valid():
            # 1. Instanz im Speicher erstellen, nicht sofort in DB speichern (commit=False)
            box_instance = form.save(commit=False)
            
            # 2. Den aktuellen Benutzer für den Verlauf an die Instanz heften.
            # simple-history und unsere Signale werden diesen User automatisch verwenden.
            box_instance._history_user = request.user
            
            # 3. Felder für das Speichern vorbereiten, um einen ValueError zu vermeiden.
            # Wir müssen sicherstellen, dass nur Felder gespeichert werden, die auch im Box-Model existieren.
            # Formularfelder wie 'image_upload' müssen herausgefiltert werden.
            
            # 3a. Hole alle Felder, die sich laut Formular geändert haben.
            changed_fields_from_form = form.changed_data or []
            
            # 3b. Hole eine Liste aller echten, speicherbaren Felder aus dem Box-Model.
            model_field_names = {field.name for field in Box._meta.fields}
            
            # 3c. Erstelle die finale Liste der zu speichernden Felder, indem wir die beiden Listen abgleichen.
            fields_to_update = [field for field in changed_fields_from_form if field in model_field_names]

            # 3d. Speichere die Instanz nur, wenn sich tatsächliche Model-Felder geändert haben.
            # Das verhindert einen leeren "Keine Felder geändert"-Log.
            if fields_to_update:
                 box_instance.save(update_fields=fields_to_update)

            # 4. Many-to-Many-Beziehungen (Kategorien) speichern.
            # Dies ist nach commit=False zwingend notwendig. Es löst auch unser m2m_changed-Signal aus.
            form.save_m2m()
            
            # 5. Hochgeladene Bilder verarbeiten
            images = request.FILES.getlist('image_upload')
            for img in images:
                # Wichtig: Das Bild mit der NEUEN `box_instance` verknüpfen
                BoxImage.objects.create(box=box_instance, image=img)
                
            # 6. Zurück zur Detailseite umleiten, mit dem Label der NEUEN Instanz
            # (wichtig, falls der Barcode selbst geändert wurde)
            return redirect('box_detail', label=box_instance.label)
    else:
        # Wenn die Seite nur aufgerufen wird -> Formular anzeigen
        form = BoxForm(instance=box)

    # TRICK: Falls das Formular Fehler hat (z.B. falsche Prüfziffer), hat das 'box' Objekt
    # im Speicher jetzt den falschen Code. Wir setzen es für die Anzeige auf das Original zurück.
    # Das Formularfeld selbst zeigt trotzdem die (falsche) Eingabe des Users an (via 'form'), 
    # damit er sie korrigieren kann. Aber der 'Abbrechen'-Link stimmt wieder!
    box.label = original_label 
    
    return render(request, 'inventory/box_form.html', {
        'form': form,
        'box': box
    })
    
@login_required
def box_new(request):
    if request.method == 'POST':
        form = BoxForm(request.POST, request.FILES)
        if form.is_valid():
            # Auch hier setzen wir den User, damit der erste Eintrag ("Erstellt") korrekt ist.
            box = form.save(commit=False)
            box._history_user = request.user
            box.save()
            form.save_m2m() # Wichtig nach commit=False

            #Multiupload von Bildern
            images = request.FILES.getlist('image_upload')
            for img in images:
                BoxImage.objects.create(box=box, image=img)

            return redirect('box_detail', label=box.label)
    else:
        form = BoxForm()

    return render(request, 'inventory/box_form.html', {
        'form': form,
        'title': 'Neue Box anlegen' # Wir übergeben einen Titel für die Seite
    })

@login_required
def box_delete(request, label):
    box = get_object_or_404(Box, label=label)
    
    if request.method == 'POST':
        # Wenn der rote Knopf "Bestätigen" gedrückt wurde
        box._history_user = request.user # Setze den User für den "Gelöscht"-Eintrag
        box.delete()
        # Bilder werden automatisch mitgelöscht (wegen on_delete=CASCADE im Model)
        return redirect('dashboard')
    
    # Zeige die Bestätigungsseite an
    return render(request, 'inventory/box_confirm_delete.html', {'box': box})

@login_required
def image_delete(request, image_id):
    image = get_object_or_404(BoxImage, id=image_id)
    # Wir holen uns die zugehörige Box
    box = image.box
    box_label = box.label
    
    # WICHTIG: Wir heften den User an die Box, BEVOR das Signal durch .delete() ausgelöst wird.
    box._history_user = request.user

    # Löschen des Bildes, dies löst unser post_delete Signal aus
    image.delete()
    
    # Zurück zur Bearbeiten-Seite der Box
    return redirect('box_edit', label=box_label)

@login_required
def global_history(request):
    # Wir holen die Historie aller Boxen, sortiert nach Datum (neueste zuerst)
    # select_related optimiert die Datenbankabfrage für User und Location
    history_qs = Box.history.all().select_related('history_user', 'location').order_by('-history_date')
    
    # Pagination: Zeige 50 Einträge pro Seite
    paginator = Paginator(history_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/global_history.html', {
        'page_obj': page_obj
    })

# View für die Changelog-Seite
@login_required
def changelog_view(request):
    return render(request, 'inventory/changelog.html')