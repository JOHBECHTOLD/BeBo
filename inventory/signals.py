# inventory/signals.py

from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone  # <--- WICHTIG: Import für die aktuelle Zeit
from .models import Box, BoxImage, Category

# Helper-Funktion, um Codeduplizierung zu vermeiden
def create_manual_history_record(instance, change_reason, history_type='~'):
    """
    Erstellt manuell einen Verlaufseintrag für eine gegebene Instanz (z.B. eine Box).
    Dieser Weg ist kompatibel mit älteren Versionen von django-simple-history.
    """
    HistoricalModel = instance.history.model
    
    # Erstelle ein Dictionary mit allen Feldwerten der Instanz
    attrs = {field.name: getattr(instance, field.name) for field in instance._meta.fields}
    
    # Füge die speziellen Felder für den Verlauf hinzu
    attrs['history_change_reason'] = change_reason
    attrs['history_user'] = getattr(instance, '_history_user', None)
    
    # KORREKTUR: Füge die fehlenden, obligatorischen Felder hinzu
    attrs['history_date'] = timezone.now()
    attrs['history_type'] = history_type # '~' steht für "Änderung" (Change)
    
    # Erstelle den Verlaufseintrag
    HistoricalModel.objects.create(**attrs)


# --- Signal für Kategorie-Änderungen ---
@receiver(m2m_changed, sender=Box.categories.through)
def log_category_changes(sender, instance, action, pk_set, **kwargs):
    """
    Erstellt einen Verlaufseintrag, wenn Kategorien zu einer Box hinzugefügt/entfernt werden.
    """
    if action in ["post_add", "post_remove"]:
        category_names = ", ".join(Category.objects.filter(pk__in=pk_set).values_list('name', flat=True))

        if action == "post_add":
            change_reason = f"Kategorien hinzugefügt: {category_names}"
        else: # post_remove
            change_reason = f"Kategorien entfernt: {category_names}"
        
        # Verwende unsere Helper-Funktion
        create_manual_history_record(instance, change_reason)


# --- Signal für das Hinzufügen von Bildern ---
@receiver(post_save, sender=BoxImage)
def log_image_add(sender, instance, created, **kwargs):
    """
    Erstellt einen Verlaufseintrag, wenn ein neues Bild zu einer Box hinzugefügt wird.
    """
    if created:
        box = instance.box
        change_reason = f"Bild hinzugefügt: {instance.image.name.split('/')[-1]}" # Nur Dateiname anzeigen
        create_manual_history_record(box, change_reason)


# --- Signal für das Löschen von Bildern ---
@receiver(post_delete, sender=BoxImage)
def log_image_delete(sender, instance, **kwargs):
    """
    Erstellt einen Verlaufseintrag, wenn ein Bild von einer Box gelöscht wird.
    """
    box = instance.box
    change_reason = f"Bild gelöscht: {instance.image.name.split('/')[-1]}" # Nur Dateiname anzeigen
    create_manual_history_record(box, change_reason)