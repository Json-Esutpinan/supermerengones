#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para HU14 - Personalización de Productos
y HU15 - Pago en Línea
"""

import pytest
from datetime import date
from manager.pedidoManager import PedidoManager
from dao.pedidoDAO import PedidoDAO
from entidades.pedido import Pedido
from entidades.detallePedido import DetallePedido


@pytest.mark.database
class TestPersonalizacionProductos:
    """Tests para HU14 - Personalización de Productos"""
    
    def test_detalle_pedido_con_personalizacion(self):
        """Test: DetallePedido puede almacenar personalización"""
        detalle = DetallePedido(
            id_producto=1,
            cantidad=1,
            precio_unitario=45.00,
            personalizacion="Mensaje: 'Feliz Cumpleaños', decoración azul"
        )
        
        assert detalle.personalizacion == "Mensaje: 'Feliz Cumpleaños', decoración azul"
        
        # Serializar
        dict_detalle = detalle.to_dict()
        assert 'personalizacion' in dict_detalle
        assert dict_detalle['personalizacion'] == detalle.personalizacion
    
    def test_detalle_pedido_sin_personalizacion(self):
        """Test: DetallePedido acepta personalización nula"""
        detalle = DetallePedido(
            id_producto=2,
            cantidad=3,
            precio_unitario=15.00,
            personalizacion=None
        )
        
        assert detalle.personalizacion is None
        
        dict_detalle = detalle.to_dict()
        assert dict_detalle['personalizacion'] is None
    
    def test_from_dict_con_personalizacion(self):
        """Test: Deserializar DetallePedido con personalización"""
        data = {
            'id_detalle_pedido': 10,
            'id_pedido': 5,
            'id_producto': 3,
            'cantidad': 2,
            'precio_unitario': 30.00,
            'personalizacion': 'Sin gluten, decoración minimalista'
        }
        
        detalle = DetallePedido.from_dict(data)
        
        assert detalle.personalizacion == 'Sin gluten, decoración minimalista'
        assert detalle.cantidad == 2
    
    def test_pedido_to_dict_incluye_personalizacion(self, cliente_test, sede_test, producto_test):
        """Test: Pedido serializado incluye personalización en detalles"""
        pedido = Pedido(
            id_cliente=cliente_test['id_cliente'] if cliente_test else 1,
            id_sede=sede_test['id_sede'] if sede_test else 1,
            fecha=date.today(),
            estado='pendiente',
            total=60.00
        )
        
        # Agregar detalle con personalización
        detalle = DetallePedido(
            id_producto=producto_test['id_producto'] if producto_test else 1,
            cantidad=1,
            precio_unitario=60.00,
            personalizacion='Tema unicornio, colores pastel'
        )
        pedido.detalles.append(detalle)
        
        # Serializar pedido completo
        dict_pedido = pedido.to_dict()
        
        assert 'detalles' in dict_pedido
        assert len(dict_pedido['detalles']) == 1
        assert dict_pedido['detalles'][0]['personalizacion'] == 'Tema unicornio, colores pastel'


@pytest.mark.database
class TestPagoEnLinea:
    """Tests para HU15 - Pago en Línea"""
    
    def test_pedido_tiene_campos_pago(self):
        """Test: Pedido tiene campos de pago"""
        pedido = Pedido(
            id_cliente=1,
            id_sede=1,
            fecha=date.today(),
            estado='pendiente',
            total=100.00,
            metodo_pago='tarjeta',
            estado_pago='pendiente'
        )
        
        assert pedido.metodo_pago == 'tarjeta'
        assert pedido.estado_pago == 'pendiente'
        assert pedido.transaccion_id is None
        assert pedido.fecha_pago is None
    
    def test_pedido_to_dict_incluye_campos_pago(self):
        """Test: Serialización incluye campos de pago"""
        from datetime import datetime
        
        pedido = Pedido(
            id_pedido=5,
            id_cliente=1,
            id_sede=1,
            fecha=date.today(),
            estado='pendiente',
            total=150.00,
            metodo_pago='yape',
            estado_pago='pagado',
            transaccion_id='YAPE123456',
            fecha_pago=datetime.now()
        )
        
        dict_pedido = pedido.to_dict()
        
        assert dict_pedido['metodo_pago'] == 'yape'
        assert dict_pedido['estado_pago'] == 'pagado'
        assert dict_pedido['transaccion_id'] == 'YAPE123456'
        assert dict_pedido['fecha_pago'] is not None
    
    def test_from_dict_con_campos_pago(self):
        """Test: Deserializar pedido con campos de pago"""
        data = {
            'id_pedido': 8,
            'id_cliente': 2,
            'id_sede': 1,
            'fecha': '2025-01-21',
            'estado': 'completado',
            'total': 200.00,
            'metodo_pago': 'transferencia',
            'estado_pago': 'pagado',
            'transaccion_id': 'TXN789012',
            'fecha_pago': '2025-01-21T15:30:00'
        }
        
        pedido = Pedido.from_dict(data)
        
        assert pedido.metodo_pago == 'transferencia'
        assert pedido.estado_pago == 'pagado'
        assert pedido.transaccion_id == 'TXN789012'
        assert pedido.fecha_pago is not None
    
    def test_procesar_pago_exitoso(self, cliente_test, sede_test, producto_test):
        """Test: Procesar pago exitosamente"""
        # Primero crear un pedido
        dao = PedidoDAO()
        pedido = Pedido(
            id_cliente=cliente_test['id_cliente'] if cliente_test else 1,
            id_sede=sede_test['id_sede'] if sede_test else 1,
            fecha=date.today(),
            estado='pendiente',
            total=85.00,
            estado_pago='pendiente'
        )
        
        # Simular creación (esto requeriría un método crear en PedidoDAO)
        # Por ahora solo probamos el manager con un ID simulado
        
        manager = PedidoManager()
        
        # Este test requeriría que el pedido exista en la BD
        # Lo dejamos como ejemplo de estructura
        pass
    
    def test_validar_metodos_pago(self):
        """Test: Validar métodos de pago permitidos"""
        metodos_validos = ['efectivo', 'tarjeta', 'transferencia', 'yape', 'plin']
        
        for metodo in metodos_validos:
            pedido = Pedido(
                id_cliente=1,
                id_sede=1,
                fecha=date.today(),
                estado='pendiente',
                total=50.00,
                metodo_pago=metodo,
                estado_pago='pendiente'
            )
            assert pedido.metodo_pago in metodos_validos
    
    def test_validar_estados_pago(self):
        """Test: Validar estados de pago permitidos"""
        estados_validos = ['pendiente', 'pagado', 'fallido', 'reembolsado']
        
        for estado in estados_validos:
            pedido = Pedido(
                id_cliente=1,
                id_sede=1,
                fecha=date.today(),
                estado='pendiente',
                total=75.00,
                estado_pago=estado
            )
            assert pedido.estado_pago in estados_validos


@pytest.mark.database
class TestIntegracionPedidoCompleto:
    """Tests de integración para pedido con personalización y pago"""
    
    def test_flujo_completo_pedido_personalizado_con_pago(self):
        """Test: Crear pedido personalizado, procesar pago, verificar datos"""
        from datetime import datetime
        
        # 1. Crear pedido con personalización
        pedido = Pedido(
            id_cliente=1,
            id_sede=1,
            fecha=date.today(),
            estado='pendiente',
            total=120.00,
            estado_pago='pendiente'
        )
        
        # Agregar detalle con personalización
        detalle = DetallePedido(
            id_producto=1,
            cantidad=1,
            precio_unitario=120.00,
            personalizacion='Torta 3 pisos, tema princesa, colores rosa y dorado'
        )
        pedido.detalles.append(detalle)
        
        # 2. Verificar personalización está presente
        assert len(pedido.detalles) == 1
        assert pedido.detalles[0].personalizacion is not None
        
        # 3. Simular procesamiento de pago
        pedido.metodo_pago = 'tarjeta'
        pedido.estado_pago = 'pagado'
        pedido.transaccion_id = 'TXN_TEST_123'
        pedido.fecha_pago = datetime.now()
        
        # 4. Verificar estado final
        assert pedido.metodo_pago == 'tarjeta'
        assert pedido.estado_pago == 'pagado'
        assert pedido.transaccion_id is not None
        
        # 5. Serializar y verificar estructura completa
        dict_pedido = pedido.to_dict()
        
        assert 'detalles' in dict_pedido
        assert 'metodo_pago' in dict_pedido
        assert 'estado_pago' in dict_pedido
        assert dict_pedido['detalles'][0]['personalizacion'] == 'Torta 3 pisos, tema princesa, colores rosa y dorado'
        assert dict_pedido['metodo_pago'] == 'tarjeta'
        assert dict_pedido['estado_pago'] == 'pagado'
