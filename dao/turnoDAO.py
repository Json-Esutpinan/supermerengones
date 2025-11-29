#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client
from entidades.turno import Turno

class TurnoDAO:
    def __init__(self):
        self.supabase = get_supabase_client()

    def crear(self, turno: Turno):
        """Crea un nuevo turno"""
        data = turno.to_dict()
        # Remover id_turno si es None (se genera automáticamente)
        if data.get('id_turno') is None:
            data.pop('id_turno', None)
        resp = self.supabase.table("turno").insert(data).execute()
        return resp

    def obtener_por_id(self, id_turno):
        """
        Obtiene un turno por su ID con información del empleado y sede
        """
        resp = self.supabase.table("turno").select(
            "*, empleado(cargo, usuario(nombre, email), sede(nombre))"
        ).eq("id_turno", id_turno).limit(1).execute()
        return resp
    
    def listar_todos(self, limite=None):
        """
        Lista todos los turnos con información del empleado
        
        Args:
            limite: Número máximo de resultados (opcional)
        """
        query = self.supabase.table("turno").select(
            "*, empleado(cargo, usuario(nombre, email), sede(nombre))"
        ).order("fecha", desc=True).order("hora_inicio", desc=False)
        
        if limite:
            query = query.limit(limite)
        
        resp = query.execute()
        return resp
    
    def listar_por_empleado(self, id_empleado, limite=None):
        """
        Lista turnos de un empleado específico
        
        Args:
            id_empleado: ID del empleado
            limite: Número máximo de resultados (opcional)
        """
        query = self.supabase.table("turno").select(
            "*"
        ).eq("id_empleado", id_empleado).order("fecha", desc=True).order("hora_inicio", desc=False)
        
        if limite:
            query = query.limit(limite)
        
        resp = query.execute()
        return resp
    
    def listar_por_fecha(self, fecha, limite=None):
        """
        Lista turnos de una fecha específica
        
        Args:
            fecha: Fecha a consultar (formato YYYY-MM-DD)
            limite: Número máximo de resultados (opcional)
        """
        query = self.supabase.table("turno").select(
            "*, empleado(cargo, usuario(nombre, email), sede(nombre))"
        ).eq("fecha", fecha).order("hora_inicio", desc=False)
        
        if limite:
            query = query.limit(limite)
        
        resp = query.execute()
        return resp
    
    def listar_por_sede_fecha(self, id_sede, fecha, limite=None):
        """
        Lista turnos de una sede en una fecha específica
        
        Args:
            id_sede: ID de la sede
            fecha: Fecha a consultar
            limite: Número máximo de resultados (opcional)
        """
        query = self.supabase.table("turno").select(
            "*, empleado!inner(id_sede, cargo, usuario(nombre, email))"
        ).eq("empleado.id_sede", id_sede).eq("fecha", fecha).order("hora_inicio", desc=False)
        
        if limite:
            query = query.limit(limite)
        
        resp = query.execute()
        return resp
    
    def modificar(self, id_turno, datos):
        """
        Modifica datos de un turno
        
        Args:
            id_turno: ID del turno
            datos: Diccionario con campos a actualizar
        """
        # Solo permitir actualizar fecha, hora_inicio, hora_fin, id_empleado
        datos_permitidos = {}
        if 'fecha' in datos:
            datos_permitidos['fecha'] = datos['fecha']
        if 'hora_inicio' in datos:
            datos_permitidos['hora_inicio'] = datos['hora_inicio']
        if 'hora_fin' in datos:
            datos_permitidos['hora_fin'] = datos['hora_fin']
        if 'id_empleado' in datos:
            datos_permitidos['id_empleado'] = datos['id_empleado']
        
        resp = self.supabase.table("turno").update(datos_permitidos).eq("id_turno", id_turno).execute()
        return resp
    
    def eliminar(self, id_turno):
        """
        Elimina un turno
        
        Args:
            id_turno: ID del turno
        """
        resp = self.supabase.table("turno").delete().eq("id_turno", id_turno).execute()
        return resp