from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')), # Wir leiten die Startseite auf unsere App um
    # Djangos eingebaute Auth-URLs (Login, Logout, PasswordChange...)
    # Wir nutzen "accounts/" als Standard-Pfad
    path('accounts/', include('django.contrib.auth.urls')),
]

# Media-Dateien servieren (auch in Production)
# In Production übernimmt normalerweise Nginx/Caddy, aber für kleine Apps ist das OK
# Nutzt django.views.static.serve statt static() - funktioniert auch mit Gunicorn
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]