"""
URL configuration for Supermerengones project.
"""
from django.contrib import admin
from django.urls import path, include
from views import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Rutas de la Aplicación Principal
    path('', views.index, name='index'),

    # 2. Rutas de Administración
    path('admin/', admin.site.urls),

    # Páginas públicas
    path('productos/', views.productos, name='productos'),
    path('promociones/', views.promociones, name='promociones'),
    path('sedes/', views.sedes, name='sedes'),
    path('carrito/', views.carrito, name='carrito'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # 3. Rutas de la API
    path('api/', include('api_urls')),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    # STATICFILES_DIRS[0] ya apunta a la carpeta static del proyecto
    try:
        static_root = str(settings.STATICFILES_DIRS[0])
    except Exception:
        static_root = None
    if static_root:
        urlpatterns += static(settings.STATIC_URL, document_root=static_root)