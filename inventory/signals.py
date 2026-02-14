from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from simple_history.utils import update_change_reason

from .models import BoxImage


@receiver(post_save, sender=BoxImage)
def log_image_add(sender, instance, created, **kwargs):
    """
    Protokolliert das Hinzufügen eines Bildes an einer Box.

    Vorgehen:
    - Text (history_change_reason) an die Box hängen
    - box.save() aufrufen
    -> simple_history erzeugt den History-Eintrag sauber (inkl. Benutzer).
    """
    if not created:
        return

    box = instance.box
    filename = instance.image.name.split('/')[-1]
    reason = f"Bild hinzugefügt: {filename}"

    # Falls der View bereits _history_user gesetzt hat, nutzt simple_history diesen.
    update_change_reason(box, reason)
    box.save()


@receiver(post_delete, sender=BoxImage)
def log_image_delete(sender, instance, **kwargs):
    """
    Protokolliert das Löschen eines Bildes an einer Box.
    """
    box = instance.box
    filename = instance.image.name.split('/')[-1]
    reason = f"Bild gelöscht: {filename}"

    update_change_reason(box, reason)
    box.save()