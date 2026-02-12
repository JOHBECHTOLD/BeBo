from django import forms
from django.db.models.functions import Lower
from .models import Box, Location, Category

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

    def __init__(self, *args, **kwargs):
        super(BoxForm, self).__init__(*args, **kwargs)
        
        # Sortiere das 'location'-Feld alphabetisch nach dem Namen
        self.fields['location'].queryset = Location.objects.order_by(Lower('name'))
        
        # Sortiere das 'categories'-Feld alphabetisch nach dem Namen
        self.fields['categories'].queryset = Category.objects.order_by(Lower('name'))

        # Das 'status'-Feld ist ein Choices-Feld, keine Datenbank-Abfrage.
        # Wenn wir es sortieren wollen, müssen wir die Choices direkt manipulieren.
        # Wir sortieren nach dem zweiten Element jedes Tupels (dem sichtbaren Namen).
        # (('STORED', 'Gelagert'), ('IN_USE', 'In Benutzung')) -> sortiert nach 'Gelagert', 'In Benutzung'
        
        # Holen der aktuellen Choices
        status_choices = list(self.fields['status'].choices)
        
        # Sortieren der Choices-Liste basierend auf dem lesbaren Namen (index 1)
        # Wir überspringen den leeren Eintrag ('---------'), falls vorhanden.
        # Der leere Eintrag ist normalerweise der erste.
        first_choice = status_choices[0]
        if first_choice[0] == '': # Prüfung, ob es ein leerer Auswahl-Platzhalter ist
            sorted_choices = sorted(status_choices[1:], key=lambda x: x[1].lower())
            self.fields['status'].choices = [first_choice] + sorted_choices
        else:
            sorted_choices = sorted(status_choices, key=lambda x: x[1].lower())
            self.fields['status'].choices = sorted_choices

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