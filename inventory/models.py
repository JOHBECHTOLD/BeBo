from django.db import models
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError
from simple_history.utils import update_change_reason

# --- Hilfsfunktionen (Deine Prüfziffern-Logik) ---

def validate_barcode(value):
    """
    Prüft das Format 94.xxxxxxxxx.p
    und berechnet die Prüfziffer nach Bechtold-Algorithmus.
    """
    # 1. Format bereinigen (Punkte entfernen)
    clean_code = value.replace('.', '')
    
    if not clean_code.startswith('94'):
        raise ValidationError(f"Code muss mit 94 beginnen. Gegeben: {value}")
    
    if len(clean_code) != 12: # 94 + 9 Ziffern + 1 Prüfziffer
        raise ValidationError(f"Code hat falsche Länge ({len(clean_code)}). Erwartet: 12 Ziffern (ohne Punkte).")
        
    if not clean_code.isdigit():
        raise ValidationError("Code darf nur Ziffern enthalten.")

    # 2. Prüfziffer berechnen
    # Wir nehmen die 9 Ziffern zwischen '94' und der letzten Ziffer
    payload = clean_code[2:11] 
    check_digit_input = int(clean_code[11])

    # Gewichtung: 3, 1, 3, 1...
    weights = [3, 1, 3, 1, 3, 1, 3, 1, 3]
    total_sum = 0
    
    for i, digit in enumerate(payload):
        total_sum += int(digit) * weights[i]
        
    # Modulo 10
    remainder = total_sum % 10
    
    # Ergebnis: 10 - Rest
    calculated_check_digit = (10 - remainder)
    if calculated_check_digit == 10:
        calculated_check_digit = 0 

    if check_digit_input != calculated_check_digit:
        raise ValidationError(f"Prüfziffer falsch! Erwartet: {calculated_check_digit}, Gelesen: {check_digit_input}")


# --- Datenbank Tabellen ---

class Location(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Beschreibung", blank=True)
    is_external = models.BooleanField("Ist extern/Transit", default=False, help_text="z.B. Nachbar, Verliehen")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Lagerort"
        verbose_name_plural = "Lagerorte"

class Category(models.Model):
    name = models.CharField("Kategorie", max_length=50)
    color = models.CharField("Farbe (Hex)", max_length=7, default="#203564")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"

class Box(models.Model):
    STATUS_CHOICES = [
        ('STORED', 'Gelagert'),
        ('ACCESS', 'Im Zugriff'),
        ('TRANSIT', 'Im Transit'),
        ('LENT', 'Verliehen'),
        ('LOST', 'Verloren/Unbekannt'),
        ('EXT', 'Extern'),
    ]

    label = models.CharField("Barcode (94...)", max_length=20, unique=True, validators=[validate_barcode])
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name="Lagerort")
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default='STORED')
    description = models.TextField("Inhalt / Beschreibung", blank=True)
    categories = models.ManyToManyField(Category, blank=True, verbose_name="Kategorien")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(m2m_fields=[categories])

    def save(self, *args, **kwargs):
        """
        Ergänzt bei Status-Änderungen einen verständlichen History-Text.
        """
        change_reason = None

        if self.pk:  # nur bei Updates vergleichen
            try:
                old = Box.objects.get(pk=self.pk)
            except Box.DoesNotExist:
                old = None

            if old and old.status != self.status:
                old_status = old.get_status_display()
                new_status = self.get_status_display()
                change_reason = f"Status geändert: {old_status} → {new_status}"

        # Erst das eigentliche Speichern (hier legt simple_history den Eintrag an)
        super().save(*args, **kwargs)
        
        if change_reason:
            update_change_reason(self, change_reason)

    def __str__(self):
        return f"Box {self.label} ({self.location})"

    class Meta:
        verbose_name = "Box"
        verbose_name_plural = "Boxen"

class BoxImage(models.Model):
    box = models.ForeignKey(Box, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField("Bild", upload_to='box_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bild für {self.box.label}"