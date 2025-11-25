"""
URL configuration for API endpoints
"""
from django.urls import path
from views.viewsProveedor import (
    crear_proveedor,
    listar_proveedores,
    obtener_proveedor,
    modificar_proveedor,
    desactivar_proveedor,
    cambiar_estado_proveedor
)
from views.viewsPedidos import (
    historial_pedidos_cliente,
    obtener_detalle_pedido,
    listar_pedidos_por_estado,
    listar_pedidos_por_fecha,
    listar_todos_pedidos
)

from views.viewsSede import (
    crear_sede,
    listar_sedes,
    obtener_sede,
    modificar_sede,
    desactivar_sede,
    vista_consolidada_sede
)

urlpatterns = [
    # Rutas para proveedores
    path('proveedores/', listar_proveedores, name='listar_proveedores'),
    path('proveedores/crear/', crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:id_proveedor>/', obtener_proveedor, name='obtener_proveedor'),
    path('proveedores/<int:id_proveedor>/modificar/', modificar_proveedor, name='modificar_proveedor'),
    path('proveedores/<int:id_proveedor>/estado/', cambiar_estado_proveedor, name='cambiar_estado_proveedor'),
    path('proveedores/<int:id_proveedor>/desactivar/', desactivar_proveedor, name='desactivar_proveedor'),
    
    # Rutas para pedidos (historial)
    path('pedidos/', listar_todos_pedidos, name='listar_todos_pedidos'),
    path('pedidos/<int:id_pedido>/', obtener_detalle_pedido, name='obtener_detalle_pedido'),
    path('pedidos/cliente/<int:id_cliente>/historial/', historial_pedidos_cliente, name='historial_pedidos_cliente'),
    path('pedidos/estado/<str:estado>/', listar_pedidos_por_estado, name='listar_pedidos_por_estado'),
    path('pedidos/fecha/', listar_pedidos_por_fecha, name='listar_pedidos_por_fecha'),

    # Rutas para sedes
    path('sedes/', listar_sedes, name='listar_sedes'),
    path('sedes/crear/', crear_sede, name='crear_sede'),
    path('sedes/<int:id_sede>/', obtener_sede, name='obtener_sede'),
    path('sedes/<int:id_sede>/modificar/', modificar_sede, name='modificar_sede'),
    path('sedes/<int:id_sede>/desactivar/', desactivar_sede, name='desactivar_sede'),
    path('sedes/<int:id_sede>/consolidado/', vista_consolidada_sede, name='vista_consolidada_sede'),
]
