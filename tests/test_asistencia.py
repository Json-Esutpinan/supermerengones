#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para HU13 - Control de Horarios y Asistencia
"""

import pytest
from datetime import datetime, date
from manager.asistenciaManager import AsistenciaManager
from dao.asistenciaDAO import AsistenciaDAO
from entidades.asistencia import Asistencia


@pytest.mark.database
class TestAsistenciaManager:
    """Tests para AsistenciaManager"""
    
    def test_registrar_entrada_exitoso(self, empleado_test, turno_test):
        """Test: Registrar entrada de empleado exitosamente"""
        manager = AsistenciaManager()
        
        resultado = manager.registrarEntrada(
            empleado_test['id_empleado'],
            turno_test['id_turno']
        )
        
        assert resultado['success'] is True
        assert 'Entrada registrada exitosamente' in resultado['message']
        assert resultado['data'] is not None
        assert resultado['data']['id_empleado'] == empleado_test['id_empleado']
        assert resultado['data']['estado'] == 'pendiente'
        assert resultado['data']['hora_entrada'] is not None
    
    def test_registrar_entrada_duplicada(self, empleado_test, turno_test):
        """Test: No permitir entrada duplicada el mismo día"""
        manager = AsistenciaManager()
        
        # Primera entrada
        resultado1 = manager.registrarEntrada(empleado_test['id_empleado'], turno_test['id_turno'])
        assert resultado1['success'] is True
        
        # Segunda entrada (debe fallar)
        resultado2 = manager.registrarEntrada(empleado_test['id_empleado'], turno_test['id_turno'])
        assert resultado2['success'] is False
        assert 'Ya existe un registro de entrada' in resultado2['message']
    
    def test_registrar_salida_exitoso(self, empleado_test, turno_test):
        """Test: Registrar salida exitosamente"""
        manager = AsistenciaManager()
        
        # Primero registrar entrada
        entrada = manager.registrarEntrada(empleado_test['id_empleado'], turno_test['id_turno'])
        id_asistencia = entrada['data']['id_asistencia']
        
        # Registrar salida
        resultado = manager.registrarSalida(id_asistencia)
        
        assert resultado['success'] is True
        assert 'Salida registrada exitosamente' in resultado['message']
        assert resultado['data']['hora_salida'] is not None
        assert resultado['data']['estado'] == 'asistio'
    
    def test_registrar_salida_sin_entrada(self):
        """Test: No permitir salida sin entrada previa"""
        manager = AsistenciaManager()
        
        resultado = manager.registrarSalida(999999)  # ID inexistente
        
        assert resultado['success'] is False
        assert 'no encontrada' in resultado['message'].lower()
    
    def test_listar_por_empleado(self, empleado_test, turno_test):
        """Test: Listar asistencias de un empleado"""
        manager = AsistenciaManager()
        
        # Crear varias asistencias
        manager.registrarEntrada(empleado_test['id_empleado'], turno_test['id_turno'])
        
        resultado = manager.listarPorEmpleado(empleado_test['id_empleado'])
        
        assert resultado['success'] is True
        assert isinstance(resultado['data'], list)
        assert len(resultado['data']) > 0
    
    def test_actualizar_estado(self, empleado_test, turno_test):
        """Test: Actualizar estado de asistencia"""
        manager = AsistenciaManager()
        
        # Crear asistencia
        entrada = manager.registrarEntrada(empleado_test['id_empleado'], turno_test['id_turno'])
        id_asistencia = entrada['data']['id_asistencia']
        
        # Actualizar estado
        resultado = manager.actualizarEstado(
            id_asistencia,
            'tardanza',
            'Llegó 15 minutos tarde'
        )
        
        assert resultado['success'] is True
        assert resultado['data']['estado'] == 'tardanza'
        assert 'Llegó 15 minutos tarde' in resultado['data']['observaciones']
    
    def test_actualizar_estado_invalido(self, empleado_test, turno_test):
        """Test: Rechazar estado inválido"""
        manager = AsistenciaManager()
        
        entrada = manager.registrarEntrada(empleado_test['id_empleado'], turno_test['id_turno'])
        id_asistencia = entrada['data']['id_asistencia']
        
        resultado = manager.actualizarEstado(id_asistencia, 'estado_invalido')
        
        assert resultado['success'] is False
        assert 'inválido' in resultado['message'].lower()
    
    def test_obtener_reporte_mensual(self, empleado_test, turno_test):
        """Test: Generar reporte mensual"""
        manager = AsistenciaManager()
        
        # Crear asistencia
        manager.registrarEntrada(empleado_test['id_empleado'], turno_test['id_turno'])
        
        # Obtener reporte
        hoy = date.today()
        resultado = manager.obtenerReporteMensual(
            empleado_test['id_empleado'],
            hoy.year,
            hoy.month
        )
        
        assert resultado['success'] is True
        assert 'asistencias' in resultado['data']
        assert 'estadisticas' in resultado['data']
        assert 'total' in resultado['data']['estadisticas']
        assert resultado['data']['estadisticas']['total'] > 0


@pytest.mark.database
class TestAsistenciaDAO:
    """Tests para AsistenciaDAO"""
    
    def test_crear_asistencia(self, empleado_test, turno_test):
        """Test: Crear registro de asistencia"""
        dao = AsistenciaDAO()
        
        asistencia = Asistencia(
            id_empleado=empleado_test['id_empleado'],
            id_turno=turno_test['id_turno'],
            fecha=date.today(),
            hora_entrada=datetime.now(),
            estado='pendiente'
        )
        
        resp = dao.crear(asistencia)
        
        assert resp.data is not None
        assert len(resp.data) > 0
        assert resp.data[0]['id_empleado'] == empleado_test['id_empleado']
    
    def test_obtener_por_id_con_joins(self, empleado_test, turno_test):
        """Test: Obtener asistencia con información de empleado y turno"""
        dao = AsistenciaDAO()
        
        # Crear asistencia
        asistencia = Asistencia(
            id_empleado=empleado_test['id_empleado'],
            id_turno=turno_test['id_turno'],
            fecha=date.today(),
            hora_entrada=datetime.now(),
            estado='pendiente'
        )
        resp_crear = dao.crear(asistencia)
        id_asistencia = resp_crear.data[0]['id_asistencia']
        
        # Obtener con JOINs
        resp = dao.obtener_por_id(id_asistencia)
        
        assert resp.data is not None
        assert len(resp.data) > 0
        # Verificar que incluye datos del empleado y usuario (objetos anidados)
        assert 'empleado' in resp.data[0]
        assert 'cargo' in resp.data[0]['empleado']
        assert 'usuario' in resp.data[0]['empleado']
        assert 'nombre' in resp.data[0]['empleado']['usuario']
    
    def test_listar_por_fecha(self, empleado_test, turno_test):
        """Test: Listar asistencias de una fecha específica"""
        dao = AsistenciaDAO()
        
        # Crear asistencia
        asistencia = Asistencia(
            id_empleado=empleado_test['id_empleado'],
            id_turno=turno_test['id_turno'],
            fecha=date.today(),
            hora_entrada=datetime.now(),
            estado='pendiente'
        )
        dao.crear(asistencia)
        
        # Listar por fecha
        hoy = date.today().isoformat()
        resp = dao.listar_por_fecha(hoy)
        
        assert resp.data is not None
        assert len(resp.data) > 0
    
    def test_registrar_salida_actualiza_estado(self, empleado_test, turno_test):
        """Test: Registrar salida actualiza automáticamente estado a 'asistio'"""
        dao = AsistenciaDAO()
        
        # Crear asistencia con entrada
        asistencia = Asistencia(
            id_empleado=empleado_test['id_empleado'],
            id_turno=turno_test['id_turno'],
            fecha=date.today(),
            hora_entrada=datetime.now(),
            estado='pendiente'
        )
        resp_crear = dao.crear(asistencia)
        id_asistencia = resp_crear.data[0]['id_asistencia']
        
        # Registrar salida
        resp_salida = dao.registrar_salida(id_asistencia, datetime.now())
        
        assert resp_salida.data is not None
        assert resp_salida.data[0]['estado'] == 'asistio'
        assert resp_salida.data[0]['hora_salida'] is not None


@pytest.mark.django_db
class TestAsistenciaEntidad:
    """Tests para la entidad Asistencia"""
    
    def test_to_dict_serialization(self):
        """Test: Serialización correcta a diccionario"""
        asistencia = Asistencia(
            id_asistencia=1,
            id_empleado=5,
            id_turno=10,
            fecha=date(2025, 1, 21),
            hora_entrada=datetime(2025, 1, 21, 8, 0, 0),
            hora_salida=datetime(2025, 1, 21, 16, 0, 0),
            estado='asistio',
            observaciones='Todo normal'
        )
        
        resultado = asistencia.to_dict()
        
        assert resultado['id_asistencia'] == 1
        assert resultado['id_empleado'] == 5
        assert resultado['fecha'] == '2025-01-21'
        assert resultado['hora_entrada'] == '2025-01-21T08:00:00'
        assert resultado['estado'] == 'asistio'
    
    def test_from_dict_deserialization(self):
        """Test: Deserialización correcta desde diccionario"""
        data = {
            'id_asistencia': 1,
            'id_empleado': 5,
            'id_turno': 10,
            'fecha': '2025-01-21',
            'hora_entrada': '2025-01-21T08:00:00',
            'hora_salida': '2025-01-21T16:00:00',
            'estado': 'asistio',
            'observaciones': 'Todo normal'
        }
        
        asistencia = Asistencia.from_dict(data)
        
        assert asistencia.id_asistencia == 1
        assert asistencia.id_empleado == 5
        assert asistencia.estado == 'asistio'
        assert isinstance(asistencia.fecha, date)
        assert isinstance(asistencia.hora_entrada, datetime)
    
    def test_calcular_horas_trabajadas(self):
        """Test: Cálculo correcto de horas trabajadas"""
        asistencia = Asistencia(
            id_empleado=1,
            fecha=date.today(),
            hora_entrada=datetime(2025, 1, 21, 8, 0, 0),
            hora_salida=datetime(2025, 1, 21, 16, 30, 0),
            estado='asistio'
        )
        
        horas = asistencia.calcular_horas_trabajadas()
        
        assert horas == 8.5  # 8 horas y 30 minutos
    
    def test_calcular_horas_sin_salida(self):
        """Test: Retorna 0 si no hay hora de salida"""
        asistencia = Asistencia(
            id_empleado=1,
            fecha=date.today(),
            hora_entrada=datetime(2025, 1, 21, 8, 0, 0),
            estado='pendiente'
        )
        
        horas = asistencia.calcular_horas_trabajadas()
        
        assert horas == 0.0
