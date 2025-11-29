#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client, TABLA_RECLAMO
from entidades.reclamo import Reclamo

class ReclamoDAO:
    """
    Data Access Object para la gestión de reclamos
    """
    def __init__(self):
        """Constructor que inicializa la conexión a Supabase"""
        self.supabase = get_supabase_client()
        self.tabla = TABLA_RECLAMO
    
    def insertar(self, reclamo_data):
        """
        Inserta un nuevo reclamo
        
        Args:
            reclamo_data: dict con los datos del reclamo
            
        Returns:
            Objeto Reclamo creado o None si falla
        """
        try:
            response = self.supabase.table(self.tabla)\
                .insert(reclamo_data)\
                .execute()
            
            if response.data:
                return Reclamo.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al insertar reclamo: {e}")
            return None
    
    def obtener_por_id(self, id_reclamo):
        """
        Obtiene un reclamo por su ID
        
        Args:
            id_reclamo: ID del reclamo
            
        Returns:
            Objeto Reclamo o None si no existe
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('id_reclamo', id_reclamo)\
                .execute()
            
            if response.data:
                return Reclamo.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al obtener reclamo: {e}")
            return None
    
    def listar_por_cliente(self, id_cliente):
        """
        Lista todos los reclamos de un cliente
        
        Args:
            id_cliente: ID del cliente
            
        Returns:
            Lista de objetos Reclamo
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('id_cliente', id_cliente)\
                .order('fecha', desc=True)\
                .execute()
            
            if response.data:
                return [Reclamo.from_dict(r) for r in response.data]
            return []
            
        except Exception as e:
            print(f"Error al listar reclamos del cliente: {e}")
            return []
    
    def listar_por_pedido(self, id_pedido):
        """
        Lista todos los reclamos de un pedido
        
        Args:
            id_pedido: ID del pedido
            
        Returns:
            Lista de objetos Reclamo
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('id_pedido', id_pedido)\
                .order('fecha', desc=True)\
                .execute()
            
            if response.data:
                return [Reclamo.from_dict(r) for r in response.data]
            return []
            
        except Exception as e:
            print(f"Error al listar reclamos del pedido: {e}")
            return []
    
    def listar_por_estado(self, estado):
        """
        Lista todos los reclamos con un estado específico
        
        Args:
            estado: Estado del reclamo (abierto, en_revision, resuelto, cerrado)
            
        Returns:
            Lista de objetos Reclamo
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('estado', estado)\
                .order('fecha', desc=True)\
                .execute()
            
            if response.data:
                return [Reclamo.from_dict(r) for r in response.data]
            return []
            
        except Exception as e:
            print(f"Error al listar reclamos por estado: {e}")
            return []
    
    def listar_todos(self, limite=100):
        """
        Lista todos los reclamos con límite opcional
        
        Args:
            limite: Número máximo de reclamos a retornar
            
        Returns:
            Lista de objetos Reclamo
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .order('fecha', desc=True)\
                .limit(limite)\
                .execute()
            
            if response.data:
                return [Reclamo.from_dict(r) for r in response.data]
            return []
            
        except Exception as e:
            print(f"Error al listar todos los reclamos: {e}")
            return []
    
    def actualizar(self, id_reclamo, datos):
        """
        Actualiza un reclamo existente
        
        Args:
            id_reclamo: ID del reclamo a actualizar
            datos: dict con los campos a actualizar
            
        Returns:
            Objeto Reclamo actualizado o None si falla
        """
        try:
            response = self.supabase.table(self.tabla)\
                .update(datos)\
                .eq('id_reclamo', id_reclamo)\
                .execute()
            
            if response.data:
                return Reclamo.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al actualizar reclamo: {e}")
            return None
    
    def cambiar_estado(self, id_reclamo, nuevo_estado, fecha_resolucion=None):
        """
        Cambia el estado de un reclamo
        
        Args:
            id_reclamo: ID del reclamo
            nuevo_estado: Nuevo estado del reclamo
            fecha_resolucion: Fecha de resolución (opcional)
            
        Returns:
            Objeto Reclamo actualizado o None si falla
        """
        try:
            datos = {'estado': nuevo_estado}
            if fecha_resolucion:
                datos['fecha_resolucion'] = fecha_resolucion
            
            response = self.supabase.table(self.tabla)\
                .update(datos)\
                .eq('id_reclamo', id_reclamo)\
                .execute()
            
            if response.data:
                return Reclamo.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al cambiar estado del reclamo: {e}")
            return None

    # Métodos alias para compatibilidad con pruebas existentes
    def crear(self, reclamo: Reclamo):
        """
        Alias de crear que acepta una entidad Reclamo y delega en insertar.
        """
        try:
            data = reclamo.to_dict() if hasattr(reclamo, 'to_dict') else reclamo
            # Asegurar autogeneración del id
            if data.get('id_reclamo') is None:
                data.pop('id_reclamo', None)
            return self.supabase.table(self.tabla).insert(data).execute()
        except Exception as e:
            print(f"Error al crear reclamo: {e}")
            raise

    def actualizar_estado(self, id_reclamo, nuevo_estado, respuesta=None):
        """
        Alias que actualiza estado y opcionalmente la respuesta del reclamo.
        Retorna la respuesta cruda de Supabase para compatibilidad con tests.
        """
        try:
            # En el esquema actual no existe columna 'respuesta'; ignoramos ese parámetro
            datos = {'estado': nuevo_estado}
            return self.supabase.table(self.tabla)\
                .update(datos)\
                .eq('id_reclamo', id_reclamo)\
                .execute()
        except Exception as e:
            print(f"Error al actualizar estado del reclamo: {e}")
            raise