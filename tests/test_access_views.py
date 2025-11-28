from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User


class AccessViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def login_with_role(self, username, password, role):
        User.objects.create_user(username=username, password=password)
        assert self.client.login(username=username, password=password)
        session = self.client.session
        session['user_rol'] = role
        session.save()

    def test_admin_access_reclamos_todos(self):
        self.login_with_role('admin@test.com', 'pass', 'administrador')
        # Mock manager
        from views import views as v
        v.reclamo_manager.listarTodosReclamos = lambda limite=200: {'success': True, 'data': [], 'message': 'ok'}
        resp = self.client.get(reverse('reclamos_todos'))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_forbidden_reclamos_todos(self):
        self.login_with_role('cliente@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('reclamos_todos'))
        self.assertEqual(resp.status_code, 403)

    def test_empleado_access_pedidos_todos(self):
        self.login_with_role('empleado@test.com', 'pass', 'empleado')
        from views import views as v
        v.pedido_manager.listarTodosPedidos = lambda limite=200: {'success': True, 'data': [], 'message': 'ok'}
        resp = self.client.get(reverse('pedidos_todos'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_can_post_order_action(self):
        self.login_with_role('empleadoX@test.com', 'pass', 'empleado')
        # Mock detalle y acción
        from views import views as v
        v.pedido_manager.obtenerDetallePedido = lambda id_p: {'success': True, 'data': type('obj', (), {'to_dict': lambda self: {'id_pedido': id_p}})()}
        v.pedido_manager.aceptarPedido = lambda id_p: {'success': True, 'message': 'ok'}
        # First ensure detail renders
        resp = self.client.get(reverse('pedido_detalle', kwargs={'id_pedido': 123}))
        self.assertEqual(resp.status_code, 200)
        # Post action
        resp = self.client.post(reverse('pedido_accion_estado', kwargs={'id_pedido': 123, 'accion': 'aceptar'}))
        self.assertEqual(resp.status_code, 302)

    def test_cliente_forbidden_order_action(self):
        self.login_with_role('clienteX@test.com', 'pass', 'cliente')
        resp = self.client.post(reverse('pedido_accion_estado', kwargs={'id_pedido': 123, 'accion': 'aceptar'}))
        self.assertEqual(resp.status_code, 403)

    def test_cliente_forbidden_pedidos_todos(self):
        self.login_with_role('otrocliente@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('pedidos_todos'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_registrar_empleado(self):
        self.login_with_role('admin2@test.com', 'pass', 'administrador')
        resp = self.client.get(reverse('registrar_empleado_ui'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_forbidden_registrar_empleado(self):
        self.login_with_role('empleado2@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('registrar_empleado_ui'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_producto_disponibilidad(self):
        self.login_with_role('admin3@test.com', 'pass', 'administrador')
        from views import views as v
        v.producto_manager.verificar_disponibilidad = lambda id_prod, cant: {'success': True, 'message': 'ok', 'data': {'disponible': True}}
        resp = self.client.get(reverse('producto_disponibilidad'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_access_producto_disponibilidad(self):
        self.login_with_role('empleado3@test.com', 'pass', 'empleado')
        from views import views as v
        v.producto_manager.verificar_disponibilidad = lambda id_prod, cant: {'success': True, 'message': 'ok', 'data': {'disponible': True}}
        resp = self.client.get(reverse('producto_disponibilidad'))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_forbidden_producto_disponibilidad(self):
        self.login_with_role('cliente3@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('producto_disponibilidad'))
        self.assertEqual(resp.status_code, 403)

    def test_cliente_access_pedido_crear(self):
        self.login_with_role('cliente7@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('pedido_crear'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_access_inventario_verificar(self):
        self.login_with_role('admin4@test.com', 'pass', 'administrador')
        from views import views as v
        v.inventario_manager.verificar_stock_disponible = lambda id_ins, id_sede, cant: {'success': True, 'message': 'ok', 'data': {'suficiente': True}}
        resp = self.client.get(reverse('inventario_verificar'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_access_inventario_verificar(self):
        self.login_with_role('empleado4@test.com', 'pass', 'empleado')
        from views import views as v
        v.inventario_manager.verificar_stock_disponible = lambda id_ins, id_sede, cant: {'success': True, 'message': 'ok', 'data': {'suficiente': True}}
        resp = self.client.get(reverse('inventario_verificar'))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_forbidden_inventario_verificar(self):
        self.login_with_role('cliente4@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('inventario_verificar'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_proveedor_estadisticas(self):
        self.login_with_role('admin5@test.com', 'pass', 'administrador')
        from views import views as v
        v.proveedor_manager.obtener_estadisticas = lambda id_prov: {'success': True, 'message': 'ok', 'data': {'compras': 0}}
        resp = self.client.get(reverse('proveedor_estadisticas'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_forbidden_proveedor_estadisticas(self):
        self.login_with_role('empleado5@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('proveedor_estadisticas'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_admin_panel(self):
        self.login_with_role('admin6@test.com', 'pass', 'administrador')
        resp = self.client.get(reverse('admin_panel'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_forbidden_admin_panel(self):
        self.login_with_role('empleado6@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('admin_panel'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_admin_funcionalidades(self):
        self.login_with_role('adminFunc@test.com', 'pass', 'administrador')
        resp = self.client.get(reverse('admin_funcionalidades'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Panel de Funcionalidades')
        self.assertContains(resp, 'Reclamos')

    def test_cliente_forbidden_admin_funcionalidades(self):
        self.login_with_role('clienteFunc@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('admin_funcionalidades'))
        self.assertEqual(resp.status_code, 403)

    def test_empleado_forbidden_admin_funcionalidades(self):
        self.login_with_role('empleadoFunc@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('admin_funcionalidades'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_admin_kpis(self):
        self.login_with_role('adminKPIs@test.com', 'pass', 'administrador')
        from views import views as v
        # Mock managers to return predictable structures
        v.pedido_manager.listarTodosPedidos = lambda limite=500: {'success': True, 'data': [type('obj', (), {'estado': 'pendiente'})(), type('obj', (), {'estado': 'pendiente'})(), type('obj', (), {'estado': 'completado'})()], 'message': 'ok'}
        v.inventario_manager.verificarAlertasReposicion = lambda s: {'exito': True, 'alertas': [{'id_insumo': 1, 'id_sede': 2, 'cantidad_actual': 3, 'nivel': 'critico'}]}
        v.compra_manager.listarCompras = lambda limite=10: {'success': True, 'data': [{'id_compra': 10, 'id_proveedor': 5, 'total': 123.45, 'estado': 'recibida'}]}
        resp = self.client.get(reverse('admin_kpis'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'pendiente')
        self.assertContains(resp, 'completado')
        self.assertContains(resp, 'Insumos Críticos')

    def test_empleado_forbidden_admin_kpis(self):
        self.login_with_role('empleadoKPIs@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('admin_kpis'))
        self.assertEqual(resp.status_code, 403)

    def test_cliente_forbidden_admin_kpis(self):
        self.login_with_role('clienteKPIs@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('admin_kpis'))
        self.assertEqual(resp.status_code, 403)

    # ---------------- Ownership Pedido Detalle ----------------
    def test_cliente_access_own_pedido_detalle(self):
        self.login_with_role('clienteOwn@test.com', 'pass', 'cliente')
        # Set fake id_cliente in session
        session = self.client.session
        session['id_cliente'] = 77
        session.save()
        from views import views as v
        # Mock detalle con id_cliente = 77
        v.pedido_manager.obtenerDetallePedido = lambda id_p: {
            'success': True,
            'data': type('obj', (), {'to_dict': lambda self: {'id_pedido': id_p, 'id_cliente': 77}})()
        }
        resp = self.client.get(reverse('pedido_detalle', kwargs={'id_pedido': 501}))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_forbidden_other_pedido_detalle(self):
        self.login_with_role('clienteOther@test.com', 'pass', 'cliente')
        session = self.client.session
        session['id_cliente'] = 77
        session.save()
        from views import views as v
        # Mock detalle con distinto id_cliente
        v.pedido_manager.obtenerDetallePedido = lambda id_p: {
            'success': True,
            'data': type('obj', (), {'to_dict': lambda self: {'id_pedido': id_p, 'id_cliente': 999}})()
        }
        resp = self.client.get(reverse('pedido_detalle', kwargs={'id_pedido': 502}))
        self.assertEqual(resp.status_code, 403)

    def test_empleado_access_any_pedido_detalle(self):
        self.login_with_role('empleadoOwn@test.com', 'pass', 'empleado')
        from views import views as v
        v.pedido_manager.obtenerDetallePedido = lambda id_p: {
            'success': True,
            'data': type('obj', (), {'to_dict': lambda self: {'id_pedido': id_p, 'id_cliente': 555}})()
        }
        resp = self.client.get(reverse('pedido_detalle', kwargs={'id_pedido': 503}))
        self.assertEqual(resp.status_code, 200)

    # ---------------- Perfil Usuario ----------------
    def test_cliente_perfil_usuario_with_data(self):
        self.login_with_role('clientePerfil@test.com', 'pass', 'cliente')
        session = self.client.session
        session['id_cliente'] = 88
        session.save()
        from views import views as v
        v.pedido_manager.obtenerHistorialCliente = lambda id_c: {'success': True, 'data': [type('obj', (), {'to_dict': lambda self: {'id_pedido': 1, 'estado': 'pendiente', 'total': 1000}})()]}
        v.reclamo_manager.listarReclamosCliente = lambda id_c: {'success': True, 'data': [type('obj', (), {'to_dict': lambda self: {'id_reclamo': 5, 'descripcion': 'Demora', 'estado': 'abierto'}})()]}
        resp = self.client.get(reverse('perfil_usuario'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Pedidos Recientes')
        self.assertContains(resp, 'Reclamos Recientes')

    def test_empleado_perfil_usuario_no_cliente(self):
        self.login_with_role('empleadoPerfil@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('perfil_usuario'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'No hay datos de cliente')

    # ---------------- Editar Perfil Cliente ----------------
    def test_cliente_access_perfil_editar(self):
        self.login_with_role('clienteEdit@test.com', 'pass', 'cliente')
        session = self.client.session
        session['id_cliente'] = 101
        session.save()
        from views import views as v
        v.ClienteDAO.obtener_por_id = lambda self2, cid: type('resp', (), {'data': [{'id_cliente': cid, 'telefono': '123', 'direccion': 'Calle 1'}]})()
        resp = self.client.get(reverse('perfil_editar'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Editar Perfil')

    def test_empleado_forbidden_perfil_editar(self):
        self.login_with_role('empleadoEdit@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('perfil_editar'))
        self.assertEqual(resp.status_code, 403)

    # ---------------- Receta Producto ----------------
    def test_admin_access_producto_receta_editar(self):
        self.login_with_role('adminReceta@test.com', 'pass', 'administrador')
        resp = self.client.get(reverse('producto_receta_editar', args=[1]))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_forbidden_producto_receta_editar(self):
        self.login_with_role('clienteReceta@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('producto_receta_editar', args=[1]))
        self.assertEqual(resp.status_code, 403)
