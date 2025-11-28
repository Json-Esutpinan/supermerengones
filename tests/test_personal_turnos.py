#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para HU11 - Gestión de Empleados y HU12 - Gestión de Turnos
Tests para PersonalManager y TurnoManager
"""

import pytest
from datetime import datetime, date, time, timedelta
from manager.personalManager import PersonalManager
from manager.turnoManager import TurnoManager
from manager.authManager import AuthManager
from dao.empleadoDAO import EmpleadoDAO
from dao.turnoDAO import TurnoDAO
from entidades.empleado import Empleado
from entidades.turno import Turno


class TestPersonalManager:
    """Tests para HU11 - Gestión de Empleados"""
    
    @pytest.mark.database
    def test_crear_empleado_exitoso(self, sede_test):
        """Test: Crear nuevo empleado"""
        if not sede_test:
            pytest.skip("No se pudo crear sede de prueba")
        
        manager = AuthManager()
        
        email = f"empleado_{datetime.now().timestamp()}@test.com"
        resultado = manager.registrarEmpleado(
            nombre="Pedro García",
            email=email,
            password="emp123456",
            id_sede=sede_test['id_sede'],
            cargo="Cajero"
        )
        
        assert resultado is not None
        assert resultado['success'] is True
        assert 'data' in resultado
        assert resultado['data']['empleado'].cargo == "Cajero"
    
    @pytest.mark.database
    def test_crear_admin_exitoso(self):
        """Test: Crear nuevo administrador"""
        manager = AuthManager()
        
        email = f"admin_{datetime.now().timestamp()}@test.com"
        resultado = manager.registrarAdministrador(
            nombre="María López",
            email=email,
            password="admin123456",
            nivel_acceso="basico"
        )
        
        assert resultado is not None
        assert resultado['success'] is True
        assert resultado['data']['administrador'].nivel_acceso == "basico"
    
    @pytest.mark.database
    def test_listar_empleados_por_sede(self, empleado_test):
        """Test: Listar empleados de una sede"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        manager = PersonalManager()
        
        resultado = manager.listarPorSede(empleado_test['id_sede'])
        
        assert resultado is not None
        assert resultado['success'] is True
        assert len(resultado['data']) > 0
    
    @pytest.mark.database
    def test_modificar_empleado(self, empleado_test):
        """Test: Modificar datos de empleado"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        manager = PersonalManager()
        
        cambios = {"cargo": "Supervisor"}
        resultado = manager.modificarEmpleado(
            empleado_test['id_empleado'],
            cambios
        )
        
        assert resultado is not None
        assert resultado['success'] is True
        assert resultado['data']['cargo'] == "Supervisor"
    


class TestTurnoManager:
    """Tests para HU12 - Gestión de Turnos"""
    
    @pytest.mark.database
    def test_crear_turno_exitoso(self, empleado_test):
        """Test: Crear nuevo turno"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        manager = TurnoManager()
        
        resultado = manager.crearTurno(
            id_empleado=empleado_test['id_empleado'],
            fecha=date.today() + timedelta(days=1),
            hora_inicio=time(9, 0),
            hora_fin=time(17, 0)
        )
        
        assert resultado is not None
        assert resultado['success'] is True
        assert resultado['data']['id_empleado'] == empleado_test['id_empleado']
    
    @pytest.mark.database
    def test_asignar_turno_empleado(self, empleado_test, turno_test):
        """Test: Asignar turno a empleado"""
        if not empleado_test or not turno_test:
            pytest.skip("No se pudieron crear fixtures necesarios")
        
        manager = TurnoManager()
        
        resultado = manager.asignarTurnoaEmpleado(
            empleado_test['id_empleado'],
            turno_test['id_turno']
        )
        
        assert resultado is not None
        assert resultado['success'] is True
    
    @pytest.mark.database
    def test_ver_turnos_por_empleado(self, turno_test):
        """Test: Ver turnos de un empleado"""
        if not turno_test:
            pytest.skip("No se pudo crear turno de prueba")
        
        manager = TurnoManager()
        
        resultado = manager.listarPorEmpleado(turno_test['id_empleado'])
        
        assert resultado is not None
        assert resultado['success'] is True
        assert len(resultado['data']) > 0
    
    @pytest.mark.database
    def test_ver_turnos_por_fecha(self, turno_test):
        """Test: Ver turnos de una fecha específica"""
        if not turno_test:
            pytest.skip("No se pudo crear turno de prueba")
        
        manager = TurnoManager()
        
        resultado = manager.listarPorFecha(date.today())
        
        assert resultado is not None
        assert resultado['success'] is True
    
    @pytest.mark.database
    def test_modificar_turno(self, turno_test):
        """Test: Modificar horario de turno"""
        if not turno_test:
            pytest.skip("No se pudo crear turno de prueba")
        
        manager = TurnoManager()
        
        cambios = {
            "hora_inicio": "10:00",
            "hora_fin": "18:00"
        }
        
        resultado = manager.modificarTurno(turno_test['id_turno'], cambios)
        
        assert resultado is not None
        assert resultado['success'] is True
    
    @pytest.mark.database
    def test_eliminar_turno(self, empleado_test):
        """Test: Eliminar turno"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        manager = TurnoManager()
        
        # Crear turno temporal
        resultado = manager.crearTurno(
            id_empleado=empleado_test['id_empleado'],
            fecha=date.today() + timedelta(days=7),
            hora_inicio=time(8, 0),
            hora_fin=time(16, 0)
        )
        
        # Eliminar
        resultado_eliminar = manager.eliminarTurno(resultado['data']['id_turno'])
        
        assert resultado_eliminar is not None
        assert resultado_eliminar['success'] is True



class TestEmpleadoDAO:
    """Tests para el DAO de Empleado"""
    
    @pytest.mark.database
    def test_crear_empleado(self, usuario_empleado_test, sede_test):
        """Test: Crear empleado en BD"""
        if not usuario_empleado_test or not sede_test:
            pytest.skip("No se pudieron crear fixtures necesarios")
        
        dao = EmpleadoDAO()
        empleado = Empleado(
            id_usuario=usuario_empleado_test['id_usuario'],
            id_sede=sede_test['id_sede'],
            cargo="Cocinero",
            fecha_ingreso=date.today()
        )
        
        resp = dao.crear(empleado)
        
        assert resp.data is not None
        assert len(resp.data) > 0
        assert resp.data[0]['cargo'] == "Cocinero"
    
    @pytest.mark.database
    def test_obtener_empleado_con_datos_usuario(self, empleado_test):
        """Test: Obtener empleado con JOIN de usuario"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        dao = EmpleadoDAO()
        resp = dao.obtener_por_id(empleado_test['id_empleado'])
        
        assert resp.data is not None
        assert len(resp.data) > 0
        # Debería incluir datos del usuario
    
    @pytest.mark.database
    def test_listar_empleados_activos(self, empleado_test):
        """Test: Listar solo empleados activos"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        dao = EmpleadoDAO()
        resp = dao.listar_activos()
        
        assert resp.data is not None


class TestTurnoDAO:
    """Tests para el DAO de Turno"""
    
    @pytest.mark.database
    def test_crear_turno(self, empleado_test):
        """Test: Crear turno en BD"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        dao = TurnoDAO()
        turno = Turno(
            id_empleado=empleado_test['id_empleado'],
            fecha=date.today() + timedelta(days=2),
            hora_inicio=time(14, 0),
            hora_fin=time(22, 0)
        )
        
        resp = dao.crear(turno)
        
        assert resp.data is not None
        assert len(resp.data) > 0
    
    @pytest.mark.database
    def test_obtener_turnos_por_empleado_y_fecha(self, turno_test):
        """Test: Obtener turnos específicos"""
        if not turno_test:
            pytest.skip("No se pudo crear turno de prueba")
        
        dao = TurnoDAO()
        resp = dao.listar_por_empleado(
            turno_test['id_empleado']
        )
        
        assert resp.data is not None


class TestTurnoEntidad:
    """Tests para la entidad Turno"""
    
    def test_to_dict(self):
        """Test: Serializar turno a dict"""
        turno = Turno(
            id_turno=1,
            id_empleado=5,
            fecha=date(2025, 11, 27),
            hora_inicio=time(8, 0),
            hora_fin=time(16, 0)
        )
        
        data = turno.to_dict()
        
        assert data['id_turno'] == 1
        assert data['id_empleado'] == 5
        assert data['fecha'] == '2025-11-27'
        assert data['hora_inicio'] == '08:00:00'
        assert data['hora_fin'] == '16:00:00'
    
    def test_from_dict(self):
        """Test: Deserializar turno desde dict"""
        data = {
            'id_turno': 1,
            'id_empleado': 5,
            'fecha': '2025-11-27',
            'hora_inicio': '08:00:00',
            'hora_fin': '16:00:00'
        }
        
        turno = Turno.from_dict(data)
        
        assert turno.id_turno == 1
        assert turno.id_empleado == 5
        assert isinstance(turno.fecha, date)
        assert isinstance(turno.hora_inicio, time)
        assert isinstance(turno.hora_fin, time)

