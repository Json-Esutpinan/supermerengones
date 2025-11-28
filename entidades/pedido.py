#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class Pedido:
    """
    Entidad que representa un pedido en el sistema
    """
    
    def __init__(self, id_pedido=None, id_cliente=None, id_sede=None, fecha=None, 
                 estado='pendiente', total=0.0, created_at=None,
                 metodo_pago=None, estado_pago='pendiente', transaccion_id=None, fecha_pago=None):
        """
        Constructor de Pedido
        
        Args:
            id_pedido: ID único del pedido
            id_cliente: ID del cliente que realizó el pedido
            id_sede: ID de la sede donde se procesa el pedido
            fecha: Fecha del pedido
            estado: Estado del pedido (pendiente, en_proceso, completado, cancelado)
            total: Total del pedido
            created_at: Fecha de creación del registro
            metodo_pago: HU15 - Método de pago (efectivo, tarjeta, transferencia, online)
            estado_pago: HU15 - Estado del pago (pendiente, pagado, fallido, reembolsado)
            transaccion_id: HU15 - ID de transacción del gateway
            fecha_pago: HU15 - Fecha y hora del pago
        """
        self.id_pedido = id_pedido
        self.id_cliente = id_cliente
        self.id_sede = id_sede
        self.fecha = fecha
        self.estado = estado
        self.total = float(total) if total else 0.0
        self.created_at = created_at
        
        # HU15 - Campos de pago
        self.metodo_pago = metodo_pago
        self.estado_pago = estado_pago
        self.transaccion_id = transaccion_id
        self.fecha_pago = fecha_pago
        
        # Lista de detalles del pedido (se carga por separado)
        self.detalles = []
    
    def to_dict(self):
        """
        Convierte el pedido a diccionario
        
        Returns:
            dict con los datos del pedido
        """
        return {
            'id_pedido': self.id_pedido,
            'id_cliente': self.id_cliente,
            'id_sede': self.id_sede,
            'fecha': self.fecha.isoformat() if isinstance(self.fecha, datetime) else self.fecha,
            'estado': self.estado,
            'total': float(self.total),
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'metodo_pago': self.metodo_pago,
            'estado_pago': self.estado_pago,
            'transaccion_id': self.transaccion_id,
            'fecha_pago': self.fecha_pago.isoformat() if isinstance(self.fecha_pago, datetime) else self.fecha_pago,
            'detalles': [detalle.to_dict() for detalle in self.detalles]
        }
    
    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Pedido desde un diccionario
        
        Args:
            data: diccionario con los datos del pedido
            
        Returns:
            Objeto Pedido
        """
        # Parsear fecha_pago si viene como string
        fecha_pago = data.get('fecha_pago')
        if isinstance(fecha_pago, str) and fecha_pago:
            try:
                fecha_pago = datetime.fromisoformat(fecha_pago.replace('Z', '+00:00'))
            except:
                fecha_pago = None
        
        return Pedido(
            id_pedido=data.get('id_pedido'),
            id_cliente=data.get('id_cliente'),
            id_sede=data.get('id_sede'),
            fecha=data.get('fecha'),
            estado=data.get('estado', 'pendiente'),
            total=data.get('total', 0.0),
            created_at=data.get('created_at'),
            metodo_pago=data.get('metodo_pago'),
            estado_pago=data.get('estado_pago', 'pendiente'),
            transaccion_id=data.get('transaccion_id'),
            fecha_pago=fecha_pago
        )
    
    def __str__(self):
        return f"Pedido #{self.id_pedido} - Cliente: {self.id_cliente} - Estado: {self.estado} - Total: ${self.total}"
    
    def __repr__(self):
        return f"Pedido(id={self.id_pedido}, cliente={self.id_cliente}, estado='{self.estado}', total={self.total})"
