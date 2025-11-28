#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime


class Notificacion:
    def __init__(self, id_notificacion=None, id_cliente=None, mensaje=None, fecha=None, leida=False):
        self.id_notificacion = id_notificacion
        self.id_cliente = id_cliente
        self.mensaje = mensaje
        self.fecha = fecha if fecha else datetime.now()
        self.leida = leida

    def to_dict(self):
        """Convierte la notificación a diccionario para JSON"""
        return {
            "id_notificacion": self.id_notificacion,
            "id_cliente": self.id_cliente,
            "mensaje": self.mensaje,
            "fecha": self.fecha.isoformat() if isinstance(self.fecha, datetime) else self.fecha,
            "leida": self.leida
        }

    @staticmethod
    def from_dict(data):
        """Crea una Notificacion desde un diccionario"""
        fecha = data.get('fecha')
        if isinstance(fecha, str):
            try:
                fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            except:
                fecha = datetime.now()
        
        return Notificacion(
            id_notificacion=data.get('id_notificacion'),
            id_cliente=data.get('id_cliente'),
            mensaje=data.get('mensaje'),
            fecha=fecha,
            leida=data.get('leida', False)
        )

    def __str__(self):
        estado = "Leída" if self.leida else "No leída"
        return f"Notificación #{self.id_notificacion} - Cliente:{self.id_cliente} - {estado}"

    def __repr__(self):
        return f"<Notificacion(id={self.id_notificacion}, cliente={self.id_cliente}, leida={self.leida})>"

