from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class TurnosFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()

    def login_with_role(self, username, password, role, id_empleado=None):
        user = User.objects.create_user(username=username, password=password)
        self.client.force_login(user)
        session = self.client.session
        session['user_rol'] = role
        if id_empleado is not None:
            session['id_empleado'] = id_empleado
        session.save()

    def test_admin_access_turnos_admin_list(self):
        self.login_with_role('adminTurnos@test.com', 'pass', 'administrador')
        from views import views as v
        # Stub listarTodos
        v.turno_manager.listarTodos = lambda limite=300: {'success': True, 'data': [
            {'id_turno': 1, 'id_empleado': 99, 'fecha': '2025-11-30', 'hora_inicio': '08:00:00', 'hora_fin': '12:00:00'}
        ]}
        resp = self.client.get(reverse('turnos_admin_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Turnos')

    def test_empleado_forbidden_turnos_admin_list(self):
        self.login_with_role('empleadoX@test.com', 'pass', 'empleado', id_empleado=50)
        resp = self.client.get(reverse('turnos_admin_list'))
        self.assertEqual(resp.status_code, 403)

    def test_empleado_access_turnos_mis(self):
        self.login_with_role('empleadoY@test.com', 'pass', 'empleado', id_empleado=51)
        from views import views as v
        v.turno_manager.listarPorEmpleado = lambda idem, limite=200: {'success': True, 'data': [
            {'id_turno': 10, 'id_empleado': 51, 'fecha': '2025-12-01', 'hora_inicio': '09:00:00', 'hora_fin': '15:00:00'}
        ]}
        resp = self.client.get(reverse('turnos_mis'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Mis Turnos')
        self.assertContains(resp, '09:00')

    def test_empleado_turnos_mis_missing_id(self):
        # Empleado sin id_empleado en session
        self.login_with_role('empleadoNoID@test.com', 'pass', 'empleado')
        resp = self.client.get(reverse('turnos_mis'))
        # Redirect to dashboard
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.endswith(reverse('dashboard')))

    def test_turno_crear_success(self):
        self.login_with_role('adminCreate@test.com', 'pass', 'administrador')
        from views import views as v
        # Patch empleadoDAO & turnoDAO inside manager
        class FakeResp:
            def __init__(self, data):
                self.data = data
        v.turno_manager.empleadoDAO.obtener_por_id = lambda idem: FakeResp([{'id_empleado': idem, 'usuario': {'activo': True}}])
        # crear() returns basic created dict; obtener_por_id returns detailed dict
        v.turno_manager.turnoDAO.crear = lambda turno: FakeResp([{'id_turno': 500}])
        v.turno_manager.turnoDAO.obtener_por_id = lambda idt: FakeResp([{'id_turno': idt, 'id_empleado': 77, 'fecha': '2025-12-05', 'hora_inicio': '08:00:00', 'hora_fin': '12:00:00'}])
        # listarPorEmpleado used in validation (existing list same date) -> empty
        v.turno_manager.listarPorEmpleado = lambda idem, limite=500: {'success': True, 'data': []}
        payload = {
            'id_empleado': '77',
            'fecha': '2025-12-05',
            'hora_inicio': '08:00',
            'hora_fin': '12:00'
        }
        resp = self.client.post(reverse('turno_crear'), payload)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.endswith(reverse('turnos_admin_list')))

    def test_turno_crear_validation_error_time_order(self):
        self.login_with_role('adminCreate2@test.com', 'pass', 'administrador')
        from views import views as v
        class FakeResp:
            def __init__(self, data):
                self.data = data
        v.turno_manager.empleadoDAO.obtener_por_id = lambda idem: FakeResp([{'id_empleado': idem, 'usuario': {'activo': True}}])
        v.turno_manager.listarPorEmpleado = lambda idem, limite=500: {'success': True, 'data': []}
        payload = {
            'id_empleado': '88',
            'fecha': '2025-12-06',
            'hora_inicio': '10:00',
            'hora_fin': '09:00'
        }
        resp = self.client.post(reverse('turno_crear'), payload)
        # Should render same page with error (200)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'hora_fin')

    def test_turno_crear_overlap_error(self):
        self.login_with_role('adminCreate3@test.com', 'pass', 'administrador')
        from views import views as v
        class FakeResp:
            def __init__(self, data):
                self.data = data
        v.turno_manager.empleadoDAO.obtener_por_id = lambda idem: FakeResp([{'id_empleado': idem, 'usuario': {'activo': True}}])
        # Existing turno 09:00-12:00 same date
        existing_list = [{'id_turno': 900, 'id_empleado': 99, 'fecha': '2025-12-07', 'hora_inicio': '09:00:00', 'hora_fin': '12:00:00'}]
        v.turno_manager.listarPorEmpleado = lambda idem, limite=500: {'success': True, 'data': existing_list}
        payload = {
            'id_empleado': '99',
            'fecha': '2025-12-07',
            'hora_inicio': '11:00',
            'hora_fin': '13:00'
        }
        resp = self.client.post(reverse('turno_crear'), payload)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Solapa')
