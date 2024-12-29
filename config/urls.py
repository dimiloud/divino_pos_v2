from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='pos/', permanent=False), name='home'),
    path('pos/', include('apps.pos.urls')),
]