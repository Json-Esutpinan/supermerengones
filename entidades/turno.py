#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, date, time

class Turno:
    def __init__(self, id_turno=None, id_empleado=None, fecha=None, hora_inicio=None, hora_fin=None):
        self.id_turno = id_turno
        self.id_empleado = id_empleado
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    def to_dict(self):
        return {
            "id_turno": self.id_turno,
            "id_empleado": self.id_empleado,
            "fecha": self.fecha.isoformat() if isinstance(self.fecha, (datetime, date)) else self.fecha,
            "hora_inicio": self.hora_inicio.isoformat() if isinstance(self.hora_inicio, time) else self.hora_inicio,
            "hora_fin": self.hora_fin.isoformat() if isinstance(self.hora_fin, time) else self.hora_fin
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Turno desde un diccionario"""
        fecha = data.get('fecha')
        if isinstance(fecha, str):
            try:
                fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00')).date()
            except:
                fecha = date.today()
        
        hora_inicio = data.get('hora_inicio')
        if isinstance(hora_inicio, str):
            try:
                hora_inicio = datetime.strptime(hora_inicio, "%H:%M:%S").time()
            except:
                try:
                    hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
                except:
                    hora_inicio = None
        
        hora_fin = data.get('hora_fin')
        if isinstance(hora_fin, str):
            try:
                hora_fin = datetime.strptime(hora_fin, "%H:%M:%S").time()
            except:
                try:
                    hora_fin = datetime.strptime(hora_fin, "%H:%M").time()
                except:
                    hora_fin = None
        
        return Turno(
            id_turno=data.get('id_turno'),
            id_empleado=data.get('id_empleado'),
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )
    
    def __str__(self):
        return f"Turno #{self.id_turno} - Empleado:{self.id_empleado} - {self.fecha} {self.hora_inicio}-{self.hora_fin}"
    
    def __repr__(self):
        return f"<Turno(id={self.id_turno}, empleado={self.id_empleado}, fecha={self.fecha}, {self.hora_inicio}-{self.hora_fin})>"
