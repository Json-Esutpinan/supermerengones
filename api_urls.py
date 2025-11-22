"""
URL configuration for API endpoints
"""
from django.urls import path
from views import (
    crear_proveedor,
    listar_proveedores,
    obtener_proveedor,
    modificar_proveedor,
    desactivar_proveedor,
    cambiar_estado_proveedor
)

urlpatterns = [
    # Rutas para proveedores
    path('proveedores/', listar_proveedores, name='listar_proveedores'),
    path('proveedores/crear/', crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:id_proveedor>/', obtener_proveedor, name='obtener_proveedor'),
    path('proveedores/<int:id_proveedor>/modificar/', modificar_proveedor, name='modificar_proveedor'),
    path('proveedores/<int:id_proveedor>/estado/', cambiar_estado_proveedor, name='cambiar_estado_proveedor'),
    path('proveedores/<int:id_proveedor>/desactivar/', desactivar_proveedor, name='desactivar_proveedor'),
]
