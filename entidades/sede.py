#!/usr/bin/python
# -*- coding: utf-8 -*-

class Sede:
    """
    Entidad que representa una sede de Supermerengones
    """
    
    def __init__(self, id_sede=None, nombre=None, direccion=None, telefono=None, activo=True):
        self.id_sede = id_sede
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.activo = activo

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id_sede": self.id_sede,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "activo": self.activo
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Sede desde un diccionario"""
        return Sede(
            id_sede=data.get('id_sede'),
            nombre=data.get('nombre'),
            direccion=data.get('direccion'),
            telefono=data.get('telefono'),
            activo=data.get('activo', True)
        )
    
    def __str__(self):
        """Representación legible del objeto"""
        estado = "Activa" if self.activo else "Inactiva"
        return f"Sede {self.nombre} - {self.direccion} ({estado})"
    
    def __repr__(self):
        """Representación técnica del objeto"""
        return f"Sede(id={self.id_sede}, nombre='{self.nombre}', activo={self.activo})"
