#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from supabase import create_client, Client
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class CompraDAO:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def crear(self, compra):
        """Crea una nueva compra"""
        try:
            data = {
                'id_proveedor': compra.id_proveedor,
                'id_usuario': compra.id_usuario,
                'fecha': compra.fecha.isoformat() if isinstance(compra.fecha, datetime) else compra.fecha,
                'total': float(compra.total),
                'estado': compra.estado
            }
            
            response = self.supabase.table('compra').insert(data).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]['id_compra']
            return None
        except Exception as e:
            logger.error(f"Error al crear compra: {str(e)}")
            return None
    
    def obtener_por_id(self, id_compra):
        """Obtiene una compra por ID con información del proveedor"""
        try:
            response = self.supabase.table('compra').select(
                'id_compra, id_proveedor, id_usuario, fecha, total, estado, '
                'proveedor(nombre, telefono, email)'
            ).eq('id_compra', id_compra).execute()
            
            if response.data and len(response.data) > 0:
                compra = response.data[0]
                # Aplanar datos del proveedor
                if compra.get('proveedor'):
                    compra['nombre_proveedor'] = compra['proveedor']['nombre']
                    compra['telefono_proveedor'] = compra['proveedor'].get('telefono')
                    compra['email_proveedor'] = compra['proveedor'].get('email')
                    del compra['proveedor']
                return compra
            return None
        except Exception as e:
            logger.error(f"Error al obtener compra {id_compra}: {str(e)}")
            return None
    
    def listar_todas(self, limite=100):
        """Lista todas las compras con información del proveedor"""
        try:
            response = self.supabase.table('compra').select(
                'id_compra, id_proveedor, id_usuario, fecha, total, estado, '
                'proveedor(nombre)'
            ).order('fecha', desc=True).limit(limite).execute()
            
            compras = []
            for compra in response.data:
                if compra.get('proveedor'):
                    compra['nombre_proveedor'] = compra['proveedor']['nombre']
                    del compra['proveedor']
                compras.append(compra)
            return compras
        except Exception as e:
            logger.error(f"Error al listar compras: {str(e)}")
            return []
    
    def listar_por_proveedor(self, id_proveedor, limite=100):
        """Lista compras de un proveedor específico"""
        try:
            response = self.supabase.table('compra').select(
                'id_compra, id_proveedor, id_usuario, fecha, total, estado'
            ).eq('id_proveedor', id_proveedor).order('fecha', desc=True).limit(limite).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Error al listar compras del proveedor {id_proveedor}: {str(e)}")
            return []
    
    def listar_por_estado(self, estado, limite=100):
        """Lista compras por estado"""
        try:
            response = self.supabase.table('compra').select(
                'id_compra, id_proveedor, id_usuario, fecha, total, estado, '
                'proveedor(nombre)'
            ).eq('estado', estado).order('fecha', desc=True).limit(limite).execute()
            
            compras = []
            for compra in response.data:
                if compra.get('proveedor'):
                    compra['nombre_proveedor'] = compra['proveedor']['nombre']
                    del compra['proveedor']
                compras.append(compra)
            return compras
        except Exception as e:
            logger.error(f"Error al listar compras por estado {estado}: {str(e)}")
            return []
    
    def listar_por_fecha(self, fecha_desde=None, fecha_hasta=None, limite=100):
        """Lista compras por rango de fechas"""
        try:
            query = self.supabase.table('compra').select(
                'id_compra, id_proveedor, id_usuario, fecha, total, estado, '
                'proveedor(nombre)'
            )
            
            if fecha_desde:
                query = query.gte('fecha', fecha_desde)
            if fecha_hasta:
                query = query.lte('fecha', fecha_hasta)
            
            response = query.order('fecha', desc=True).limit(limite).execute()
            
            compras = []
            for compra in response.data:
                if compra.get('proveedor'):
                    compra['nombre_proveedor'] = compra['proveedor']['nombre']
                    del compra['proveedor']
                compras.append(compra)
            return compras
        except Exception as e:
            logger.error(f"Error al listar compras por fecha: {str(e)}")
            return []
    
    def actualizar_estado(self, id_compra, nuevo_estado):
        """Actualiza el estado de una compra"""
        try:
            response = self.supabase.table('compra').update({
                'estado': nuevo_estado
            }).eq('id_compra', id_compra).execute()
            
            return response.data and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error al actualizar estado de compra {id_compra}: {str(e)}")
            return False
    
    def actualizar_total(self, id_compra, nuevo_total):
        """Actualiza el total de una compra"""
        try:
            response = self.supabase.table('compra').update({
                'total': float(nuevo_total)
            }).eq('id_compra', id_compra).execute()
            
            return response.data and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error al actualizar total de compra {id_compra}: {str(e)}")
            return False
    
    def eliminar(self, id_compra):
        """Elimina una compra (solo si no tiene detalles o en CASCADE)"""
        try:
            response = self.supabase.table('compra').delete().eq('id_compra', id_compra).execute()
            return response.data and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error al eliminar compra {id_compra}: {str(e)}")
            return False