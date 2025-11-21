#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client, TABLA_PROVEEDOR
from entidades.proveedor import Proveedor

class ProveedorDAO:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.tabla = TABLA_PROVEEDOR

    def insertar(self, proveedor):
        """
        Inserta un nuevo proveedor en la base de datos
        
        Args:
            proveedor: Objeto Proveedor a insertar
            
        Returns:
            Proveedor con el ID asignado o None si hay error
        """
        try:
            # Preparar datos para inserción (sin el ID)
            datos = {
                'nombre': proveedor.nombre,
                'telefono': proveedor.telefono,
                'email': proveedor.email,
                'direccion': proveedor.direccion,
                'activo': proveedor.activo
            }
            
            # Insertar en Supabase
            response = self.supabase.table(self.tabla).insert(datos).execute()
            
            if response.data:
                # Retornar el proveedor con el ID asignado
                return Proveedor.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al insertar proveedor: {e}")
            return None

    def actualizar(self, id_proveedor, datos):
        """
        Actualiza un proveedor existente
        
        Args:
            id_proveedor: ID del proveedor a actualizar
            datos: Diccionario con los campos a actualizar
            
        Returns:
            Proveedor actualizado o None si hay error
        """
        try:
            # Filtrar solo los campos permitidos
            campos_validos = ['nombre', 'telefono', 'email', 'direccion', 'activo']
            datos_actualizacion = {k: v for k, v in datos.items() if k in campos_validos}
            
            # Actualizar en Supabase
            response = self.supabase.table(self.tabla)\
                .update(datos_actualizacion)\
                .eq('id_proveedor', id_proveedor)\
                .execute()
            
            if response.data:
                return Proveedor.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al actualizar proveedor: {e}")
            return None

    def obtener_por_id(self, id_proveedor):
        """
        Obtiene un proveedor por su ID
        
        Args:
            id_proveedor: ID del proveedor
            
        Returns:
            Objeto Proveedor o None si no existe
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('id_proveedor', id_proveedor)\
                .execute()
            
            if response.data:
                return Proveedor.from_dict(response.data[0])
            return None
            
        except Exception as e:
            print(f"Error al obtener proveedor: {e}")
            return None

    def listar_todos(self, solo_activos=True):
        """
        Lista todos los proveedores
        
        Args:
            solo_activos: Si es True, solo retorna proveedores activos
            
        Returns:
            Lista de objetos Proveedor
        """
        try:
            query = self.supabase.table(self.tabla).select("*")
            
            if solo_activos:
                query = query.eq('activo', True)
            
            response = query.execute()
            
            if response.data:
                return [Proveedor.from_dict(p) for p in response.data]
            return []
            
        except Exception as e:
            print(f"Error al listar proveedores: {e}")
            return []

    def eliminar_logico(self, id_proveedor):
        """
        Desactiva un proveedor (eliminación lógica)
        
        Args:
            id_proveedor: ID del proveedor a desactivar
            
        Returns:
            True si se desactivó correctamente, False en caso contrario
        """
        try:
            response = self.supabase.table(self.tabla)\
                .update({'activo': False})\
                .eq('id_proveedor', id_proveedor)\
                .execute()
            
            return response.data is not None and len(response.data) > 0
            
        except Exception as e:
            print(f"Error al desactivar proveedor: {e}")
            return False

    def buscar_por_nombre(self, nombre):
        """
        Busca proveedores por nombre (búsqueda parcial)
        
        Args:
            nombre: Texto a buscar en el nombre
            
        Returns:
            Lista de objetos Proveedor que coinciden
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .ilike('nombre', f'%{nombre}%')\
                .eq('activo', True)\
                .execute()
            
            if response.data:
                return [Proveedor.from_dict(p) for p in response.data]
            return []
            
        except Exception as e:
            print(f"Error al buscar proveedores: {e}")
            return []

    def existe_email(self, email, excluir_id=None):
        """
        Verifica si ya existe un proveedor con el email dado
        
        Args:
            email: Email a verificar
            excluir_id: ID de proveedor a excluir de la búsqueda (útil para actualizaciones)
            
        Returns:
            True si existe, False si no
        """
        try:
            query = self.supabase.table(self.tabla)\
                .select("id_proveedor")\
                .eq('email', email)
            
            if excluir_id:
                query = query.neq('id_proveedor', excluir_id)
            
            response = query.execute()
            
            return response.data is not None and len(response.data) > 0
            
        except Exception as e:
            print(f"Error al verificar email: {e}")
            return False