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
    cambiar_estado_proveedor,
    obtener_estadisticas_proveedor
)
from views.viewsPedidos import (
    historial_pedidos_cliente,
    obtener_detalle_pedido,
    listar_pedidos_por_estado,
    listar_pedidos_por_fecha,
    listar_todos_pedidos,
    actualizar_estado_pedido,
    procesar_pago,
    obtener_estado_pago
)

from views.viewsSede import (
    crear_sede,
    listar_sedes,
    obtener_sede,
    modificar_sede,
    desactivar_sede,
    cambiar_estado_sede,
    vista_consolidada_sede
)
from views.viewsProducto import (
    listar_productos,
    obtener_producto,
    crear_producto,
    modificar_producto,
    cambiar_estado_producto,
    actualizar_stock_producto,
    verificar_disponibilidad_producto
)
from views.views import (
    api_productos_activos,
    api_pedidos_cliente,
    api_pedido_crear_token,
    api_pedido_detalle,
)
from views.viewsReclamo import (
    listar_reclamos_cliente,
    listar_reclamos_pedido,
    obtener_reclamo,
    listar_reclamos_por_estado,
    listar_todos_reclamos,
    crear_reclamo,
    cambiar_estado_reclamo,
    agregar_respuesta_reclamo,
    resolver_reclamo,
    rechazar_reclamo,
    obtener_estadisticas_reclamos
)
from views.viewsAuth import (
    registrar_empleado_view,
    registrar_administrador_view,
    usuario_actual_view,
)
from views.views import (
    api_auth_login_entry,
    api_auth_register_entry,
    api_auth_logout_entry,
)
from views.viewsPersonal import (
    listar_empleados,
    listar_empleados_por_sede,
    obtener_empleado,
    modificar_empleado,
    transferir_sede,
    desactivar_empleado,
    activar_empleado
)
from views.viewsTurno import (
    crear_turno,
    listar_turnos,
    listar_turnos_empleado,
    listar_turnos_fecha,
    listar_turnos_sede_fecha,
    obtener_turno,
    modificar_turno,
    eliminar_turno
)
from views.viewsNotificacion import (
    crear_notificacion,
    enviar_notificacion_masiva,
    listar_notificaciones_cliente,
    contar_no_leidas,
    obtener_notificacion,
    marcar_como_leida,
    marcar_todas_leidas,
    eliminar_notificacion,
    listar_todas_notificaciones
)
from views.viewsAsistencia import (
    registrar_entrada,
    registrar_salida,
    mis_registros,
    listar_asistencias,
    asistencias_por_fecha,
    asistencias_por_empleado,
    obtener_asistencia,
    modificar_asistencia,
    eliminar_asistencia,
    reporte_mensual,
    actualizar_estado,
    asistencias_por_estado
)
from views.viewsPromocion import (
    listar_promociones,
    obtener_promocion,
    crear_promocion,
    modificar_promocion,
    eliminar_promocion
)
from views.viewsCompra import (
    crear_compra,
    listar_compras,
    obtener_compra,
    cambiar_estado_compra,
    agregar_detalle_compra,
    listar_compras_por_proveedor,
    obtener_historial_insumo,
    listar_compras_por_estado
)
from views.viewsInventario import (
    listar_inventario_por_sede,
    listar_inventario_por_insumo,
    listar_stock_bajo,
    registrar_entrada_stock,
    registrar_salida_stock,
    transferir_entre_sedes,
    obtener_historial_movimientos,
    obtener_alertas_reposicion,
    verificar_stock_disponible
)
from views.viewsInsumo import (
    crear_insumo,
    listar_insumos,
    obtener_insumo,
    modificar_insumo,
    desactivar_insumo
)

urlpatterns = [
    # Rutas para proveedores
    path('proveedores/', listar_proveedores, name='listar_proveedores'),
    path('proveedores/crear/', crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:id_proveedor>/', obtener_proveedor, name='obtener_proveedor'),
    path('proveedores/<int:id_proveedor>/modificar/', modificar_proveedor, name='modificar_proveedor'),
    path('proveedores/<int:id_proveedor>/estado/', cambiar_estado_proveedor, name='cambiar_estado_proveedor'),
    path('proveedores/<int:id_proveedor>/desactivar/', desactivar_proveedor, name='desactivar_proveedor'),
    path('proveedores/<int:id_proveedor>/estadisticas/', obtener_estadisticas_proveedor, name='obtener_estadisticas_proveedor'),
    
    # Rutas para pedidos (historial)
    path('pedidos/', listar_todos_pedidos, name='listar_todos_pedidos'),
    path('pedidos/<int:id_pedido>/', obtener_detalle_pedido, name='obtener_detalle_pedido'),
    path('pedidos/<int:id_pedido>/estado/', actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('pedidos/<int:id_pedido>/pago/', procesar_pago, name='procesar_pago'),
    path('pedidos/<int:id_pedido>/estado-pago/', obtener_estado_pago, name='obtener_estado_pago'),
    path('pedidos/cliente/<int:id_cliente>/historial/', historial_pedidos_cliente, name='historial_pedidos_cliente'),
    path('pedidos/estado/<str:estado>/', listar_pedidos_por_estado, name='listar_pedidos_por_estado'),
    path('pedidos/fecha/', listar_pedidos_por_fecha, name='listar_pedidos_por_fecha'),

    # Rutas para sedes
    path('sedes/', listar_sedes, name='listar_sedes'),
    path('sedes/crear/', crear_sede, name='crear_sede'),
    path('sedes/<int:id_sede>/', obtener_sede, name='obtener_sede'),
    path('sedes/<int:id_sede>/modificar/', modificar_sede, name='modificar_sede'),
    path('sedes/<int:id_sede>/estado/', cambiar_estado_sede, name='cambiar_estado_sede'),
    path('sedes/<int:id_sede>/desactivar/', desactivar_sede, name='desactivar_sede'),
    path('sedes/<int:id_sede>/consolidado/', vista_consolidada_sede, name='vista_consolidada_sede'),
    
    # Rutas para reclamos
    path('reclamos/', listar_todos_reclamos, name='listar_todos_reclamos'),
    path('reclamos/crear/', crear_reclamo, name='crear_reclamo'),
    path('reclamos/<int:id_reclamo>/', obtener_reclamo, name='obtener_reclamo'),
    path('reclamos/<int:id_reclamo>/estado/', cambiar_estado_reclamo, name='cambiar_estado_reclamo'),
    path('reclamos/<int:id_reclamo>/respuesta/', agregar_respuesta_reclamo, name='agregar_respuesta_reclamo'),
    path('reclamos/<int:id_reclamo>/resolver/', resolver_reclamo, name='resolver_reclamo'),
    path('reclamos/<int:id_reclamo>/rechazar/', rechazar_reclamo, name='rechazar_reclamo'),
    path('reclamos/cliente/<int:id_cliente>/', listar_reclamos_cliente, name='listar_reclamos_cliente'),
    path('reclamos/pedido/<int:id_pedido>/', listar_reclamos_pedido, name='listar_reclamos_pedido'),
    path('reclamos/estado/', listar_reclamos_por_estado, name='listar_reclamos_por_estado'),
    path('reclamos/estadisticas/', obtener_estadisticas_reclamos, name='obtener_estadisticas_reclamos'),

    # Rutas para productos
    path('productos/activos/', api_productos_activos, name='api_productos_activos'),
    path('productos/', listar_productos, name='listar_productos'),
    path('productos/crear/', crear_producto, name='crear_producto'),
    path('productos/<int:id_producto>/', obtener_producto, name='obtener_producto'),
    path('productos/<int:id_producto>/modificar/', modificar_producto, name='modificar_producto'),
    path('productos/<int:id_producto>/estado/', cambiar_estado_producto, name='cambiar_estado_producto'),
    path('productos/<int:id_producto>/stock/', actualizar_stock_producto, name='actualizar_stock_producto'),
    path('productos/<int:id_producto>/disponibilidad/', verificar_disponibilidad_producto, name='verificar_disponibilidad_producto'),

    # Rutas para promociones
    path('promociones/', listar_promociones, name='listar_promociones'),
    path('promociones/crear/', crear_promocion, name='crear_promocion'),
    path('promociones/<int:id>/', obtener_promocion, name='obtener_promocion'),
    path('promociones/<int:id>/modificar/', modificar_promocion, name='modificar_promocion'),
    path('promociones/<int:id>/eliminar/', eliminar_promocion, name='eliminar_promocion'),

    # Rutas para inventario
    path('inventario/sede/<int:id_sede>/', listar_inventario_por_sede, name='listar_inventario_por_sede'),
    path('inventario/insumo/<int:id_insumo>/', listar_inventario_por_insumo, name='listar_inventario_por_insumo'),
    path('inventario/stock-bajo/', listar_stock_bajo, name='listar_stock_bajo'),
    path('inventario/entrada/', registrar_entrada_stock, name='registrar_entrada_stock'),
    path('inventario/salida/', registrar_salida_stock, name='registrar_salida_stock'),
    path('inventario/transferir/', transferir_entre_sedes, name='transferir_entre_sedes'),
    path('inventario/movimientos/', obtener_historial_movimientos, name='obtener_historial_movimientos'),
    path('inventario/alertas/', obtener_alertas_reposicion, name='obtener_alertas_reposicion'),
    path('inventario/insumo/<int:id_insumo>/verificar/', verificar_stock_disponible, name='verificar_stock_disponible'),

    # Rutas para insumos
    path('insumos/', listar_insumos, name='listar_insumos'),
    path('insumos/crear/', crear_insumo, name='crear_insumo'),
    path('insumos/<int:id_insumo>/', obtener_insumo, name='obtener_insumo'),
    path('insumos/<int:id_insumo>/modificar/', modificar_insumo, name='modificar_insumo'),
    path('insumos/<int:id_insumo>/eliminar/', desactivar_insumo, name='desactivar_insumo'),

    # Rutas para compras
    path('compras/', listar_compras, name='listar_compras'),
    path('compras/crear/', crear_compra, name='crear_compra'),
    path('compras/<int:id_compra>/', obtener_compra, name='obtener_compra'),
    path('compras/<int:id_compra>/estado/', cambiar_estado_compra, name='cambiar_estado_compra'),
    path('compras/<int:id_compra>/detalle/', agregar_detalle_compra, name='agregar_detalle_compra'),
    path('compras/proveedor/<int:id_proveedor>/', listar_compras_por_proveedor, name='listar_compras_por_proveedor'),
    path('compras/insumo/<int:id_insumo>/historial/', obtener_historial_insumo, name='obtener_historial_insumo'),
    path('compras/estado/', listar_compras_por_estado, name='listar_compras_por_estado'),

    # Rutas para autenticación (API): wrappers to redirect browser to HTML views
    path("auth/login/", api_auth_login_entry, name="api_login"),
    path("auth/registrar-cliente/", api_auth_register_entry, name="api_registrar_cliente"),
    path("auth/registrar-empleado/", registrar_empleado_view, name="registrar_empleado"),
    path("auth/registrar-administrador/", registrar_administrador_view, name="registrar_administrador"),
    path("auth/usuario/", usuario_actual_view, name="usuario_actual"),
    path("auth/logout/", api_auth_logout_entry, name="api_cerrar_sesion"),

    # Rutas para empleados (gestión de personal)
    path('empleados/', listar_empleados, name='listar_empleados'),
    path('empleados/sede/<int:id_sede>/', listar_empleados_por_sede, name='listar_empleados_por_sede'),
    path('empleados/<int:id_empleado>/', obtener_empleado, name='obtener_empleado'),
    path('empleados/<int:id_empleado>/modificar/', modificar_empleado, name='modificar_empleado'),
    path('empleados/<int:id_empleado>/transferir/', transferir_sede, name='transferir_sede'),
    path('empleados/<int:id_empleado>/desactivar/', desactivar_empleado, name='desactivar_empleado'),
    path('empleados/<int:id_empleado>/activar/', activar_empleado, name='activar_empleado'),

    # Rutas para turnos (asignación de roles y turnos)
    path('turnos/', listar_turnos, name='listar_turnos'),
    path('turnos/crear/', crear_turno, name='crear_turno'),
    path('turnos/<int:id_turno>/', obtener_turno, name='obtener_turno'),
    path('turnos/<int:id_turno>/modificar/', modificar_turno, name='modificar_turno'),
    path('turnos/<int:id_turno>/eliminar/', eliminar_turno, name='eliminar_turno'),
    path('turnos/empleado/<int:id_empleado>/', listar_turnos_empleado, name='listar_turnos_empleado'),
    path('turnos/fecha/<str:fecha>/', listar_turnos_fecha, name='listar_turnos_fecha'),
    path('turnos/sede/<int:id_sede>/fecha/<str:fecha>/', listar_turnos_sede_fecha, name='listar_turnos_sede_fecha'),

    # Rutas para notificaciones (sistema de notificaciones)
    path('notificaciones/', listar_todas_notificaciones, name='listar_todas_notificaciones'),
    path('notificaciones/crear/', crear_notificacion, name='crear_notificacion'),
    path('notificaciones/masiva/', enviar_notificacion_masiva, name='enviar_notificacion_masiva'),
    path('notificaciones/mis-notificaciones/', listar_notificaciones_cliente, name='listar_notificaciones_cliente'),
    path('notificaciones/no-leidas/count/', contar_no_leidas, name='contar_no_leidas'),
    path('notificaciones/<int:id_notificacion>/', obtener_notificacion, name='obtener_notificacion'),
    path('notificaciones/<int:id_notificacion>/leer/', marcar_como_leida, name='marcar_como_leida'),
    path('notificaciones/leer-todas/', marcar_todas_leidas, name='marcar_todas_leidas'),
    path('notificaciones/<int:id_notificacion>/eliminar/', eliminar_notificacion, name='eliminar_notificacion'),

    # Rutas para asistencia (control de horarios y asistencia)
    path('asistencia/entrada/', registrar_entrada, name='registrar_entrada'),
    path('asistencia/salida/', registrar_salida, name='registrar_salida'),
    path('asistencia/mis-registros/', mis_registros, name='mis_registros'),
    path('asistencia/', listar_asistencias, name='listar_asistencias'),
    path('asistencia/fecha/<str:fecha>/', asistencias_por_fecha, name='asistencias_por_fecha'),
    path('asistencia/empleado/<int:id_empleado>/', asistencias_por_empleado, name='asistencias_por_empleado'),
    path('asistencia/estado/<str:estado>/', asistencias_por_estado, name='asistencias_por_estado'),
    path('asistencia/reporte-mensual/', reporte_mensual, name='reporte_mensual'),
    path('asistencia/<int:id_asistencia>/', obtener_asistencia, name='obtener_asistencia'),
    path('asistencia/<int:id_asistencia>/modificar/', modificar_asistencia, name='modificar_asistencia'),
    path('asistencia/<int:id_asistencia>/estado/', actualizar_estado, name='actualizar_estado_asistencia'),
    path('asistencia/<int:id_asistencia>/eliminar/', eliminar_asistencia, name='eliminar_asistencia'),

    # API básica adicional
    path('cliente/pedidos/', api_pedidos_cliente, name='api_pedidos_cliente'),
    path('pedidos/crear-token/', api_pedido_crear_token, name='api_pedido_crear_token'),
    path('pedidos/<int:id_pedido>/detalle/', api_pedido_detalle, name='api_pedido_detalle'),
]
