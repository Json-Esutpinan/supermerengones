#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class Insumo:
    """
    Entidad que representa un insumo en el sistema
    """
    
    def __init__(self, id_insumo=None, codigo=None, nombre=None, descripcion=None,
                 id_unidad=None, id_sede=None, stock_minimo=0, activo=True, created_at=None):
        """
        Constructor de Insumo
        
        Args:
            id_insumo: ID único del insumo
            codigo: Código único del insumo
            nombre: Nombre del insumo
            descripcion: Descripción del insumo
            id_unidad: ID de la unidad de medida
            id_sede: ID de la sede a la que pertenece el insumo
            stock_minimo: Stock mínimo requerido
            activo: Si el insumo está activo
            created_at: Fecha de creación del registro
        """
        self.id_insumo = id_insumo
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_unidad = id_unidad
        self.id_sede = id_sede
        self.stock_minimo = stock_minimo
        self.activo = activo
        self.created_at = created_at
    
    def to_dict(self):
        """
        Convierte el insumo a diccionario
        
        Returns:
            dict con los datos del insumo
        """
        return {
            'id_insumo': self.id_insumo,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'id_unidad': self.id_unidad,
            'id_sede': self.id_sede,
            'stock_minimo': self.stock_minimo,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Insumo desde un diccionario
        
        Args:
            data: diccionario con los datos del insumo
            
        Returns:
            Objeto Insumo
        """
        return Insumo(
            id_insumo=data.get('id_insumo'),
            codigo=data.get('codigo'),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            id_unidad=data.get('id_unidad'),
            id_sede=data.get('id_sede'),
            stock_minimo=data.get('stock_minimo', 0),
            activo=data.get('activo', True),
            created_at=data.get('created_at')
        )
    
    def __str__(self):
        return f"Insumo: {self.nombre} - Código: {self.codigo} - Sede: {self.id_sede}"
    
    def __repr__(self):
        return f"Insumo(id={self.id_insumo}, codigo='{self.codigo}', nombre='{self.nombre}', sede={self.id_sede})"
