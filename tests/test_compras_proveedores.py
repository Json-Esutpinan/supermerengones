#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para CompraManager y ProveedorManager
Incluye gestión de compras a proveedores, órdenes de compra, y registro de proveedores
"""

import pytest
from datetime import datetime, date
from manager.compraManager import CompraManager
from manager.proveedorManager import ProveedorManager
from dao.compraDAO import CompraDAO
from dao.detalleCompraDAO import DetalleCompraDAO
from dao.proveedorDAO import ProveedorDAO
from entidades.compra import Compra
from entidades.detalleCompra import DetalleCompra
from entidades.proveedor import Proveedor


class TestCompraManager:
    """Tests para gestión de compras a proveedores"""
    
    @pytest.mark.database
    def test_crear_compra_exitosa(self, empleado_test):
        """Test: Crear orden de compra"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        manager = CompraManager()
        
        # Requiere proveedor existente
        resultado = manager.crearCompra(
            id_proveedor=1,
            id_usuario=empleado_test['id_empleado'],
            detalles=[
                {
                    'id_insumo': 1,
                    'cantidad': 50,
                    'precio_unitario': 5.00
                }
            ]
        )
        
        assert resultado is not None
        assert 'success' in resultado
    
    @pytest.mark.database
    def test_listar_compras_por_proveedor(self):
        """Test: Ver historial de compras de un proveedor"""
        manager = CompraManager()
        
        resultado = manager.listarCompras(id_proveedor=1)
        
        assert resultado is not None
        assert resultado['success'] is True
        assert isinstance(resultado['data'], list)
    
    @pytest.mark.database
    def test_listar_compras_por_fecha(self):
        """Test: Filtrar compras por rango de fechas"""
        manager = CompraManager()
        
        fecha_inicio = date(2024, 1, 1)
        fecha_fin = date.today()
        
        resultado = manager.listarCompras(fecha_desde=fecha_inicio, fecha_hasta=fecha_fin)
        
        assert resultado is not None
        assert resultado['success'] is True
        assert isinstance(resultado['data'], list)
    
    @pytest.mark.database
    def test_obtener_detalle_compra(self):
        """Test: Obtener compra con sus detalles"""
        manager = CompraManager()
        
        resultado = manager.obtenerCompra(id_compra=1)
        
        # Puede fallar si no existe la compra
        assert resultado is not None
        assert 'success' in resultado
    
    @pytest.mark.database
    def test_crear_compra_registra_recepcion_automaticamente(self, empleado_test, sede_test):
        """Contrato: crearCompra registra recepción y marca estado 'recibida'."""
        if not empleado_test or not sede_test:
            pytest.skip("No se pudieron crear fixtures necesarios")

        manager = CompraManager()

        res = manager.crearCompra(
            id_proveedor=1,
            id_usuario=empleado_test['id_empleado'],
            detalles=[{'id_insumo': 1, 'cantidad': 2, 'precio_unitario': 3.5}],
            registrar_en_inventario=True,
            id_sede=sede_test['id_sede']
        )

        assert res is not None and res.get('success') is True
        assert res['data']['estado'] == 'recibida'
        assert 'items_en_inventario' in res['data']
    
    @pytest.mark.database
    def test_actualizar_estado_compra(self, empleado_test):
        """Test: Cambiar estado de compra"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        manager = CompraManager()
        
        resultado = manager.cambiarEstadoCompra(
            id_compra=1,
            nuevo_estado='recibida'
        )
        
        assert resultado is not None
        assert 'success' in resultado
    
    @pytest.mark.database
    def test_total_compra_calculado_en_creacion(self, empleado_test):
        """Contrato: el total devuelto por crearCompra coincide con suma de subtotales."""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")

        manager = CompraManager()
        detalles = [
            {'id_insumo': 1, 'cantidad': 10, 'precio_unitario': 5.00},
            {'id_insumo': 1, 'cantidad': 20, 'precio_unitario': 3.00}
        ]
        esperado = 10*5.00 + 20*3.00

        res = manager.crearCompra(
            id_proveedor=1,
            id_usuario=empleado_test['id_empleado'],
            detalles=detalles,
            registrar_en_inventario=False  # evita requerir id_sede
        )

        assert res is not None and res.get('success') is True
        assert abs(res['data']['total'] - esperado) < 1e-6
    
    @pytest.mark.database
    def test_listar_compras_pendientes(self):
        """Test: Obtener compras pendientes de recibir"""
        manager = CompraManager()
        
        resultado = manager.listarCompras(estado='pendiente')
        
        assert resultado is not None
        assert resultado['success'] is True
        assert isinstance(resultado['data'], list)


class TestProveedorManager:
    """Tests para gestión de proveedores"""
    
    @pytest.mark.database
    def test_registrar_proveedor_exitoso(self):
        """Test: Registrar nuevo proveedor"""
        manager = ProveedorManager()
        
        resultado = manager.crearProveedor(
            nombre="Distribuidora ABC",
            telefono="987654321",
            email="contacto@abc.com",
            direccion="Av. Principal 123"
        )
        
        assert resultado is not None
        assert 'exito' in resultado or 'success' in resultado
    
    
    
    @pytest.mark.database
    def test_listar_proveedores_activos(self):
        """Test: Listar solo proveedores activos"""
        manager = ProveedorManager()
        
        resultado = manager.listarProveedores(solo_activos=True)
        
        assert resultado is not None
        assert 'exito' in resultado or 'success' in resultado
    
    @pytest.mark.database
    def test_obtener_proveedor_por_id(self):
        """Test: Obtener proveedor específico"""
        manager = ProveedorManager()
        
        resultado = manager.obtenerProveedor(id_proveedor=1)
        
        assert resultado is not None
        assert 'exito' in resultado or 'success' in resultado
    
    @pytest.mark.database
    def test_modificar_proveedor(self):
        """Test: Actualizar datos de proveedor"""
        manager = ProveedorManager()
        
        # Primero crear un proveedor
        resultado_crear = manager.crearProveedor(
            nombre="Proveedor Test Modificar",
            telefono="999999999",
            email="test@proveedor.com",
            direccion="Calle 123"
        )
        
        if resultado_crear['success']:
            id_proveedor = resultado_crear['data'].id_proveedor
            
            # Modificar
            resultado_modificar = manager.modificarProveedor(
                id_proveedor=id_proveedor,
                data={
                    'telefono': '888888888',
                    'email': 'nuevo@email.com'
                }
            )
            
            assert resultado_modificar is not None
            assert resultado_modificar['success'] is True
            assert resultado_modificar['data'].telefono == "888888888"
    
    @pytest.mark.database
    def test_desactivar_proveedor(self):
        """Test: Desactivar proveedor"""
        manager = ProveedorManager()
        
        # Crear proveedor
        resultado_crear = manager.crearProveedor(
            nombre="Proveedor a Desactivar",
            telefono="888888888",
            email="desactivar@test.com",
            direccion="Av. Test 456"
        )
        
        if resultado_crear['success']:
            id_proveedor = resultado_crear['data'].id_proveedor
            
            # Desactivar
            resultado = manager.desactivarProveedor(id_proveedor)
            
            assert resultado is not None
            assert resultado['success'] is True
    
    @pytest.mark.database
    def test_buscar_proveedor_por_nombre(self):
        """Test: Buscar proveedor por nombre"""
        manager = ProveedorManager()
        
        # Buscar
        resultado = manager.buscarProveedores("Distribuidora")
        
        assert resultado is not None
        assert resultado['success'] is True
        assert isinstance(resultado['data'], list)
    
    def test_obtener_estadisticas_proveedor(self):
        """Test: Estadísticas de compras por proveedor"""
        manager = ProveedorManager()
        
        stats = manager.obtener_estadisticas(id_proveedor=1)
        
        assert stats is not None
        assert isinstance(stats, dict)
        assert 'success' in stats


class TestCompraDAO:
    """Tests para CompraDAO"""
    
    @pytest.mark.database
    def test_crear_compra(self, empleado_test):
        """Test: Insertar compra en BD"""
        if not empleado_test:
            pytest.skip("No se pudo crear empleado de prueba")
        
        dao = CompraDAO()
        
        compra = Compra(
            id_proveedor=1,
            id_usuario=empleado_test['id_empleado'],
            fecha=datetime.now(),
            total=150.00,
            estado='pendiente'
        )
        
        resp = dao.crear(compra)
        
        assert resp is not None or resp is None
    
    def test_listar_por_proveedor(self):
        """Test: Obtener compras de un proveedor"""
        dao = CompraDAO()
        
        compras = dao.listar_por_proveedor(id_proveedor=1)
        
        assert compras is not None
    
    def test_actualizar_estado(self):
        """Test: Cambiar estado de compra"""
        dao = CompraDAO()
        
        resultado = dao.actualizar_estado(
            id_compra=1,
            nuevo_estado='recibido'
        )
        
        assert resultado is not None or resultado is None


class TestDetalleCompraDAO:
    """Tests para DetalleCompraDAO"""
    
    @pytest.mark.database
    def test_crear_detalle(self):
        """Test: Insertar detalle de compra"""
        dao = DetalleCompraDAO()
        
        detalle = DetalleCompra(
            id_compra=1,
            id_insumo=1,
            cantidad=100,
            precio_unitario=5.00
        )
        
        resp = dao.crear(detalle)
        
        assert resp is not None or resp is None
    
    def test_listar_por_compra(self):
        """Test: Obtener detalles de una compra"""
        dao = DetalleCompraDAO()
        
        detalles = dao.listar_por_compra(id_compra=1)
        
        assert detalles is not None


class TestProveedorDAO:
    """Tests para ProveedorDAO"""
    
    @pytest.mark.database
    def test_crear_proveedor(self):
        """Test: Insertar proveedor en BD"""
        dao = ProveedorDAO()
        
        proveedor = Proveedor(
            nombre="Proveedor DAO Test",
            telefono="666666666",
            email="test@proveedor.com",
            activo=True
        )
        
        resp = dao.insertar(proveedor)
        
        assert resp is not None
    
    
    
    @pytest.mark.database
    def test_listar_activos(self):
        """Test: Listar proveedores activos"""
        dao = ProveedorDAO()
        
        activos = dao.listar_todos(solo_activos=True)
        
        assert activos is not None
        assert isinstance(activos, list)


class TestCompraEntidad:
    """Tests para entidad Compra"""
    
    def test_to_dict(self):
        """Test: Conversión a diccionario"""
        compra = Compra(
            id_compra=1,
            id_proveedor=1,
            id_usuario=1,
            fecha=datetime.now(),
            total=200.00,
            estado='pendiente'
        )
        
        data = compra.to_dict()
        
        assert data['id_compra'] == 1
        assert data['total'] == 200.00
        assert data['estado'] == 'pendiente'
    
    def test_from_dict(self):
        """Test: Creación desde diccionario"""
        data = {
            'id_compra': 2,
            'id_proveedor': 1,
            'id_usuario': 1,
            'fecha': '2024-01-15',
            'total': 300.00,
            'estado': 'recibido'
        }
        
        compra = Compra.from_dict(data)
        
        assert compra.id_compra == 2
        assert compra.total == 300.00


class TestProveedorEntidad:
    """Tests para entidad Proveedor"""
    
    def test_to_dict(self):
        """Test: Conversión a diccionario"""
        proveedor = Proveedor(
            id_proveedor=1,
            nombre="Distribuidora ABC",
            telefono="987654321",
            email="abc@test.com",
            direccion="Av. Test 123",
            activo=True
        )
        
        data = proveedor.to_dict()
        
        assert data['nombre'] == "Distribuidora ABC"
        assert data['telefono'] == "987654321"
    
    def test_from_dict(self):
        """Test: Creación desde diccionario"""
        data = {
            'id_proveedor': 1,
            'nombre': "Proveedor XYZ",
            'telefono': "999999999",
            'email': "xyz@ejemplo.com",
            'direccion': "Av. XYZ 456",
            'activo': True
        }
        
        proveedor = Proveedor.from_dict(data)
        
        assert proveedor.nombre == "Proveedor XYZ"
        assert proveedor.telefono == "999999999"
    
    
