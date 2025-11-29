#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class Reclamo:
    """
    Entidad que representa un reclamo en el sistema
    """
    
    def __init__(self, id_reclamo=None, id_pedido=None, id_cliente=None,
                 descripcion='', estado='abierto', fecha=None, fecha_resolucion=None):
        """
        Constructor de Reclamo
        
        Args:
            id_reclamo: ID único del reclamo
            id_pedido: ID del pedido asociado
            id_cliente: ID del cliente que hace el reclamo
            descripcion: Descripción del reclamo
            estado: Estado del reclamo (abierto, en_revision, resuelto, cerrado)
            fecha: Fecha de creación del reclamo
            fecha_resolucion: Fecha de resolución del reclamo
        """
        self.id_reclamo = id_reclamo
        self.id_pedido = id_pedido
        self.id_cliente = id_cliente
        self.descripcion = descripcion
        self.estado = estado
        self.fecha = fecha
        self.fecha_resolucion = fecha_resolucion
    
    def to_dict(self):
        """
        Convierte el reclamo a diccionario
        
        Returns:
            dict con los datos del reclamo
        """
        return {
            'id_reclamo': self.id_reclamo,
            'id_pedido': self.id_pedido,
            'id_cliente': self.id_cliente,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'fecha': self.fecha.isoformat() if isinstance(self.fecha, datetime) else self.fecha,
            'fecha_resolucion': self.fecha_resolucion.isoformat() if isinstance(self.fecha_resolucion, datetime) else self.fecha_resolucion
        }
    
    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Reclamo desde un diccionario
        
        Args:
            data: diccionario con los datos del reclamo
            
        Returns:
            Objeto Reclamo
        """
        return Reclamo(
            id_reclamo=data.get('id_reclamo'),
            id_pedido=data.get('id_pedido'),
            id_cliente=data.get('id_cliente'),
            descripcion=data.get('descripcion', ''),
            estado=data.get('estado', 'abierto'),
            fecha=data.get('fecha'),
            fecha_resolucion=data.get('fecha_resolucion')
        )
    
    def __str__(self):
        return f"Reclamo #{self.id_reclamo} - Pedido: {self.id_pedido} - Estado: {self.estado}"
    
    def __repr__(self):
        return f"Reclamo(id={self.id_reclamo}, pedido={self.id_pedido}, estado='{self.estado}')"
