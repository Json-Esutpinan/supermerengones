#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class Pedido:
    """
    Entidad que representa un pedido en el sistema
    """
    
    def __init__(self, id_pedido=None, id_cliente=None, fecha=None, 
                 estado='pendiente', total=0.0, created_at=None):
        """
        Constructor de Pedido
        
        Args:
            id_pedido: ID único del pedido
            id_cliente: ID del cliente que realizó el pedido
            fecha: Fecha del pedido
            estado: Estado del pedido (pendiente, en_proceso, completado, cancelado)
            total: Total del pedido
            created_at: Fecha de creación del registro
        """
        self.id_pedido = id_pedido
        self.id_cliente = id_cliente
        self.fecha = fecha
        self.estado = estado
        self.total = float(total) if total else 0.0
        self.created_at = created_at
        
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
            'fecha': self.fecha.isoformat() if isinstance(self.fecha, datetime) else self.fecha,
            'estado': self.estado,
            'total': float(self.total),
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
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
        return Pedido(
            id_pedido=data.get('id_pedido'),
            id_cliente=data.get('id_cliente'),
            fecha=data.get('fecha'),
            estado=data.get('estado', 'pendiente'),
            total=data.get('total', 0.0),
            created_at=data.get('created_at')
        )
    
    def __str__(self):
        return f"Pedido #{self.id_pedido} - Cliente: {self.id_cliente} - Estado: {self.estado} - Total: ${self.total}"
    
    def __repr__(self):
        return f"Pedido(id={self.id_pedido}, cliente={self.id_cliente}, estado='{self.estado}', total={self.total})"
