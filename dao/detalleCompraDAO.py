#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from supabase import create_client, Client
import os

logger = logging.getLogger(__name__)

class DetalleCompraDAO:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def crear(self, detalle):
        """Crea un nuevo detalle de compra"""
        try:
            data = {
                'id_compra': detalle.id_compra,
                'id_insumo': detalle.id_insumo,
                'cantidad': float(detalle.cantidad),
                'precio_unitario': float(detalle.precio_unitario),
                'subtotal': float(detalle.subtotal)
            }
            
            response = self.supabase.table('detalle_compra').insert(data).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]['id_detalle_compra']
            return None
        except Exception as e:
            logger.error(f"Error al crear detalle de compra: {str(e)}")
            return None
    
    def crear_multiple(self, detalles):
        """Crea múltiples detalles de compra en una sola operación"""
        try:
            data = []
            for detalle in detalles:
                data.append({
                    'id_compra': detalle.id_compra,
                    'id_insumo': detalle.id_insumo,
                    'cantidad': float(detalle.cantidad),
                    'precio_unitario': float(detalle.precio_unitario),
                    'subtotal': float(detalle.subtotal)
                })
            
            response = self.supabase.table('detalle_compra').insert(data).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error al crear detalles múltiples: {str(e)}")
            return []
    
    def obtener_por_id(self, id_detalle_compra):
        """Obtiene un detalle por ID con información del insumo"""
        try:
            response = self.supabase.table('detalle_compra').select(
                'id_detalle_compra, id_compra, id_insumo, cantidad, precio_unitario, subtotal, '
                'insumo(nombre, unidad_medida(nombre, abreviatura))'
            ).eq('id_detalle_compra', id_detalle_compra).execute()
            
            if response.data and len(response.data) > 0:
                detalle = response.data[0]
                # Aplanar datos del insumo
                if detalle.get('insumo'):
                    detalle['nombre_insumo'] = detalle['insumo']['nombre']
                    if detalle['insumo'].get('unidad_medida'):
                        detalle['unidad_medida'] = detalle['insumo']['unidad_medida']['abreviatura']
                    del detalle['insumo']
                return detalle
            return None
        except Exception as e:
            logger.error(f"Error al obtener detalle {id_detalle_compra}: {str(e)}")
            return None
    
    def listar_por_compra(self, id_compra):
        """Lista todos los detalles de una compra con información del insumo"""
        try:
            response = self.supabase.table('detalle_compra').select(
                'id_detalle_compra, id_compra, id_insumo, cantidad, precio_unitario, subtotal, '
                'insumo(nombre, unidad_medida(nombre, abreviatura))'
            ).eq('id_compra', id_compra).execute()
            
            detalles = []
            for detalle in response.data:
                if detalle.get('insumo'):
                    detalle['nombre_insumo'] = detalle['insumo']['nombre']
                    if detalle['insumo'].get('unidad_medida'):
                        detalle['unidad_medida'] = detalle['insumo']['unidad_medida']['abreviatura']
                    del detalle['insumo']
                detalles.append(detalle)
            return detalles
        except Exception as e:
            logger.error(f"Error al listar detalles de compra {id_compra}: {str(e)}")
            return []
    
    def listar_por_insumo(self, id_insumo, limite=100):
        """Lista compras de un insumo específico"""
        try:
            response = self.supabase.table('detalle_compra').select(
                'id_detalle_compra, id_compra, id_insumo, cantidad, precio_unitario, subtotal, '
                'compra(fecha, estado, proveedor(nombre))'
            ).eq('id_insumo', id_insumo).order('id_compra', desc=True).limit(limite).execute()
            
            detalles = []
            for detalle in response.data:
                if detalle.get('compra'):
                    detalle['fecha_compra'] = detalle['compra']['fecha']
                    detalle['estado_compra'] = detalle['compra']['estado']
                    if detalle['compra'].get('proveedor'):
                        detalle['nombre_proveedor'] = detalle['compra']['proveedor']['nombre']
                    del detalle['compra']
                detalles.append(detalle)
            return detalles
        except Exception as e:
            logger.error(f"Error al listar detalles por insumo {id_insumo}: {str(e)}")
            return []
    
    def actualizar(self, id_detalle_compra, datos):
        """Actualiza un detalle de compra"""
        try:
            # Campos permitidos
            campos_permitidos = ['cantidad', 'precio_unitario', 'subtotal']
            datos_actualizados = {}
            
            for campo in campos_permitidos:
                if campo in datos:
                    if campo in ['cantidad', 'precio_unitario', 'subtotal']:
                        datos_actualizados[campo] = float(datos[campo])
            
            if not datos_actualizados:
                return False
            
            response = self.supabase.table('detalle_compra').update(
                datos_actualizados
            ).eq('id_detalle_compra', id_detalle_compra).execute()
            
            return response.data and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error al actualizar detalle {id_detalle_compra}: {str(e)}")
            return False
    
    def eliminar(self, id_detalle_compra):
        """Elimina un detalle de compra"""
        try:
            response = self.supabase.table('detalle_compra').delete().eq(
                'id_detalle_compra', id_detalle_compra
            ).execute()
            return response.data and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error al eliminar detalle {id_detalle_compra}: {str(e)}")
            return False
    
    def calcular_total_compra(self, id_compra):
        """Calcula el total de una compra sumando sus detalles"""
        try:
            response = self.supabase.table('detalle_compra').select(
                'subtotal'
            ).eq('id_compra', id_compra).execute()
            
            total = 0.0
            for detalle in response.data:
                total += float(detalle['subtotal'])
            return total
        except Exception as e:
            logger.error(f"Error al calcular total de compra {id_compra}: {str(e)}")
            return 0.0