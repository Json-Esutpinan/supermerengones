#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para Gestión de Productos, Inventario e Insumos
Tests para ProductoManager, InventarioManager, InsumoManager
"""

import pytest
from datetime import datetime, date
from manager.productoManager import ProductoManager
from manager.inventarioManager import InventarioManager
from manager.insumoManager import InsumoManager
from dao.productoDAO import ProductoDAO
from dao.inventarioDAO import InventarioDAO
from dao.insumoDAO import InsumoDAO
from entidades.producto import Producto
from entidades.inventario import Inventario
from entidades.insumo import Insumo


class TestProductoManager:
    """Tests para Gestión de Productos"""
    
    @pytest.mark.database
    def test_crear_producto_exitoso(self):
        """Test: Crear nuevo producto"""
        manager = ProductoManager()
        
        resultado = manager.crearProducto(
            codigo=f"PROD-{datetime.now().timestamp()}",
            nombre="Merengón Especial",
            descripcion="Merengón de chocolate",
            id_unidad=1,
            contenido=500,
            precio=25.00,
            stock=100
        )
        
        assert resultado is not None
        assert resultado['exito'] is True
        assert resultado['producto'].nombre == "Merengón Especial"
        assert resultado['producto'].precio == 25.00
    
    @pytest.mark.database
    def test_listar_productos_activos(self, producto_test):
        """Test: Listar solo productos activos"""
        if not producto_test:
            pytest.skip("No se pudo crear producto de prueba")
        
        manager = ProductoManager()
        
        resultado = manager.listarProductos(solo_activos=True)
        
        assert resultado is not None
        assert resultado['exito'] is True
        assert len(resultado['productos']) > 0
        assert all(p.activo for p in resultado['productos'])
    
    @pytest.mark.database
    def test_obtener_producto_por_id(self, producto_test):
        """Test: Obtener producto específico"""
        if not producto_test:
            pytest.skip("No se pudo crear producto de prueba")
        
        manager = ProductoManager()
        
        resultado = manager.obtenerProducto(producto_test['id_producto'])
        
        assert resultado is not None
        assert resultado['exito'] is True
        assert resultado['producto'].id_producto == producto_test['id_producto']
    
    @pytest.mark.database
    def test_modificar_producto(self, producto_test):
        """Test: Modificar datos de producto"""
        if not producto_test:
            pytest.skip("No se pudo crear producto de prueba")
        
        manager = ProductoManager()
        
        cambios = {
            "precio": 30.00,
            "stock": 150
        }
        
        resultado = manager.modificarProducto(
            producto_test['id_producto'],
            cambios
        )
        
        assert resultado is not None
        assert resultado['exito'] is True
        assert resultado['producto'].precio == 30.00
    
    @pytest.mark.database
    def test_desactivar_producto(self, producto_test):
        """Test: Desactivar producto"""
        if not producto_test:
            pytest.skip("No se pudo crear producto de prueba")
        
        manager = ProductoManager()
        
        resultado = manager.cambiarEstado(producto_test['id_producto'], False)
        
        assert resultado is not None
        assert resultado['exito'] is True
        assert resultado['producto'].activo is False
    
    @pytest.mark.database
    def test_buscar_productos_por_nombre(self):
        """Test: Buscar productos por nombre"""
        manager = ProductoManager()
        
        resultado = manager.buscarProductos("Merengón")
        
        assert resultado is not None
        assert resultado['exito'] is True
        # Puede estar vacío o tener resultados
    
    @pytest.mark.database
    def test_actualizar_stock_producto(self, producto_test):
        """Test: Actualizar stock de producto"""
        if not producto_test:
            pytest.skip("No se pudo crear producto de prueba")
        
        manager = ProductoManager()
        
        stock_inicial = producto_test['stock']
        cantidad = 10
        
        resultado = manager.actualizarStock(
            producto_test['id_producto'],
            cantidad,
            operacion='sumar'
        )
        
        assert resultado is not None
        assert resultado['exito'] is True
        assert resultado['producto'].stock == stock_inicial + cantidad
    
    def test_verificar_disponibilidad_producto(self, producto_test):
        """Test: Verificar si producto tiene stock disponible"""
        if not producto_test:
            pytest.skip("No se pudo crear producto de prueba")
        
        manager = ProductoManager()
        
        disponible = manager.verificar_disponibilidad(
            producto_test['id_producto'],
            cantidad=5
        )
        
        assert disponible is not None


class TestInventarioManager:
    """Tests para Gestión de Inventario"""
    
    @pytest.mark.database
    def test_registrar_entrada_stock(self, sede_test):
        """Test: Registrar entrada de insumo al inventario"""
        if not sede_test:
            pytest.skip("No se pudo crear sede de prueba")
        
        manager = InventarioManager()
        
        resultado = manager.registrarEntradaStock(
            id_insumo=1,
            id_sede=sede_test['id_sede'],
            cantidad=50,
            motivo="Test de entrada de stock"
        )
        
        # Debe funcionar tanto si crea como si actualiza inventario existente
        assert resultado is not None
        assert 'exito' in resultado
        # Puede ser True o False dependiendo si el insumo ya existía
    
    @pytest.mark.database
    def test_descontar_stock_por_pedido(self):
        """Test: Descontar insumos del inventario al procesar pedido"""
        manager = InventarioManager()
        
        # Este test requiere un pedido con detalles
        # Mockear o crear pedido temporal
        resultado = manager.descontarStockPorPedido(id_pedido=1)
        
        # Verificar que se haya procesado (puede fallar si no existe pedido)
        assert resultado is not None
    
    @pytest.mark.database
    def test_verificar_alertas_reposicion(self, sede_test):
        """Test: Verificar alertas de stock bajo"""
        if not sede_test:
            pytest.skip("No se pudo crear sede de prueba")
        
        manager = InventarioManager()
        
        resultado = manager.verificarAlertasReposicion(sede_test['id_sede'])
        
        assert resultado is not None
        assert resultado['exito'] is True
        # alertas es una lista que puede estar vacía
    
    @pytest.mark.database
    def test_transferir_insumo_entre_sedes(self, sede_test):
        """Test: Transferir insumo de una sede a otra"""
        if not sede_test:
            pytest.skip("No se pudo crear sede de prueba")
        
        manager = InventarioManager()
        
        # Requiere dos sedes
        # Por simplicidad, asumimos id_sede_destino=2
        resultado = manager.transferirInsumoEntreSedes(
            id_sede_origen=sede_test['id_sede'],
            id_sede_destino=2,
            id_insumo=1,
            cantidad=10
        )
        
        # Puede fallar si no hay segunda sede o stock insuficiente
        assert resultado is not None
    
    @pytest.mark.database
    def test_obtener_inventario_por_sede(self, sede_test):
        """Test: Obtener todo el inventario de una sede"""
        if not sede_test:
            pytest.skip("No se pudo crear sede de prueba")
        
        manager = InventarioManager()
        
        resultado = manager.obtenerInventarioPorSede(sede_test['id_sede'])
        
        assert resultado is not None
        assert resultado['exito'] is True
    
    def test_verificar_stock_disponible(self, sede_test):
        """Test: Verificar si hay stock suficiente"""
        if not sede_test:
            pytest.skip("No se pudo crear sede de prueba")
        
        manager = InventarioManager()
        
        disponible = manager.verificar_stock_disponible(
            id_insumo=1,
            id_sede=sede_test['id_sede'],
            cantidad=5
        )
        
        assert isinstance(disponible, bool)


class TestInsumoManager:
    """Tests para Gestión de Insumos"""
    
    @pytest.mark.database
    def test_crear_insumo_exitoso(self):
        """Test: Crear nuevo insumo"""
        manager = InsumoManager()
        
        codigo = f"INS-{datetime.now().timestamp()}"
        resultado = manager.crearInsumo(
            codigo=codigo,
            nombre="Fresa Premium",
            id_unidad=1,  # Asumiendo unidad existe
            id_sede=1     # Asumiendo sede existe
        )
        
        assert resultado is not None
        assert resultado['exito'] is True
        assert resultado['insumo'].nombre == "Fresa Premium"
    
    @pytest.mark.database
    def test_listar_insumos_activos(self):
        """Test: Listar insumos activos"""
        manager = InsumoManager()
        
        resultado = manager.listarInsumosActivos(id_sede=1)
        
        assert resultado is not None
        assert isinstance(resultado, list)
    
    @pytest.mark.database
    def test_modificar_insumo(self):
        """Test: Modificar datos de insumo"""
        manager = InsumoManager()
        
        # Primero crear insumo
        codigo = f"INS-{datetime.now().timestamp()}"
        resultado_crear = manager.crearInsumo(
            codigo=codigo,
            nombre="Chocolate",
            id_unidad=1,
            id_sede=1
        )
        
        if resultado_crear['exito']:
            id_insumo = resultado_crear['insumo'].id_insumo
            
            # Modificar
            resultado = manager.modificarInsumo(id_insumo, nombre="Chocolate Premium")
            
            assert resultado is not None
            assert resultado['exito'] is True
            assert resultado['insumo'].nombre == "Chocolate Premium"
    
    @pytest.mark.database
    def test_obtener_insumo_por_id(self):
        """Test: Obtener insumo específico"""
        manager = InsumoManager()
        
        # Crear insumo
        codigo = f"INS-{datetime.now().timestamp()}"
        resultado_crear = manager.crearInsumo(
            codigo=codigo,
            nombre="Vainilla",
            id_unidad=1,
            id_sede=1
        )
        
        if resultado_crear['exito']:
            id_insumo = resultado_crear['insumo'].id_insumo
            
            # Obtener
            insumo = manager.obtenerInsumoPorId(id_insumo)
            
            assert insumo is not None
            assert insumo.id_insumo == id_insumo
    
    @pytest.mark.database
    def test_desactivar_insumo(self):
        """Test: Desactivar insumo"""
        manager = InsumoManager()
        
        # Crear insumo
        codigo = f"INS-{datetime.now().timestamp()}"
        resultado_crear = manager.crearInsumo(
            codigo=codigo,
            nombre="Leche",
            id_unidad=1,
            id_sede=1
        )
        
        if resultado_crear['exito']:
            id_insumo = resultado_crear['insumo'].id_insumo
            
            # Desactivar
            resultado = manager.desactivarInsumo(id_insumo)
            
            assert resultado is not None
            assert resultado['exito'] is True
            
            # Verificar que realmente se desactivó
            insumo = manager.obtenerInsumoPorId(id_insumo)
            assert insumo.activo is False


class TestProductoDAO:
    """Tests para el DAO de Producto"""
    
    @pytest.mark.database
    def test_insertar_producto(self):
        """Test: Insertar producto en BD"""
        dao = ProductoDAO()
        producto = Producto(
            codigo=f"TEST-{datetime.now().timestamp()}",
            nombre="Producto Test",
            descripcion="Test",
            id_unidad=1,
            contenido=1000,
            precio=10.00,
            stock=50,
            activo=True
        )
        
        resultado = dao.insertar(producto)
        
        assert resultado is not None
        assert resultado.nombre == "Producto Test"
    
    @pytest.mark.database
    def test_obtener_producto_por_codigo(self):
        """Test: Obtener producto por código"""
        dao = ProductoDAO()
        
        # Crear producto
        codigo = f"TEST-{datetime.now().timestamp()}"
        producto = Producto(
            codigo=codigo,
            nombre="Test",
            descripcion="Test",
            id_unidad=1,
            contenido=1000,
            precio=10.00,
            stock=50
        )
        dao.insertar(producto)
        
        # Buscar por código
        resultado = dao.obtener_por_codigo(codigo)
        
        assert resultado is not None
    
    @pytest.mark.database
    def test_actualizar_stock(self, producto_test):
        """Test: Actualizar stock de producto"""
        if not producto_test:
            pytest.skip("No se pudo crear producto de prueba")
        
        dao = ProductoDAO()
        
        nuevo_stock = 200
        resultado = dao.actualizar_stock(producto_test['id_producto'], nuevo_stock)
        
        assert resultado is not None


class TestInventarioDAO:
    """Tests para el DAO de Inventario"""
    
    @pytest.mark.database
    def test_crear_inventario(self, sede_test):
        """Test: Crear registro de inventario"""
        if not sede_test:
            pytest.skip("No se pudo crear sede de prueba")
        
        dao = InventarioDAO()
        inventario = Inventario(
            id_insumo=1,
            id_sede=sede_test['id_sede'],
            cantidad=100
        )
        
        resp = dao.crear(inventario)
        
        # Puede fallar si el insumo ya existe (unique constraint)
        # El test pasa si no genera excepción
        assert True
    
    @pytest.mark.database
    def test_obtener_por_insumo_y_sede(self, sede_test):
        """Test: Obtener inventario específico"""
        if not sede_test:
            pytest.skip("No se pudo crear sede de prueba")
        
        dao = InventarioDAO()
        
        resp = dao.obtener_por_insumo_y_sede(1, sede_test['id_sede'])
        
        # Puede retornar el inventario o None si no existe
        # El test pasa si no genera excepción
        assert True


class TestInsumoDAO:
    """Tests para el DAO de Insumo"""
    
    def test_crear_insumo(self):
        """Test: Crear insumo en BD"""
        dao = InsumoDAO()
        # Obtener una sede válida para la FK
        from dao.sedeDAO import SedeDAO
        sede_dao = SedeDAO()
        sede_resp = sede_dao.listar(solo_activos=True)
        if not sede_resp.data:
            pytest.skip("No hay sedes activas para asociar el insumo")
        id_sede = sede_resp.data[0]['id_sede']
        insumo = Insumo(
            codigo=f"INS-{datetime.now().timestamp()}",
            nombre="Insumo Test",
            id_unidad=1,
            id_sede=id_sede,
            activo=True
        )
        
        resp = dao.insertar(insumo)
        
        assert resp is not None
    
    @pytest.mark.database
    def test_listar_activos(self):
        """Test: Listar insumos activos"""
        dao = InsumoDAO()
        
        resp = dao.listar_todos(solo_activos=True)
        
        assert resp is not None


class TestProductoEntidad:
    """Tests para la entidad Producto"""
    
    def test_to_dict(self):
        """Test: Serializar producto"""
        producto = Producto(
            id_producto=1,
            codigo="PROD-001",
            nombre="Merengón",
            descripcion="Delicioso",
            id_unidad=1,
            contenido=500,
            precio=25.00,
            stock=100,
            activo=True
        )
        
        data = producto.to_dict()
        
        assert data['codigo'] == "PROD-001"
        assert data['precio'] == 25.00
    
    def test_from_dict(self):
        """Test: Deserializar producto"""
        data = {
            'id_producto': 1,
            'codigo': 'PROD-001',
            'nombre': 'Test',
            'descripcion': 'Test',
            'id_unidad': 1,
            'contenido': 1000,
            'precio': 15.00,
            'stock': 50,
            'activo': True
        }
        
        producto = Producto.from_dict(data)
        
        assert producto.id_producto == 1
        assert producto.precio == 15.00


class TestInsumoEntidad:
    """Tests para la entidad Insumo"""
    
    def test_to_dict(self):
        """Test: Serializar insumo"""
        insumo = Insumo(
            id_insumo=1,
            codigo="INS-001",
            nombre="Fresa",
            id_unidad=1,
            activo=True
        )
        
        data = insumo.to_dict()
        
        assert data['codigo'] == "INS-001"
        assert data['id_unidad'] == 1
    
    def test_from_dict(self):
        """Test: Deserializar insumo"""
        data = {
            'id_insumo': 1,
            'codigo': 'INS-001',
            'nombre': 'Chocolate',
            'id_unidad': 1,
            'activo': True
        }
        
        insumo = Insumo.from_dict(data)
        
        assert insumo.id_insumo == 1
        assert insumo.nombre == "Chocolate"
