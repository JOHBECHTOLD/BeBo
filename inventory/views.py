from django.shortcuts import render, get_object_or_404, redirect
from .models import Box, BoxImage
from .forms import BoxForm

def dashboard(request):
    # Hole alle Boxen, sortiert nach Update-Datum (neueste zuerst)
    boxes = Box.objects.all().order_by('-updated_at')
    
    return render(request, 'inventory/dashboard.html', {
        'boxes': boxes,
        'total_count': boxes.count()
    })

def box_detail(request, label):
    # Wir suchen die Box anhand des Barcodes (label). 
    # Wenn sie nicht existiert, kommt automatisch Fehler 404 (Seite nicht gefunden).
    box = get_object_or_404(Box, label=label)
    
    return render(request, 'inventory/box_detail.html', {
        'box': box,
    })
def box_edit(request, label):
    box = get_object_or_404(Box, label=label)
    
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
    
    return render(request, 'inventory/box_form.html', {
        'form': form,
        'box': box
    })