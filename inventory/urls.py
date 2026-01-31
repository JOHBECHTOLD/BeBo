from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('box/new/', views.box_new, name='box_new'),
    path('box/<str:label>/', views.box_detail, name='box_detail'),
    path('box/<str:label>/edit/', views.box_edit, name='box_edit'),
]