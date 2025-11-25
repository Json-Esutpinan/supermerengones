#!/usr/bin/python
# -*- coding: utf-8 -*-

class DetallePedido:
    """
    Entidad que representa el detalle de un pedido
    """
    
    def __init__(self, id_detalle=None, id_pedido=None, id_producto=None,
                 cantidad=0, precio_unitario=0.0, subtotal=0.0, nombre_producto=None):
        """
        Constructor de DetallePedido
        
        Args:
            id_detalle: ID único del detalle
            id_pedido: ID del pedido al que pertenece
            id_producto: ID del producto
            cantidad: Cantidad de productos
            precio_unitario: Precio unitario del producto
            subtotal: Subtotal (cantidad * precio_unitario)
            nombre_producto: Nombre del producto (para joins)
        """
        self.id_detalle = id_detalle
        self.id_pedido = id_pedido
        self.id_producto = id_producto
        self.cantidad = int(cantidad) if cantidad else 0
        self.precio_unitario = float(precio_unitario) if precio_unitario else 0.0
        self.subtotal = float(subtotal) if subtotal else 0.0
        self.nombre_producto = nombre_producto
    
    def to_dict(self):
        """
        Convierte el detalle a diccionario
        
        Returns:
            dict con los datos del detalle
        """
        result = {
            'id_detalle': self.id_detalle,
            'id_pedido': self.id_pedido,
            'id_producto': self.id_producto,
            'cantidad': self.cantidad,
            'precio_unitario': float(self.precio_unitario),
            'subtotal': float(self.subtotal)
        }
        
        if self.nombre_producto:
            result['nombre_producto'] = self.nombre_producto
            
        return result
    
    @staticmethod
    def from_dict(data):
        """
        Crea un objeto DetallePedido desde un diccionario
        
        Args:
            data: diccionario con los datos del detalle
            
        Returns:
            Objeto DetallePedido
        """
        return DetallePedido(
            id_detalle=data.get('id_detalle'),
            id_pedido=data.get('id_pedido'),
            id_producto=data.get('id_producto'),
            cantidad=data.get('cantidad', 0),
            precio_unitario=data.get('precio_unitario', 0.0),
            subtotal=data.get('subtotal', 0.0),
            nombre_producto=data.get('nombre_producto')
        )
    
    def __str__(self):
        return f"DetallePedido - Producto: {self.id_producto} x {self.cantidad} = ${self.subtotal}"
    
    def __repr__(self):
        return f"DetallePedido(id={self.id_detalle}, producto={self.id_producto}, cantidad={self.cantidad})"
