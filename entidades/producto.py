#!/usr/bin/python
# -*- coding: utf-8 -*-

class Producto:
    """
    Entidad que representa un producto en el sistema
    """
    
    def __init__(self, id_producto=None, codigo=None, nombre=None, descripcion=None,
                 id_unidad=None, contenido=None, precio=0.0, stock=0, activo=True):
        """
        Constructor de Producto
        
        Args:
            id_producto: ID único del producto
            codigo: Código único del producto
            nombre: Nombre del producto
            descripcion: Descripción del producto
            id_unidad: ID de la unidad de medida
            contenido: Contenido/tamaño del producto (ej: 500g, 1L)
            precio: Precio de venta
            stock: Stock disponible
            activo: Si el producto está activo
        """
        self.id_producto = id_producto
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_unidad = id_unidad
        self.contenido = contenido
        self.precio = float(precio) if precio else 0.0
        self.stock = int(stock) if stock else 0
        self.activo = activo
    
    def to_dict(self):
        """
        Convierte el producto a diccionario
        
        Returns:
            dict con los datos del producto
        """
        return {
            'id_producto': self.id_producto,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'id_unidad': self.id_unidad,
            'contenido': self.contenido,
            'precio': float(self.precio),
            'stock': int(self.stock),
            'activo': self.activo
        }
    
    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Producto desde un diccionario
        
        Args:
            data: diccionario con los datos del producto
            
        Returns:
            Objeto Producto
        """
        return Producto(
            id_producto=data.get('id_producto'),
            codigo=data.get('codigo'),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            id_unidad=data.get('id_unidad'),
            contenido=data.get('contenido'),
            precio=data.get('precio', 0.0),
            stock=data.get('stock', 0),
            activo=data.get('activo', True)
        )
    
    def __str__(self):
        return f"Producto: {self.nombre} - ${self.precio} - Stock: {self.stock}"
    
    def __repr__(self):
        return f"Producto(id={self.id_producto}, codigo='{self.codigo}', nombre='{self.nombre}', precio={self.precio})"
