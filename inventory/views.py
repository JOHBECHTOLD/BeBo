from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Box, BoxImage, Location, Category
from .forms import BoxForm
from django.db.models import Q
from django.core.paginator import Paginator

# Imports für Feature Release 1.6.0
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q


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
    # Basis-Abfrage: Hole die Historie aller Boxen
    # Das .order_by() hier wird unser Standard, falls keine Sortierung angegeben ist.
    history_qs = Box.history.all().select_related('history_user', 'location').order_by('-history_date')
    
    view_title = "Alle Aktivitäten"

    # --- 1. USER-FILTER LOGIK (bleibt gleich) ---
    user_filter = request.GET.get('user')
    if user_filter == 'me' and request.user.is_authenticated:
        history_qs = history_qs.filter(history_user=request.user)
        view_title = "Meine Aktivitäten"

    # --- 2. NEUE SORTIER-LOGIK ---
    # Standard-Sortierung
    sort_by = request.GET.get('sort', '-history_date') # Default: neueste zuerst
    sort_dir = request.GET.get('dir', 'desc')

    # Mapping von URL-Parametern zu echten DB-Feldern, um Sicherheit zu gewährleisten
    # und nach verknüpften Feldern zu sortieren (z.B. user__username).
    valid_sort_fields = {
        'wann': 'history_date',
        'wer': 'history_user__username',
        'aktion': 'history_type',
        'box': 'label',
        'lagerort': 'location__name',
        'status': 'status',
    }

    # Hole den DB-Feldnamen aus unserem Mapping
    db_field = valid_sort_fields.get(request.GET.get('sort'))

    if db_field:
        # Wenn die Richtung 'desc' (absteigend) ist, fügen wir ein '-' vor den Feldnamen
        if sort_dir == 'desc':
            sort_by = f'-{db_field}'
        else:
            sort_by = db_field
            
        # Wende die Sortierung an
        history_qs = history_qs.order_by(sort_by)

    # Pagination: Zeige 50 Einträge pro Seite
    paginator = Paginator(history_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Baue einen String mit den aktuellen Query-Parametern für die Links im Template
    # Wir schließen 'page' aus, da es von den Paginierungslinks selbst hinzugefügt wird.
    current_params = request.GET.copy()
    if 'page' in current_params:
        del current_params['page']
    
    # Aktuelle Sortierrichtung für die Links im Template bestimmen
    # Wenn aktuell aufsteigend sortiert wird, soll der nächste Klick absteigend sein
    next_sort_dir = 'asc' if sort_dir == 'desc' else 'desc'
    
    return render(request, 'inventory/global_history.html', {
        'page_obj': page_obj,
        'view_title': view_title,
        'current_sort': request.GET.get('sort'), # Welches Feld ist sortiert?
        'current_dir': sort_dir,                 # In welche Richtung?
        'next_sort_dir': next_sort_dir,          # Was ist die nächste Richtung?
        'query_params': current_params.urlencode(), # z.B. "user=me&sort=wer&dir=asc"
    })

# View für die Changelog-Seite
@login_required
def changelog_view(request):
    return render(request, 'inventory/changelog.html')


# --- Feature Release 1.6.0: Stammdaten-Verwaltung (CRUD) ---
# Wir verwenden Class-Based Views (CBVs) für Standard-Operationen.
# Das LoginRequiredMixin stellt sicher, dass nur eingeloggte Benutzer zugreifen können.

# --- LAGERORT (LOCATION) VIEWS ---

class LocationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'inventory.view_location'
    model = Location
    template_name = 'inventory/location_list.html'          # Dieses Template müssen wir erstellen
    context_object_name = 'locations'                       # Name der Variable im Template
    ordering = ['name']                                     # Sortiert die Liste alphabetisch

class LocationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventory.add_location'
    model = Location
    fields = ['name', 'description', 'is_external']         # Welche Felder sollen im Formular sein?
    template_name = 'inventory/location_form.html'          # Dieses Template müssen wir erstellen
    success_url = reverse_lazy('location_list')             # Wohin nach erfolgreichem Speichern?

class LocationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.change_location'
    model = Location
    fields = ['name', 'description', 'is_external']
    template_name = 'inventory/location_form.html'          # Nutzt das gleiche Template wie CreateView
    success_url = reverse_lazy('location_list')

class LocationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.delete_location'
    model = Location
    template_name = 'inventory/location_confirm_delete.html' # Dieses Template müssen wir erstellen
    success_url = reverse_lazy('location_list')

# --- Feature Release 1.6.0: KATEGORIEN (CATEGORY) VIEWS ---

class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'inventory.view_category'
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']

class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventory.add_category'
    model = Category
    fields = ['name', 'color'] # ACHTUNG: Felder an das Category-Model anpassen!
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.change_category'
    model = Category
    fields = ['name', 'color'] # ACHTUNG: Felder an das Category-Model anpassen!
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.delete_category'
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    # --- Feature Release 1.6.0: BOX (BOX) VIEWS ---

class BoxListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'inventory.view_box'
    model = Box
    template_name = 'inventory/dashboard.html'              # Das Dashboard dient als Liste
    context_object_name = 'boxes'
    ordering = ['-updated_at']                              # Letzte Änderung zuerst
    raise_exception = True                                  # Zeigt 403 Fehler bei fehlender Berechtigung

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 1. Parameter aus der URL holen
        search_query = self.request.GET.get('q')            # Suchbegriff aus dem Suchformular
        location_id = self.request.GET.get('location')      # Filter für Lagerort (Antippen)
        category_id = self.request.GET.get('category')      # Filter für Kategorie (Antippen)
        status_filter = self.request.GET.get('status')      # Filter für Status (Antippen der Badges)

        # --- LOGIK: GEZIELTE FILTER (Antippen von Badges/Links) ---
        if location_id:
            queryset = queryset.filter(location_id=location_id)
            
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # --- LOGIK: VOLLTEXTSUCHE (Manuelle Eingabe im Suchfeld) ---
        if search_query:
            # Mapping deutscher Begriffe auf die Datenbank-Werte (STATUS_CHOICES)
            status_map = {
                'gelagert': 'STORED',
                'verliehen': 'LENT',
                'zugriff': 'ACCESS',
                'extern': 'EXT',
                'transit': 'TRANSIT',
                'verloren': 'LOST',
                'unbekannt': 'LOST'
            }
            mapped_status = status_map.get(search_query.lower())

            # Suche über alle relevanten Felder mit Q-Objekten
            q_objects = Q(label__icontains=search_query) | \
                        Q(description__icontains=search_query) | \
                        Q(location__name__icontains=search_query) | \
                        Q(categories__name__icontains=search_query)

            # Falls der Suchbegriff einem Status entspricht, diesen in die Suche einbeziehen
            if mapped_status:
                q_objects |= Q(status=mapped_status)

            queryset = queryset.filter(q_objects).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # total_count muss auf dem bereits gefilterten Queryset basieren
        context['total_count'] = self.get_queryset().count()
        # Suchbegriff für das Template bereitstellen
        context['search_query'] = self.request.GET.get('q', '')
        return context
    

class BoxDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'inventory.view_box'
    model = Box
    template_name = 'inventory/box_detail.html'
    context_object_name = 'box'
    slug_field = 'label'        # Name des Feldes in deinem Model (z.B. 'label' oder 'barcode')
    slug_url_kwarg = 'label_id'       # Name des Parameters aus der urls.py (dort haben wir 'pk' genutzt)

class BoxCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inventory.add_box'
    model = Box
    # Felder an dein Model anpassen (Beispielhaft):
    fields = ['label', 'location', 'categories', 'status', 'description']
    template_name = 'inventory/box_form.html'
    success_url = reverse_lazy('dashboard')
    raise_exception = True

class BoxUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inventory.change_box'
    model = Box
    # Felder an dein Model anpassen:
    fields = ['label', 'location', 'categories', 'status', 'description']
    template_name = 'inventory/box_form.html'
    success_url = reverse_lazy('dashboard')
    slug_field = 'label' 
    slug_url_kwarg = 'label_id'

class BoxDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'inventory.delete_box'
    model = Box
    template_name = 'inventory/box_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    slug_field = 'label' 
    slug_url_kwarg = 'label_id'