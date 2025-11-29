#!/usr/bin/python
# -*- coding: utf-8 -*-

class DetalleCompra:
    def __init__(self, id_detalle_compra=None, id_compra=None, id_insumo=None, cantidad=0.0, precio_unitario=0.0, subtotal=0.0):
        self.id_detalle_compra = id_detalle_compra
        self.id_compra = id_compra
        self.id_insumo = id_insumo
        self.cantidad = float(cantidad) if cantidad else 0.0
        self.precio_unitario = float(precio_unitario) if precio_unitario else 0.0
        self.subtotal = float(subtotal) if subtotal else 0.0
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_detalle_compra': self.id_detalle_compra,
            'id_compra': self.id_compra,
            'id_insumo': self.id_insumo,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto DetalleCompra desde un diccionario"""
        return DetalleCompra(
            id_detalle_compra=data.get('id_detalle_compra'),
            id_compra=data.get('id_compra'),
            id_insumo=data.get('id_insumo'),
            cantidad=data.get('cantidad', 0.0),
            precio_unitario=data.get('precio_unitario', 0.0),
            subtotal=data.get('subtotal', 0.0)
        )
    
    def calcular_subtotal(self):
        """Calcula el subtotal basado en cantidad y precio unitario"""
        self.subtotal = self.cantidad * self.precio_unitario
        return self.subtotal
    
    def __str__(self):
        return f"Detalle #{self.id_detalle_compra} - Insumo:{self.id_insumo} Cant:{self.cantidad} x ${self.precio_unitario} = ${self.subtotal}"
    
    def __repr__(self):
        return f"<DetalleCompra(id={self.id_detalle_compra}, compra={self.id_compra}, insumo={self.id_insumo}, subtotal={self.subtotal})>"
