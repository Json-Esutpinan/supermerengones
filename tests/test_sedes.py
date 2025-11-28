#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para SedeManager
Gestión de sedes (sucursales) de la empresa
"""

import pytest
from datetime import datetime
from manager.sedeManager import SedeManager
from dao.sedeDAO import SedeDAO
from entidades.sede import Sede


class TestSedeManager:
    """Tests para gestión de sedes"""
    
    @pytest.mark.database
    def test_crear_sede_exitosa(self):
        """Test: Crear nueva sede"""
        manager = SedeManager()
        
        resultado = manager.crearSede(
            nombre=f"Sede Norte {datetime.now().timestamp()}",
            direccion="Av. Los Olivos 456",
            telefono="987654321"
        )
        
        assert resultado is not None
        assert resultado['success'] is True
        assert isinstance(resultado['data'], Sede)
    
    @pytest.mark.database
    def test_crear_sede_nombre_duplicado(self):
        """Test: No permite nombre de sede duplicado"""
        manager = SedeManager()
        
        nombre_unico = f"Sede Central {datetime.now().timestamp()}"
        
        # Primera sede
        resultado1 = manager.crearSede(
            nombre=nombre_unico,
            direccion="Av. Principal 123",
            telefono="111111111"
        )
        
        # Intento de duplicado
        resultado2 = manager.crearSede(
            nombre=nombre_unico,  # Nombre duplicado
            direccion="Otra dirección",
            telefono="222222222"
        )
        
        assert resultado2 is not None
        assert resultado2['success'] is False
    
    @pytest.mark.database
    def test_listar_sedes_activas(self):
        """Test: Listar solo sedes activas"""
        manager = SedeManager()
        
        resultado = manager.listarSedes(solo_activos=True)
        
        assert resultado is not None
        assert resultado['success'] is True
    
    @pytest.mark.database
    def test_obtener_sede_por_id(self):
        """Test: Obtener sede específica"""
        manager = SedeManager()
        
        resultado = manager.obtenerSede(id_sede=1)
        
        assert resultado is not None
    
    @pytest.mark.database
    def test_modificar_sede(self):
        """Test: Actualizar datos de sede"""
        manager = SedeManager()
        
        # Crear sede
        resultado = manager.crearSede(
            nombre=f"Sede Test Modificar {datetime.now().timestamp()}",
            direccion="Dirección Original",
            telefono="111111111"
        )
        
        if resultado and resultado['success']:
            # Modificar
            cambios = {
                "direccion": "Dirección Actualizada",
                "telefono": "999999999"
            }
            actualizada = manager.modificarSede(
                id_sede=resultado['data'].id_sede,
                cambios=cambios
            )
            
            assert actualizada is not None
            assert actualizada['success'] is True
    
    @pytest.mark.database
    def test_desactivar_sede(self):
        """Test: Desactivar sede"""
        manager = SedeManager()
        
        # Crear y desactivar
        resultado = manager.crearSede(
            nombre=f"Sede a Desactivar {datetime.now().timestamp()}",
            direccion="Av. Test 789",
            telefono="888888888"
        )
        
        if resultado and resultado['success']:
            desactivada = manager.desactivarSede(resultado['data'].id_sede)
            
            assert desactivada is not None
            assert desactivada['success'] is True
    

class TestSedeDAO:
    """Tests para SedeDAO"""
    
    @pytest.mark.database
    def test_crear_sede(self):
        """Test: Insertar sede en BD"""
        dao = SedeDAO()
        
        sede = Sede(
            nombre=f"Sede DAO Test {datetime.now().timestamp()}",
            direccion="Av. DAO 123",
            telefono="444444444",
            activo=True
        )
        
        resp = dao.crear(sede)
        
        assert resp.data is not None
    

class TestSedeEntidad:
    """Tests para entidad Sede"""
    
    def test_to_dict(self):
        """Test: Conversión a diccionario"""
        sede = Sede(
            id_sede=1,
            nombre="Sede Central",
            direccion="Av. Principal 123",
            telefono="987654321",
            activo=True
        )
        
        data = sede.to_dict()
        
        assert data['nombre'] == "Sede Central"
        assert data['direccion'] == "Av. Principal 123"
        assert data['activo'] is True
    
    def test_from_dict(self):
        """Test: Creación desde diccionario"""
        data = {
            'id_sede': 2,
            'nombre': "Sede Norte",
            'direccion': "Av. Los Olivos 456",
            'telefono': "111222333",
            'activo': True
        }
        
        sede = Sede.from_dict(data)
        
        assert sede.nombre == "Sede Norte"
        assert sede.direccion == "Av. Los Olivos 456"
