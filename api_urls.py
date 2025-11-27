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
from views.viewsProducto import (
    listar_productos,
    obtener_producto,
)
from views.viewsReclamo import (
    listar_reclamos_cliente,
    listar_reclamos_pedido,
    obtener_reclamo,
    listar_reclamos_por_estado,
    listar_todos_reclamos,
    crear_reclamo,
    cambiar_estado_reclamo,
    agregar_respuesta_reclamo
)
from views.viewsAuth import (
    login_view,
    registrar_cliente_view,
    usuario_actual_view
)
from views.viewsPromocion import (
    listar_promociones,
    obtener_promocion,
    crear_promocion,
    modificar_promocion,
    eliminar_promocion
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
    
    # Rutas para reclamos
    path('reclamos/', listar_todos_reclamos, name='listar_todos_reclamos'),
    path('reclamos/crear/', crear_reclamo, name='crear_reclamo'),
    path('reclamos/<int:id_reclamo>/', obtener_reclamo, name='obtener_reclamo'),
    path('reclamos/<int:id_reclamo>/estado/', cambiar_estado_reclamo, name='cambiar_estado_reclamo'),
    path('reclamos/<int:id_reclamo>/respuesta/', agregar_respuesta_reclamo, name='agregar_respuesta_reclamo'),
    path('reclamos/cliente/<int:id_cliente>/', listar_reclamos_cliente, name='listar_reclamos_cliente'),
    path('reclamos/pedido/<int:id_pedido>/', listar_reclamos_pedido, name='listar_reclamos_pedido'),
    path('reclamos/estado/', listar_reclamos_por_estado, name='listar_reclamos_por_estado'),

    # Rutas para productos
    path('productos/', listar_productos, name='listar_productos'),
    path('productos/<int:id_producto>/', obtener_producto, name='obtener_producto'),

    # Rutas para promociones
    path('promociones/', listar_promociones, name='listar_promociones'),
    path('promociones/crear/', crear_promocion, name='crear_promocion'),
    path('promociones/<int:id>/', obtener_promocion, name='obtener_promocion'),
    path('promociones/<int:id>/modificar/', modificar_promocion, name='modificar_promocion'),
    path('promociones/<int:id>/eliminar/', eliminar_promocion, name='eliminar_promocion'),

    #Rutas para autenticación
    path("auth/login/", login_view),
    path("auth/registrar-cliente/", registrar_cliente_view),
    path("auth/usuario/", usuario_actual_view),
]
