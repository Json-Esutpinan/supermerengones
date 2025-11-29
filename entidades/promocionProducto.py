#!/usr/bin/python
# -*- coding: utf-8 -*-

class PromocionProducto:
    """
    Entidad que representa la relación entre una promoción y un producto
    Tabla intermedia para relación many-to-many
    """
    
    def __init__(self, id_promocion_producto=None, id_promocion=None, id_producto=None):
        """
        Constructor de PromocionProducto
        
        Args:
            id_promocion_producto: ID único de la relación
            id_promocion: ID de la promoción
            id_producto: ID del producto
        """
        self.id_promocion_producto = id_promocion_producto
        self.id_promocion = id_promocion
        self.id_producto = id_producto
    
    def to_dict(self):
        """
        Convierte la relación a diccionario
        
        Returns:
            dict con los datos de la relación
        """
        return {
            'id_promocion_producto': self.id_promocion_producto,
            'id_promocion': self.id_promocion,
            'id_producto': self.id_producto
        }
    
    @staticmethod
    def from_dict(data):
        """
        Crea un objeto PromocionProducto desde un diccionario
        
        Args:
            data: diccionario con los datos de la relación
            
        Returns:
            Objeto PromocionProducto
        """
        return PromocionProducto(
            id_promocion_producto=data.get('id_promocion_producto'),
            id_promocion=data.get('id_promocion'),
            id_producto=data.get('id_producto')
        )
    
    def __str__(self):
        return f"PromocionProducto: Promoción #{self.id_promocion} -> Producto #{self.id_producto}"
    
    def __repr__(self):
        return f"PromocionProducto(id={self.id_promocion_producto}, promocion={self.id_promocion}, producto={self.id_producto})"
