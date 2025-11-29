#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from config import get_supabase_client

logger = logging.getLogger(__name__)


class AsistenciaDAO:
    """
    DAO para gestión de asistencia de empleados (HU13)
    """

    def __init__(self):
        self.supabase = get_supabase_client()

    def crear(self, asistencia):
        """Crea un nuevo registro de asistencia"""
        try:
            datos = {
                "id_empleado": asistencia.id_empleado,
                "id_turno": asistencia.id_turno,
                "fecha": asistencia.fecha.isoformat() if hasattr(asistencia.fecha, 'isoformat') else asistencia.fecha,
                "hora_entrada": asistencia.hora_entrada.isoformat() if asistencia.hora_entrada and hasattr(asistencia.hora_entrada, 'isoformat') else asistencia.hora_entrada,
                "hora_salida": asistencia.hora_salida.isoformat() if asistencia.hora_salida and hasattr(asistencia.hora_salida, 'isoformat') else asistencia.hora_salida,
                "estado": asistencia.estado,
                "observaciones": asistencia.observaciones
            }
            
            resp = self.supabase.table('asistencia').insert(datos).execute()
            return resp
        except Exception as e:
            logger.error(f"Error al crear asistencia: {str(e)}")
            raise

    def obtener_por_id(self, id_asistencia):
        """Obtiene una asistencia por ID con datos del empleado y turno"""
        try:
            resp = self.supabase.table('asistencia')\
                .select('*, empleado(id_empleado, cargo, usuario(nombre, email)), turno(fecha, hora_inicio, hora_fin)')\
                .eq('id_asistencia', id_asistencia)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al obtener asistencia: {str(e)}")
            raise

    def listar_por_empleado(self, id_empleado, limite=50):
        """Lista asistencias de un empleado específico"""
        try:
            resp = self.supabase.table('asistencia')\
                .select('*, turno(fecha, hora_inicio, hora_fin)')\
                .eq('id_empleado', id_empleado)\
                .order('fecha', desc=True)\
                .order('created_at', desc=True)\
                .limit(limite)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al listar asistencias del empleado: {str(e)}")
            raise

    def listar_por_fecha(self, fecha, limite=100):
        """Lista todas las asistencias en una fecha específica"""
        try:
            resp = self.supabase.table('asistencia')\
                .select('*, empleado(id_empleado, cargo, usuario(nombre, email), sede(nombre))')\
                .eq('fecha', fecha)\
                .order('hora_entrada')\
                .limit(limite)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al listar asistencias por fecha: {str(e)}")
            raise

    def listar_por_empleado_fecha(self, id_empleado, fecha):
        """Lista asistencias de un empleado en una fecha específica"""
        try:
            resp = self.supabase.table('asistencia')\
                .select('*, turno(fecha, hora_inicio, hora_fin)')\
                .eq('id_empleado', id_empleado)\
                .eq('fecha', fecha)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al listar asistencias: {str(e)}")
            raise

    def listar_por_estado(self, estado, limite=100):
        """Lista asistencias por estado"""
        try:
            resp = self.supabase.table('asistencia')\
                .select('*, empleado(id_empleado, cargo, usuario(nombre, email))')\
                .eq('estado', estado)\
                .order('fecha', desc=True)\
                .limit(limite)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al listar asistencias por estado: {str(e)}")
            raise

    def registrar_entrada(self, id_asistencia, hora_entrada):
        """Registra la hora de entrada"""
        try:
            datos = {
                "hora_entrada": hora_entrada.isoformat() if hasattr(hora_entrada, 'isoformat') else hora_entrada
            }
            resp = self.supabase.table('asistencia')\
                .update(datos)\
                .eq('id_asistencia', id_asistencia)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al registrar entrada: {str(e)}")
            raise

    def registrar_salida(self, id_asistencia, hora_salida):
        """Registra la hora de salida y actualiza estado a 'asistio'"""
        try:
            datos = {
                "hora_salida": hora_salida.isoformat() if hasattr(hora_salida, 'isoformat') else hora_salida,
                "estado": "asistio"
            }
            resp = self.supabase.table('asistencia')\
                .update(datos)\
                .eq('id_asistencia', id_asistencia)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al registrar salida: {str(e)}")
            raise

    def actualizar_estado(self, id_asistencia, estado, observaciones=None):
        """Actualiza el estado de una asistencia"""
        try:
            datos = {"estado": estado}
            if observaciones:
                datos["observaciones"] = observaciones
            
            resp = self.supabase.table('asistencia')\
                .update(datos)\
                .eq('id_asistencia', id_asistencia)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al actualizar estado: {str(e)}")
            raise

    def modificar(self, id_asistencia, datos):
        """Modifica campos de una asistencia"""
        try:
            # Filtrar solo campos permitidos
            campos_permitidos = ['id_turno', 'fecha', 'hora_entrada', 'hora_salida', 'estado', 'observaciones']
            datos_filtrados = {k: v for k, v in datos.items() if k in campos_permitidos}
            
            resp = self.supabase.table('asistencia')\
                .update(datos_filtrados)\
                .eq('id_asistencia', id_asistencia)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al modificar asistencia: {str(e)}")
            raise

    def eliminar(self, id_asistencia):
        """Elimina un registro de asistencia"""
        try:
            resp = self.supabase.table('asistencia')\
                .delete()\
                .eq('id_asistencia', id_asistencia)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al eliminar asistencia: {str(e)}")
            raise

    def listar_todas(self, limite=100):
        """Lista todas las asistencias con información completa"""
        try:
            resp = self.supabase.table('asistencia')\
                .select('*, empleado(id_empleado, cargo, usuario(nombre, email), sede(nombre)), turno(fecha, hora_inicio, hora_fin)')\
                .order('fecha', desc=True)\
                .order('created_at', desc=True)\
                .limit(limite)\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al listar todas las asistencias: {str(e)}")
            raise

    def obtener_reporte_mensual(self, id_empleado, year, month):
        """Obtiene asistencias de un empleado en un mes específico"""
        try:
            # Calcular primer y último día del mes
            from datetime import date
            primer_dia = date(year, month, 1)
            if month == 12:
                ultimo_dia = date(year + 1, 1, 1)
            else:
                ultimo_dia = date(year, month + 1, 1)
            
            resp = self.supabase.table('asistencia')\
                .select('*, turno(fecha, hora_inicio, hora_fin)')\
                .eq('id_empleado', id_empleado)\
                .gte('fecha', primer_dia.isoformat())\
                .lt('fecha', ultimo_dia.isoformat())\
                .order('fecha')\
                .execute()
            return resp
        except Exception as e:
            logger.error(f"Error al obtener reporte mensual: {str(e)}")
            raise
