#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class MovimientoInventario:
    """
    Entidad que representa un movimiento de inventario (entrada/salida)
    """
    
    def __init__(self, id_movimiento=None, id_inventario=None, tipo=None, cantidad=0, 
                 motivo=None, fecha=None, id_usuario=None):
        self.id_movimiento = id_movimiento
        self.id_inventario = id_inventario
        self.tipo = tipo  # 'entrada' o 'salida'
        self.cantidad = cantidad
        self.motivo = motivo
        self.fecha = fecha or datetime.now()
        self.id_usuario = id_usuario
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_movimiento": self.id_movimiento,
            "id_inventario": self.id_inventario,
            "tipo": self.tipo,
            "cantidad": self.cantidad,
            "motivo": self.motivo,
            "fecha": self.fecha.isoformat() if isinstance(self.fecha, datetime) else self.fecha,
            "id_usuario": self.id_usuario
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto MovimientoInventario desde un diccionario"""
        fecha = data.get('fecha')
        if fecha and isinstance(fecha, str):
            try:
                fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            except:
                fecha = datetime.now()
        
        return MovimientoInventario(
            id_movimiento=data.get('id_movimiento'),
            id_inventario=data.get('id_inventario'),
            tipo=data.get('tipo'),
            cantidad=data.get('cantidad', 0),
            motivo=data.get('motivo'),
            fecha=fecha,
            id_usuario=data.get('id_usuario')
        )
    
    def __str__(self):
        """Representación legible del objeto"""
        return f"Movimiento {self.tipo}: {self.cantidad} unidades - {self.motivo}"
    
    def __repr__(self):
        """Representación técnica del objeto"""
        return f"MovimientoInventario(id={self.id_movimiento}, tipo='{self.tipo}', cantidad={self.cantidad})"
