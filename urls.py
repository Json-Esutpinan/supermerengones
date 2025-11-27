"""
URL configuration for Supermerengones project.
"""
from django.contrib import admin
from django.urls import path, include
from views import views 

urlpatterns = [
    # 1. Rutas de la Aplicación Principal 
    path('', views.index, name='index'), 
    
    # 2. Rutas de Administración
    path('admin/', admin.site.urls),
    
    # 3. Rutas de la API 
    path('api/', include('api_urls')), 
]