from django import forms
from .models import Box

# 1. Das Widget: Erlaubt HTML-seitig mehrere Dateien (multiple)
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# 2. Das Feld: Erlaubt Python-seitig eine Liste von Dateien
class MultipleFileField(forms.FileField):
    def to_python(self, data):
        if not data:
            return None
        # Wenn wir eine Liste bekommen, prüfen wir jede Datei einzeln
        if isinstance(data, list):
            return [super(MultipleFileField, self).to_python(f) for f in data]
        # Wenn es nur eine Datei ist, packen wir sie in eine Liste
        return [super(MultipleFileField, self).to_python(data)]

    def clean(self, data, initial=None):
        # Wenn nichts da ist, ist es okay (da required=False)
        if not data:
            return None
        # Wir geben die bereinigte Liste zurück
        return self.to_python(data)

# 3. Das Formular
class BoxForm(forms.ModelForm):
    # Wir nutzen unser neues Feld und unser neues Widget
    image_upload = MultipleFileField( 
        required=False, 
        label="Bilder hinzufügen (Mehrfachauswahl möglich)",
        widget=MultipleFileInput(attrs={
            'class': 'form-control', 
            'accept': 'image/*', 
            'multiple': True 
        })
    )

    class Meta:
        model = Box
        fields = ['label', 'location', 'status', 'description', 'categories']
        
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control font-monospace'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }