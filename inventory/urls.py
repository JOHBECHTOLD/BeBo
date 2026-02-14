from django.urls import path
from .views import (
    # --- Verbleibende Funktions-Views --- 
    global_history, 
    changelog_view,
    
    # --- Feature Release 1.6.0: Box Management (CBVs) ---
    BoxListView,
    BoxDetailView,
    BoxCreateView, 
    BoxUpdateView, 
    BoxDeleteView,
    BoxImageDeleteView,
    
    # --- Feature Release 1.6.0: Stammdaten (CBVs) ---
    LocationListView, 
    LocationCreateView, 
    LocationUpdateView, 
    LocationDeleteView,
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
)

urlpatterns = [
    # --- BOX VERWALTUNG ---
    # Wir nutzen BoxListView für das Dashboard, um die Rechteprüfung (view_box) zu erzwingen.
    path('', BoxListView.as_view(), name='dashboard'),                                          # 1.6.0 Feature
    path('box/new/', BoxCreateView.as_view(), name='box_new'),                                  # 1.6.0 Feature
    path('box/<str:label_id>/', BoxDetailView.as_view(), name='box_detail'),                    # 1.6.0 Feature
    path('box/<str:label_id>/edit/', BoxUpdateView.as_view(), name='box_edit'),                 # 1.6.0 Feature
    path('box/<str:label_id>/delete/', BoxDeleteView.as_view(), name='box_delete'),             # 1.6.0 Feature

    # Bilder löschen über die CBV
    path('image/<int:pk>/delete/', BoxImageDeleteView.as_view(), name='image_delete'),          # 1.6.0 Feature

    # --- LAGERORTE (LOCATIONS) ---
    path('locations/', LocationListView.as_view(), name='location_list'),                       # 1.6.0 Feature
    path('locations/new/', LocationCreateView.as_view(), name='location_create'),               # 1.6.0 Feature
    path('locations/<int:pk>/edit/', LocationUpdateView.as_view(), name='location_update'),     # 1.6.0 Feature
    path('locations/<int:pk>/delete/', LocationDeleteView.as_view(), name='location_delete'),   # 1.6.0 Feature

    # --- KATEGORIEN (CATEGORIES) ---
    path('categories/', CategoryListView.as_view(), name='category_list'),                      # 1.6.0 Feature
    path('categories/new/', CategoryCreateView.as_view(), name='category_create'),              # 1.6.0 Feature
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),    # 1.6.0 Feature
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),  # 1.6.0 Feature

    # --- SONSTIGES (Historie, Changelog) ---
    path('history/', global_history, name='global_history'),
    path('changelog/', changelog_view, name='changelog'),
]