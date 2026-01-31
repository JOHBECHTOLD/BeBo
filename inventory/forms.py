from django import forms
from .models import Box, BoxImage

class BoxForm(forms.ModelForm):
    # Ein Zusatzfeld für den Upload eines Bildes
    image_upload = forms.ImageField(
        required=False, 
        label="Neues Bild hinzufügen",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Box
        # Diese Felder darf der User bearbeiten:
        fields = ['label', 'location', 'status', 'description', 'categories']
        
        # Damit es hübsch aussieht (Bootstrap Klassen)
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control font-monospace'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }