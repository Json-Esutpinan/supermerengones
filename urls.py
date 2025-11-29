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
    path('carrito/crear-pedido/', views.carrito_crear_pedido, name='carrito_crear_pedido'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.perfil_editar, name='perfil_editar'),
    # Seguridad
    path('cuenta/password-change/', views.password_change, name='password_change'),
    path('cuenta/password-reset/', views.password_reset_request, name='password_reset_request'),
    path('cuenta/sesiones/', views.sessions_list, name='sessions_list'),
    # Reclamos front
    path('reclamos/mis/', views.reclamos_mis, name='reclamos_mis'),
    path('reclamos/crear/', views.reclamo_crear, name='reclamo_crear'),
    path('reclamos/', views.reclamos_todos, name='reclamos_todos'),
    path('reclamos/<int:id_reclamo>/resolver/', views.reclamo_resolver_ui, name='reclamo_resolver_ui'),
    path('reclamos/<int:id_reclamo>/rechazar/', views.reclamo_rechazar_ui, name='reclamo_rechazar_ui'),
    # Pedidos front
    path('pedidos/mis/', views.pedidos_mis, name='pedidos_mis'),
    path('pedidos/crear/', views.pedido_crear, name='pedido_crear'),
    path('pedidos/', views.pedidos_todos, name='pedidos_todos'),
    path('pedidos/<int:id_pedido>/', views.pedido_detalle, name='pedido_detalle'),
    path('pedidos/<int:id_pedido>/cancelar-cliente/', views.pedido_cancelar_cliente, name='pedido_cancelar_cliente'),
    path('pedidos/<int:id_pedido>/<str:accion>/', views.pedido_accion_estado, name='pedido_accion_estado'),
    # Panel admin
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/kpis/', views.admin_kpis, name='admin_kpis'),
    path('admin-panel/funcionalidades/', views.admin_funcionalidades, name='admin_funcionalidades'),
        path('admin/export/pedidos.csv', views.export_pedidos_csv, name='export_pedidos_csv'),
        path('admin/export/productos.csv', views.export_productos_csv, name='export_productos_csv'),
    path('admin/kpis/top-productos/', views.admin_top_productos, name='admin_top_productos'),
    # Auditoría
    path('app-admin/auditoria/', views.auditoria_logs, name='auditoria_logs'),
    # Notificaciones
    path('notificaciones/', views.notificaciones_cliente, name='notificaciones_cliente'),
    path('notificaciones/marcar/<int:id_notificacion>/', views.notificacion_marcar_leida, name='notificacion_marcar_leida'),
    path('notificaciones/marcar-todas/', views.notificaciones_marcar_todas, name='notificaciones_marcar_todas'),
    # Prefijo 'app-admin/' para no colisionar con Django admin site
    path('app-admin/notificaciones/', views.notificaciones_admin, name='notificaciones_admin'),
    path('app-admin/notificaciones/nueva/', views.notificacion_admin_crear, name='notificacion_admin_crear'),
    # Verificaciones y estadísticas
    path('verificar/producto/', views.producto_disponibilidad, name='producto_disponibilidad'),
    path('verificar/inventario/', views.inventario_verificar, name='inventario_verificar'),
    path('proveedores/estadisticas/', views.proveedor_estadisticas, name='proveedor_estadisticas'),
    # Receta producto
    path('productos/<int:id_producto>/receta/', views.producto_receta_editar, name='producto_receta_editar'),
    # Productos CRUD admin
    path('app-admin/productos/', views.productos_admin_list, name='productos_admin_list'),
    path('app-admin/productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('app-admin/productos/<int:id_producto>/editar/', views.producto_editar, name='producto_editar'),
    path('app-admin/productos/<int:id_producto>/toggle/', views.producto_toggle_estado, name='producto_toggle_estado'),
    # Insumos CRUD admin
    path('app-admin/insumos/', views.insumos_admin_list, name='insumos_admin_list'),
    path('app-admin/insumos/nuevo/', views.insumo_crear, name='insumo_crear'),
    path('app-admin/insumos/<int:id_insumo>/editar/', views.insumo_editar, name='insumo_editar'),
    path('app-admin/insumos/<int:id_insumo>/toggle/', views.insumo_toggle_estado, name='insumo_toggle_estado'),
    # Sedes CRUD admin
    path('app-admin/sedes/', views.sedes_admin_list, name='sedes_admin_list'),
    path('app-admin/sedes/nuevo/', views.sede_crear, name='sede_crear'),
    path('app-admin/sedes/<int:id_sede>/editar/', views.sede_editar, name='sede_editar'),
    path('app-admin/sedes/<int:id_sede>/toggle/', views.sede_toggle_estado, name='sede_toggle_estado'),
    # Promociones CRUD admin
    path('app-admin/promociones/', views.promociones_admin_list, name='promociones_admin_list'),
    path('app-admin/promociones/nueva/', views.promocion_crear, name='promocion_crear'),
    path('app-admin/promociones/<int:id_promocion>/editar/', views.promocion_editar, name='promocion_editar'),
    path('app-admin/promociones/<int:id_promocion>/toggle/', views.promocion_toggle_estado, name='promocion_toggle_estado'),
    # Turnos CRUD admin
    path('app-admin/turnos/', views.turnos_admin_list, name='turnos_admin_list'),
    path('app-admin/turnos/nuevo/', views.turno_crear, name='turno_crear'),
    path('app-admin/turnos/<int:id_turno>/editar/', views.turno_editar, name='turno_editar'),
    path('app-admin/turnos/<int:id_turno>/eliminar/', views.turno_eliminar, name='turno_eliminar'),
    # Turnos empleado
    path('turnos/mis/', views.turnos_mis, name='turnos_mis'),
    # Asistencia empleado / admin
    path('asistencia/mia/', views.asistencia_mi, name='asistencia_mi'),
    path('asistencia/entrada/', views.asistencia_registrar_entrada, name='asistencia_registrar_entrada'),
    path('asistencia/salida/', views.asistencia_registrar_salida, name='asistencia_registrar_salida'),
    path('asistencia/hoy/', views.asistencia_admin_hoy, name='asistencia_admin_hoy'),
    path('asistencia/<int:id_asistencia>/estado/', views.asistencia_actualizar_estado, name='asistencia_actualizar_estado'),
    # Proveedores CRUD
    path('proveedores/', views.proveedores_listar, name='proveedores_listar'),
    path('proveedores/nuevo/', views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/<int:id_proveedor>/editar/', views.proveedor_editar, name='proveedor_editar'),
    # Compras
    path('compras/', views.compras_listar, name='compras_listar'),
    path('compras/nueva/', views.compra_registrar, name='compra_registrar'),
    # Inventario movimientos
    path('inventario/movimientos/', views.inventario_movimientos, name='inventario_movimientos'),
    path('app-admin/stock-bajo/', views.stock_bajo_admin, name='stock_bajo_admin'),
    # Registro multi-rol (admin) - evitar colisión con admin.site.urls
    path('admin-panel/registrar-empleado/', views.registrar_empleado_ui, name='registrar_empleado_ui'),
    path('admin-panel/registrar-administrador/', views.registrar_administrador_ui, name='registrar_administrador_ui'),

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