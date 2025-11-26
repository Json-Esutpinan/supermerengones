#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client, TABLA_INSUMO
from entidades.insumo import Insumo


class InsumoDAO:
    """
    Data Access Object para la gestión de insumos
    """
    
    def __init__(self):
        """Constructor que inicializa la conexión a Supabase"""
        self.supabase = get_supabase_client()
        self.tabla = TABLA_INSUMO
    
    def insertar(self, insumo_data):
        """
        Inserta un nuevo insumo
        
        Args:
            insumo_data: dict con los datos del insumo (debe incluir id_sede)
            
        Returns:
            Objeto Insumo creado o None si falla
        """
        try:
            response = self.supabase.table(self.tabla)\
                .insert(insumo_data)\
                .execute()
            
            if response.data:
                return Insumo.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al insertar insumo: {e}")
            return None
    
    def obtener_por_id(self, id_insumo):
        """
        Obtiene un insumo por su ID
        
        Args:
            id_insumo: ID del insumo
            
        Returns:
            Objeto Insumo o None si no existe
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*, sede(nombre), unidad_medida(nombre, abreviatura)")\
                .eq('id_insumo', id_insumo)\
                .execute()
            
            if response.data:
                return Insumo.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al obtener insumo: {e}")
            return None
    
    def listar_por_sede(self, id_sede, solo_activos=True):
        """
        Lista todos los insumos de una sede
        
        Args:
            id_sede: ID de la sede
            solo_activos: Si True, solo retorna insumos activos
            
        Returns:
            Lista de objetos Insumo
        """
        try:
            query = self.supabase.table(self.tabla)\
                .select("*, sede(nombre), unidad_medida(nombre, abreviatura)")\
                .eq('id_sede', id_sede)
            
            if solo_activos:
                query = query.eq('activo', True)
            
            response = query.order('nombre').execute()
            
            if response.data:
                return [Insumo.from_dict(i) for i in response.data]
            return []
            
        except Exception as e:
            print(f"Error al listar insumos por sede: {e}")
            return []
    
    def listar_todos(self, solo_activos=True):
        """
        Lista todos los insumos
        
        Args:
            solo_activos: Si True, solo retorna insumos activos
            
        Returns:
            Lista de objetos Insumo
        """
        try:
            query = self.supabase.table(self.tabla)\
                .select("*, sede(nombre), unidad_medida(nombre, abreviatura)")
            
            if solo_activos:
                query = query.eq('activo', True)
            
            response = query.order('nombre').execute()
            
            if response.data:
                return [Insumo.from_dict(i) for i in response.data]
            return []
            
        except Exception as e:
            print(f"Error al listar todos los insumos: {e}")
            return []
    
    def actualizar(self, id_insumo, datos):
        """
        Actualiza un insumo existente
        
        Args:
            id_insumo: ID del insumo a actualizar
            datos: dict con los campos a actualizar
            
        Returns:
            Objeto Insumo actualizado o None si falla
        """
        try:
            response = self.supabase.table(self.tabla)\
                .update(datos)\
                .eq('id_insumo', id_insumo)\
                .execute()
            
            if response.data:
                return Insumo.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al actualizar insumo: {e}")
            return None
    
    def cambiar_estado(self, id_insumo, activo):
        """
        Cambia el estado de un insumo (activo/inactivo)
        
        Args:
            id_insumo: ID del insumo
            activo: True para activar, False para desactivar
            
        Returns:
            Objeto Insumo actualizado o None si falla
        """
        return self.actualizar(id_insumo, {'activo': activo})