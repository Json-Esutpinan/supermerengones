#!/usr/bin/python
# -*- coding: utf-8 -*-

class Proveedor:
    def __init__(self, id_proveedor=None, nombre=None, telefono=None, 
                 email=None, direccion=None, activo=True):
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.activo = activo

    def to_dict(self):
        """
        Convierte la entidad Proveedor a un diccionario
        """
        return {
            'id_proveedor': self.id_proveedor,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'activo': self.activo
        }

    @staticmethod
    def from_dict(data):
        """
        Crea una instancia de Proveedor desde un diccionario
        """
        return Proveedor(
            id_proveedor=data.get('id_proveedor'),
            nombre=data.get('nombre'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            direccion=data.get('direccion'),
            activo=data.get('activo', True)
        )

    def __str__(self):
        return f"Proveedor(id={self.id_proveedor}, nombre={self.nombre}, email={self.email})"

    def __repr__(self):
        return self.__str__()
