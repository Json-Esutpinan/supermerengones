from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from utils.validation import validate_producto, validate_insumo


class Phase1NewFeaturesTests(TestCase):
    def setUp(self):
        self.client = Client()

    def login_with_role(self, username, password, role, id_cliente=None):
        # Crear usuario y forzar login para evitar posibles fallos de autenticación
        # (force_login evita dependencias de backends personalizados o hashes).
        user = User.objects.create_user(username=username, password=password)
        self.client.force_login(user)
        session = self.client.session
        session['user_rol'] = role
        if id_cliente is not None:
            session['id_cliente'] = id_cliente
        session.save()

    # -------------------- Notificaciones --------------------
    def test_cliente_access_notificaciones_list(self):
        self.login_with_role('clienteNotif@test.com', 'pass', 'cliente', id_cliente=11)
        from views import views as v
        class FakeDAO:
            def listar_por_cliente(self, idc, solo_no_leidas=False, limite=100):
                return type('resp', (), {'data': [
                    {'id_notificacion': 1, 'titulo': 'Hola', 'mensaje': 'Mensaje', 'leida': False, 'fecha': '2025-11-28'}
                ]})()
        v.NotificacionDAO = FakeDAO
        resp = self.client.get(reverse('notificaciones_cliente'))
        # Debug print if needed
        if 'Mis Notificaciones' not in resp.content.decode(errors='ignore'):
            print('DEBUG notificaciones_cliente content snippet:', resp.content[:300])
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Mis Notificaciones')
        self.assertContains(resp, 'Hola')

    def test_cliente_mark_all_notificaciones(self):
        self.login_with_role('clienteNotif2@test.com', 'pass', 'cliente', id_cliente=12)
        from views import views as v
        class FakeDAO:
            def listar_por_cliente(self, *a, **k):
                return type('resp', (), {'data': []})()
            def marcar_todas_leidas(self, idc):
                return type('resp', (), {'data': []})()
        v.NotificacionDAO = FakeDAO
        resp = self.client.get(reverse('notificaciones_marcar_todas'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.endswith(reverse('notificaciones_cliente')))

    def test_admin_access_notificaciones_admin(self):
        self.login_with_role('adminNotif@test.com', 'pass', 'administrador')
        from views import views as v
        class FakeDAO:
            def listar_todas(self, limite=200):
                return type('resp', (), {'data': [
                    {'id_notificacion': 5, 'titulo': 'Info', 'mensaje': 'Sistema', 'leida': True, 'fecha': '2025-11-28', 'cliente': {'id_cliente': 99, 'usuario': {'email': 'c@test.com'}}}
                ]})()
        v.NotificacionDAO = FakeDAO
        resp = self.client.get(reverse('notificaciones_admin'))
        if 'Notificaciones (Admin)' not in resp.content.decode(errors='ignore'):
            print('DEBUG notificaciones_admin content snippet:', resp.content[:300])
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Notificaciones (Admin)')
        self.assertContains(resp, 'Info')

    def test_cliente_forbidden_notificaciones_admin(self):
        self.login_with_role('clienteNotif3@test.com', 'pass', 'cliente', id_cliente=13)
        resp = self.client.get(reverse('notificaciones_admin'))
        self.assertEqual(resp.status_code, 403)

    # -------------------- Cancelación Pedido Cliente --------------------
    def test_cliente_cancel_pedido_pendiente(self):
        self.login_with_role('clienteCancel@test.com', 'pass', 'cliente', id_cliente=21)
        from views import views as v
        # Mock detalle pendiente
        v.pedido_manager.obtenerDetallePedido = lambda idp: {
            'success': True,
            'data': type('Obj', (), {'to_dict': lambda self: {
                'id_pedido': idp, 'id_cliente': 21, 'estado': 'pendiente'
            }})()
        }
        estado_capturado = {}
        def fake_actualizar(idp, nuevo_estado):
            estado_capturado['estado'] = nuevo_estado
            return {'success': True, 'data': type('Obj', (), {'to_dict': lambda self: {'id_pedido': idp, 'estado': nuevo_estado}})()}
        v.pedido_manager.actualizarEstado = fake_actualizar
        resp = self.client.post(reverse('pedido_cancelar_cliente', kwargs={'id_pedido': 700}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(estado_capturado.get('estado'), 'cancelado')

    def test_cliente_cancel_pedido_no_pendiente(self):
        self.login_with_role('clienteCancel2@test.com', 'pass', 'cliente', id_cliente=22)
        from views import views as v
        v.pedido_manager.obtenerDetallePedido = lambda idp: {
            'success': True,
            'data': type('Obj', (), {'to_dict': lambda self: {
                'id_pedido': idp, 'id_cliente': 22, 'estado': 'en_proceso'
            }})()
        }
        # actualizarEstado no debería llamarse
        v.pedido_manager.actualizarEstado = lambda *a, **k: {'success': False, 'message': 'Should not call'}
        resp = self.client.post(reverse('pedido_cancelar_cliente', kwargs={'id_pedido': 701}))
        self.assertEqual(resp.status_code, 302)
        # No cambia a cancelado - verificar mensaje en response (follow)
        resp_follow = self.client.get(resp.url)
        self.assertContains(resp_follow, 'Solo se pueden cancelar pedidos pendientes')

    def test_cliente_cancel_pedido_forbidden_other_user(self):
        self.login_with_role('clienteCancel3@test.com', 'pass', 'cliente', id_cliente=23)
        from views import views as v
        v.pedido_manager.obtenerDetallePedido = lambda idp: {
            'success': True,
            'data': type('Obj', (), {'to_dict': lambda self: {
                'id_pedido': idp, 'id_cliente': 999, 'estado': 'pendiente'
            }})()
        }
        resp = self.client.post(reverse('pedido_cancelar_cliente', kwargs={'id_pedido': 702}))
        self.assertEqual(resp.status_code, 403)

    # -------------------- Productos / Insumos CRUD Access --------------------
    def test_admin_access_productos_admin_list(self):
        self.login_with_role('adminProd@test.com', 'pass', 'administrador')
        from views import views as v
        v.producto_dao.listar_todos = lambda limite=500: []
        resp = self.client.get(reverse('productos_admin_list'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_access_productos_admin_list(self):
        self.login_with_role('empleadoProd@test.com', 'pass', 'empleado')
        from views import views as v
        v.producto_dao.listar_todos = lambda limite=500: []
        resp = self.client.get(reverse('productos_admin_list'))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_forbidden_productos_admin_list(self):
        self.login_with_role('clienteProd@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('productos_admin_list'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_insumos_admin_list(self):
        self.login_with_role('adminIns@test.com', 'pass', 'administrador')
        from views import views as v
        resp = self.client.get(reverse('insumos_admin_list'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_access_insumos_admin_list(self):
        self.login_with_role('empleadoIns@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('insumos_admin_list'))
        self.assertEqual(resp.status_code, 200)

    def test_cliente_forbidden_insumos_admin_list(self):
        self.login_with_role('clienteIns@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('insumos_admin_list'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_producto_crear(self):
        self.login_with_role('adminProd2@test.com', 'pass', 'administrador')
        resp = self.client.get(reverse('producto_crear'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_forbidden_producto_crear(self):
        self.login_with_role('empleadoProd2@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('producto_crear'))
        self.assertEqual(resp.status_code, 403)

    def test_cliente_forbidden_producto_crear(self):
        self.login_with_role('clienteProd2@test.com', 'pass', 'cliente')
        resp = self.client.get(reverse('producto_crear'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_access_insumo_crear(self):
        self.login_with_role('adminIns2@test.com', 'pass', 'administrador')
        resp = self.client.get(reverse('insumo_crear'))
        self.assertEqual(resp.status_code, 200)

    def test_empleado_forbidden_insumo_crear(self):
        self.login_with_role('empleadoIns2@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('insumo_crear'))
        self.assertEqual(resp.status_code, 403)

    # -------------------- Validation Functions --------------------
    def test_validate_producto_errors(self):
        errores = validate_producto(codigo='', nombre='', precio='-5', existing_codigos={'X1'})
        self.assertIn('codigo', errores)
        self.assertIn('nombre', errores)
        self.assertIn('precio', errores)
        # Duplicate code
        errores_dup = validate_producto(codigo='X1', nombre='Nombre', precio='10', existing_codigos={'X1'})
        self.assertIn('codigo', errores_dup)

    def test_validate_producto_success(self):
        errores = validate_producto(codigo='ABC123', nombre='Prod', precio='10.5', existing_codigos={'XYZ'})
        self.assertEqual(errores, {})

    def test_validate_insumo_errors(self):
        errores = validate_insumo(codigo='', nombre='', id_sede='0', stock_minimo='-2', existing_codigos={'I1'})
        self.assertIn('codigo', errores)
        self.assertIn('nombre', errores)
        self.assertIn('id_sede', errores)
        self.assertIn('stock_minimo', errores)
        errores_dup = validate_insumo(codigo='I1', nombre='Insumo', id_sede='1', existing_codigos={'I1'})
        self.assertIn('codigo', errores_dup)

    def test_validate_insumo_success(self):
        errores = validate_insumo(codigo='INS_01', nombre='Azucar', id_sede='5', stock_minimo='10', existing_codigos={'OTRO'})
        self.assertEqual(errores, {})
