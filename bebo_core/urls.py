from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')), # Wir leiten die Startseite auf unsere App um
    # Djangos eingebaute Auth-URLs (Login, Logout, PasswordChange...)
    # Wir nutzen "accounts/" als Standard-Pfad
    path('accounts/', include('django.contrib.auth.urls')),
]

# Media-Dateien servieren (auch in Production)
# In Production übernimmt normalerweise Nginx/Caddy, aber für kleine Apps ist das OK
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)