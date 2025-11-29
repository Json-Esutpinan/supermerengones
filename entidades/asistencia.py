#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, date


class Asistencia:
    """
    Entidad para control de asistencia de empleados (HU13)
    """

    def __init__(self, id_asistencia=None, id_empleado=None, id_turno=None, 
                 fecha=None, hora_entrada=None, hora_salida=None, 
                 estado='pendiente', observaciones=None, created_at=None):
        self.id_asistencia = id_asistencia
        self.id_empleado = id_empleado
        self.id_turno = id_turno
        self.fecha = fecha if fecha else date.today()
        self.hora_entrada = hora_entrada
        self.hora_salida = hora_salida
        self.estado = estado  # 'pendiente', 'asistio', 'falta', 'tardanza', 'justificado'
        self.observaciones = observaciones
        self.created_at = created_at if created_at else datetime.now()

    def to_dict(self, incluir_datos_empleado=False):
        """Convierte la asistencia a diccionario para JSON"""
        result = {
            "id_asistencia": self.id_asistencia,
            "id_empleado": self.id_empleado,
            "id_turno": self.id_turno,
            "fecha": self.fecha.isoformat() if isinstance(self.fecha, date) else self.fecha,
            "hora_entrada": self.hora_entrada.isoformat() if isinstance(self.hora_entrada, datetime) else self.hora_entrada,
            "hora_salida": self.hora_salida.isoformat() if isinstance(self.hora_salida, datetime) else self.hora_salida,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
        return result

    @staticmethod
    def from_dict(data):
        """Crea una Asistencia desde un diccionario"""
        # Parsear fecha
        fecha = data.get('fecha')
        if isinstance(fecha, str):
            try:
                fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
            except:
                fecha = date.today()
        
        # Parsear hora_entrada
        hora_entrada = data.get('hora_entrada')
        if isinstance(hora_entrada, str):
            try:
                hora_entrada = datetime.fromisoformat(hora_entrada.replace('Z', '+00:00'))
            except:
                hora_entrada = None
        
        # Parsear hora_salida
        hora_salida = data.get('hora_salida')
        if isinstance(hora_salida, str):
            try:
                hora_salida = datetime.fromisoformat(hora_salida.replace('Z', '+00:00'))
            except:
                hora_salida = None
        
        # Parsear created_at
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                created_at = datetime.now()
        
        return Asistencia(
            id_asistencia=data.get('id_asistencia'),
            id_empleado=data.get('id_empleado'),
            id_turno=data.get('id_turno'),
            fecha=fecha,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            estado=data.get('estado', 'pendiente'),
            observaciones=data.get('observaciones'),
            created_at=created_at
        )

    def calcular_horas_trabajadas(self):
        """Calcula las horas trabajadas basado en entrada y salida"""
        if self.hora_entrada and self.hora_salida:
            delta = self.hora_salida - self.hora_entrada
            return delta.total_seconds() / 3600  # retorna horas como float
        return 0

    def __str__(self):
        return f"Asistencia #{self.id_asistencia} - Empleado:{self.id_empleado} - {self.fecha} - {self.estado}"

    def __repr__(self):
        return f"<Asistencia(id={self.id_asistencia}, empleado={self.id_empleado}, fecha={self.fecha}, estado={self.estado})>"
