#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class Compra:
    def __init__(self, id_compra=None, id_proveedor=None, id_usuario=None, fecha=None, total=0.0, estado='pendiente'):
        self.id_compra = id_compra
        self.id_proveedor = id_proveedor
        self.id_usuario = id_usuario
        self.fecha = fecha if isinstance(fecha, datetime) else datetime.now()
        self.total = float(total) if total else 0.0
        self.estado = estado
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_compra': self.id_compra,
            'id_proveedor': self.id_proveedor,
            'id_usuario': self.id_usuario,
            'fecha': self.fecha.isoformat() if isinstance(self.fecha, datetime) else self.fecha,
            'total': self.total,
            'estado': self.estado
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Compra desde un diccionario"""
        fecha = data.get('fecha')
        if isinstance(fecha, str):
            try:
                fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            except:
                fecha = datetime.now()
        
        return Compra(
            id_compra=data.get('id_compra'),
            id_proveedor=data.get('id_proveedor'),
            id_usuario=data.get('id_usuario'),
            fecha=fecha,
            total=data.get('total', 0.0),
            estado=data.get('estado', 'pendiente')
        )
    
    def __str__(self):
        return f"Compra #{self.id_compra} - Proveedor:{self.id_proveedor} Total:${self.total} [{self.estado}]"
    
    def __repr__(self):
        return f"<Compra(id={self.id_compra}, proveedor={self.id_proveedor}, total={self.total}, estado={self.estado})>"
