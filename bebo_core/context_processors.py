from django.conf import settings

def bebo_version(request):
    # Gibt die Version an alle Templates weiter
    return {
        'bebo_version': getattr(settings, 'BEBO_VERSION', '1.0.0')
    }