from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Box, BoxImage
from .forms import BoxForm

@login_required
def dashboard(request):
    # Hole alle Boxen, sortiert nach Update-Datum (neueste zuerst)
    boxes = Box.objects.all().order_by('-updated_at')
    
    return render(request, 'inventory/dashboard.html', {
        'boxes': boxes,
        'total_count': boxes.count()
    })
@login_required
def box_detail(request, label):
    # Wir suchen die Box anhand des Barcodes (label). 
    # Wenn sie nicht existiert, kommt automatisch Fehler 404 (Seite nicht gefunden).
    box = get_object_or_404(Box, label=label)
    
    return render(request, 'inventory/box_detail.html', {
        'box': box,
    })
@login_required
def box_edit(request, label):
    box = get_object_or_404(Box, label=label)
    original_label = box.label
    
    if request.method == 'POST':
        # Wenn Daten gesendet wurden (Speichern Button gedrückt)
        form = BoxForm(request.POST, request.FILES, instance=box)
        if form.is_valid():
            # 1. Box Daten speichern
            box = form.save()
            
            # 2. Bild speichern (falls eines hochgeladen wurde)
            image = form.cleaned_data.get('image_upload')
            if image:
                BoxImage.objects.create(box=box, image=image)
                
            # Zurück zur Detailseite
            return redirect('box_detail', label=box.label)
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
# NEU: Neue Box anlegen
@login_required
def box_new(request):
    if request.method == 'POST':
        form = BoxForm(request.POST, request.FILES)
        if form.is_valid():
            box = form.save()
            # Falls direkt beim Erstellen ein Bild hochgeladen wurde:
            image = form.cleaned_data.get('image_upload')
            if image:
                BoxImage.objects.create(box=box, image=image)
            return redirect('box_detail', label=box.label)
    else:
        form = BoxForm()

    return render(request, 'inventory/box_form.html', {
        'form': form,
        'title': 'Neue Box anlegen' # Wir übergeben einen Titel für die Seite
    })
# NEU: Box löschen
@login_required
def box_delete(request, label):
    box = get_object_or_404(Box, label=label)
    
    if request.method == 'POST':
        # Wenn der rote Knopf "Bestätigen" gedrückt wurde
        box.delete()
        # Bilder werden automatisch mitgelöscht (wegen on_delete=CASCADE im Model)
        return redirect('dashboard')
    
    # Zeige die Bestätigungsseite an
    return render(request, 'inventory/box_confirm_delete.html', {'box': box})