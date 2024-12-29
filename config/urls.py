from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.pos.urls')),  # Point d'entrée principal pour le POS
]