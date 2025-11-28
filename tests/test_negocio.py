from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class NegocioInvalidoTests(TestCase):
    def setUp(self):
        self.client = Client()

    def login_role(self, username, password, role):
        User.objects.create_user(username=username, password=password)
        assert self.client.login(username=username, password=password)
        session = self.client.session
        session['user_rol'] = role
        if role == 'cliente':
            session['id_cliente'] = 55  # id_cliente ficticio
        session.save()

    def test_reclamo_crear_sin_id_pedido(self):
        self.login_role('cliente_inv@test.com', 'pass', 'cliente')
        # Forzar helper para evitar llamadas externas
        from views import views as v
        v.get_usuario_cliente = lambda request: {'usuario_row': None, 'id_usuario': None, 'cliente_row': None, 'id_cliente': 55}
        resp = self.client.post(reverse('reclamo_crear'), data={'descripcion': 'Algo pasó'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id_pedido')  # mensaje error campo

    def test_pedido_crear_sin_items(self):
        self.login_role('cliente_pedido@test.com', 'pass', 'cliente')
        from views import views as v
        v.get_usuario_cliente = lambda request: {'usuario_row': None, 'id_usuario': None, 'cliente_row': None, 'id_cliente': 55}
        resp = self.client.post(reverse('pedido_crear'), data={'id_sede': '1'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Debe seleccionar al menos un producto')

    def test_compra_registrar_sin_proveedor(self):
        self.login_role('empleado_compra@test.com', 'pass', 'empleado')
        from views import views as v
        # Mock listar para evitar uso real
        v.proveedor_manager.listar = lambda: {'success': True, 'data': []}
        v.insumo_manager.listar = lambda: {'success': True, 'data': []}
        data = {'i1_id': '10', 'i1_qty': '2'}  # items pero sin id_proveedor
        resp = self.client.post(reverse('compra_registrar'), data=data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id_proveedor')

    def test_perfil_editar_sin_cambios(self):
        self.login_role('cliente_perfil@test.com', 'pass', 'cliente')
        from views import views as v
        # Mock obtener_por_id para perfil existente
        v.ClienteDAO.obtener_por_id = lambda self2, cid: type('resp', (), {'data': [{'id_cliente': cid, 'telefono': '123', 'direccion': 'Calle 1'}]})()
        resp_get = self.client.get(reverse('perfil_editar'))
        self.assertEqual(resp_get.status_code, 200)
        # Post mismos valores
        resp_post = self.client.post(reverse('perfil_editar'), data={'telefono': '123', 'direccion': 'Calle 1'})
        self.assertEqual(resp_post.status_code, 200)
        self.assertContains(resp_post, 'No se detectaron cambios')
