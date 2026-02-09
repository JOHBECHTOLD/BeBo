# Erstellt in Version 1.5.3
from django import template

register = template.Library()

@register.filter(name='format_barcode')
def format_barcode(value):
    """
    Formatiert einen 12-stelligen Barcode in das Format 94.xxxxxxxxx.p.
    Beispiel: '941234567895' -> '94.123456789.5'
    """
    # Prüft, ob der Wert ein String ist, genau 12 Zeichen lang und nur aus Ziffern besteht.
    if isinstance(value, str) and len(value) == 12 and value.isdigit():
        # Baut den neuen String mit Punkten zusammen.
        return f"{value[:2]}.{value[2:11]}.{value[11:]}"
    
    # Wenn der Wert nicht dem erwarteten Format entspricht, gib ihn unverändert zurück.
    return value

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Dieser Tag ersetzt oder fügt Query-Parameter in der aktuellen URL hinzu.
    Sehr nützlich für Paginierung, Filter und Sortierung.
    """
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()