#!/usr/bin/python
# -*- coding: utf-8 -*-

class Inventario:
    """
    Entidad que representa el inventario de insumos por sede
    """
    
    def __init__(self, id_inventario=None, id_insumo=None, id_sede=None, cantidad=0):
        self.id_inventario = id_inventario
        self.id_insumo = id_insumo
        self.id_sede = id_sede
        self.cantidad = cantidad
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_inventario": self.id_inventario,
            "id_insumo": self.id_insumo,
            "id_sede": self.id_sede,
            "cantidad": self.cantidad
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Inventario desde un diccionario"""
        return Inventario(
            id_inventario=data.get('id_inventario'),
            id_insumo=data.get('id_insumo'),
            id_sede=data.get('id_sede'),
            cantidad=data.get('cantidad', 0)
        )
    
    def __str__(self):
        """Representación legible del objeto"""
        return f"Inventario: Insumo {self.id_insumo} en Sede {self.id_sede} - Cantidad: {self.cantidad}"
    
    def __repr__(self):
        """Representación técnica del objeto"""
        return f"Inventario(id={self.id_inventario}, insumo={self.id_insumo}, sede={self.id_sede}, cantidad={self.cantidad})"
