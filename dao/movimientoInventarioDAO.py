#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client, TABLA_MOVIMIENTO_INVENTARIO
from entidades.movimientoInventario import MovimientoInventario
from datetime import datetime


class MovimientoInventarioDAO:
    """
    Data Access Object para la gestión de movimientos de inventario
    """
    
    def __init__(self):
        """Constructor que inicializa la conexión a Supabase"""
        self.supabase = get_supabase_client()
        self.tabla = TABLA_MOVIMIENTO_INVENTARIO
    
    def crear(self, movimiento):
        """
        Registra un nuevo movimiento de inventario
        
        Args:
            movimiento: Objeto MovimientoInventario
            
        Returns:
            Objeto MovimientoInventario creado o None si hay error
        """
        try:
            datos = {
                'id_inventario': movimiento.id_inventario,
                'tipo': movimiento.tipo,
                'cantidad': int(movimiento.cantidad),
                'motivo': movimiento.motivo,
                'fecha': movimiento.fecha.isoformat() if isinstance(movimiento.fecha, datetime) else movimiento.fecha,
                'id_usuario': movimiento.id_usuario
            }
            
            response = self.supabase.table(self.tabla)\
                .insert(datos)\
                .execute()
            
            if response.data:
                return MovimientoInventario.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al crear movimiento: {e}")
            return None
    
    def obtener_por_id(self, id_movimiento):
        """
        Obtiene un movimiento por ID
        
        Args:
            id_movimiento: ID del movimiento
            
        Returns:
            Objeto MovimientoInventario o None si no existe
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('id_movimiento', id_movimiento)\
                .execute()
            
            if response.data:
                return MovimientoInventario.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al obtener movimiento: {e}")
            return None
    
    def listar_por_inventario(self, id_inventario, limite=100):
        """
        Lista movimientos de un registro de inventario específico
        
        Args:
            id_inventario: ID del inventario
            limite: Número máximo de movimientos a retornar
            
        Returns:
            Lista de objetos MovimientoInventario
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('id_inventario', id_inventario)\
                .order('fecha', desc=True)\
                .limit(limite)\
                .execute()
            
            movimientos = []
            if response.data:
                for mov_data in response.data:
                    movimientos.append(MovimientoInventario.from_dict(mov_data))
            
            return movimientos
            
        except Exception as e:
            print(f"Error al listar movimientos por inventario: {e}")
            return []
    
    def listar_por_sede(self, id_sede, tipo=None, fecha_desde=None, fecha_hasta=None, limite=100):
        """
        Lista movimientos de una sede con filtros opcionales
        
        Args:
            id_sede: ID de la sede
            tipo: 'entrada' o 'salida' (opcional)
            fecha_desde: Fecha inicio (opcional)
            fecha_hasta: Fecha fin (opcional)
            limite: Número máximo de movimientos
            
        Returns:
            Lista de objetos MovimientoInventario
        """
        try:
            query = self.supabase.table(self.tabla)\
                .select("*, inventario!inner(id_sede, insumo(nombre))")
            
            # Filtrar por sede usando el JOIN con inventario
            query = query.eq('inventario.id_sede', id_sede)
            
            if tipo:
                query = query.eq('tipo', tipo)
            
            if fecha_desde:
                query = query.gte('fecha', fecha_desde)
            
            if fecha_hasta:
                query = query.lte('fecha', fecha_hasta)
            
            response = query.order('fecha', desc=True).limit(limite).execute()
            
            movimientos = []
            if response.data:
                for mov_data in response.data:
                    movimiento = MovimientoInventario.from_dict(mov_data)
                    # Agregar información del insumo si existe
                    if 'inventario' in mov_data and mov_data['inventario']:
                        if 'insumo' in mov_data['inventario'] and mov_data['inventario']['insumo']:
                            movimiento.nombre_insumo = mov_data['inventario']['insumo'].get('nombre')
                    movimientos.append(movimiento)
            
            return movimientos
            
        except Exception as e:
            print(f"Error al listar movimientos por sede: {e}")
            return []
    
    def listar_por_tipo(self, tipo, limite=100):
        """
        Lista movimientos por tipo (entrada/salida)
        
        Args:
            tipo: 'entrada' o 'salida'
            limite: Número máximo de movimientos
            
        Returns:
            Lista de objetos MovimientoInventario
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('tipo', tipo)\
                .order('fecha', desc=True)\
                .limit(limite)\
                .execute()
            
            movimientos = []
            if response.data:
                for mov_data in response.data:
                    movimientos.append(MovimientoInventario.from_dict(mov_data))
            
            return movimientos
            
        except Exception as e:
            print(f"Error al listar movimientos por tipo: {e}")
            return []
    
    def listar_todos(self, limite=100):
        """
        Lista todos los movimientos
        
        Args:
            limite: Número máximo de movimientos
            
        Returns:
            Lista de objetos MovimientoInventario
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*, inventario(id_sede, id_insumo, insumo(nombre), sede(nombre))")\
                .order('fecha', desc=True)\
                .limit(limite)\
                .execute()
            
            movimientos = []
            if response.data:
                for mov_data in response.data:
                    movimiento = MovimientoInventario.from_dict(mov_data)
                    # Agregar información adicional
                    if 'inventario' in mov_data and mov_data['inventario']:
                        if 'insumo' in mov_data['inventario'] and mov_data['inventario']['insumo']:
                            movimiento.nombre_insumo = mov_data['inventario']['insumo'].get('nombre')
                        if 'sede' in mov_data['inventario'] and mov_data['inventario']['sede']:
                            movimiento.nombre_sede = mov_data['inventario']['sede'].get('nombre')
                    movimientos.append(movimiento)
            
            return movimientos
            
        except Exception as e:
            print(f"Error al listar todos los movimientos: {e}")
            return []