from django.contrib import admin
from .models import Location, Box, Category, BoxImage
from simple_history.admin import SimpleHistoryAdmin

# Bilder direkt in der Box-Ansicht anzeigen
class BoxImageInline(admin.TabularInline):
    model = BoxImage
    extra = 1

@admin.register(Box)
class BoxAdmin(SimpleHistoryAdmin):
    list_display = ('label', 'location', 'status', 'updated_at')
    search_fields = ('label', 'description')
    list_filter = ('location', 'status', 'categories')
    inlines = [BoxImageInline]

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_external')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')