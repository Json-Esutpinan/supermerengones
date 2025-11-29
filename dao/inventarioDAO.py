#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client, TABLA_INVENTARIO
from entidades.inventario import Inventario


class InventarioDAO:
    """
    Data Access Object para la gestión de inventario
    """
    
    def __init__(self):
        """Constructor que inicializa la conexión a Supabase"""
        self.supabase = get_supabase_client()
        self.tabla = TABLA_INVENTARIO
    
    def obtener_por_id(self, id_inventario):
        """
        Obtiene un registro de inventario por ID
        
        Args:
            id_inventario: ID del inventario
            
        Returns:
            Objeto Inventario o None si no existe
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('id_inventario', id_inventario)\
                .execute()
            
            if response.data:
                return Inventario.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al obtener inventario: {e}")
            return None
    
    def obtener_por_insumo_y_sede(self, id_insumo, id_sede):
        """
        Obtiene el inventario de un insumo específico en una sede
        
        Args:
            id_insumo: ID del insumo
            id_sede: ID de la sede
            
        Returns:
            Objeto Inventario o None si no existe
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('id_insumo', id_insumo)\
                .eq('id_sede', id_sede)\
                .execute()
            
            if response.data:
                return Inventario.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al obtener inventario por insumo y sede: {e}")
            return None
    
    def listar_por_sede(self, id_sede):
        """
        Lista todo el inventario de una sede específica
        
        Args:
            id_sede: ID de la sede
            
        Returns:
            Lista de objetos Inventario
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*, insumo(nombre, unidad_medida(nombre, abreviatura))")\
                .eq('id_sede', id_sede)\
                .order('id_insumo')\
                .execute()
            
            inventarios = []
            if response.data:
                for inv_data in response.data:
                    inventario = Inventario.from_dict(inv_data)
                    # Agregar información del insumo si existe
                    if 'insumo' in inv_data and inv_data['insumo']:
                        inventario.nombre_insumo = inv_data['insumo'].get('nombre')
                        if 'unidad_medida' in inv_data['insumo'] and inv_data['insumo']['unidad_medida']:
                            inventario.nombre_unidad = inv_data['insumo']['unidad_medida'].get('nombre')
                            inventario.abreviatura_unidad = inv_data['insumo']['unidad_medida'].get('abreviatura')
                    inventarios.append(inventario)
            
            return inventarios
            
        except Exception as e:
            print(f"Error al listar inventario por sede: {e}")
            return []
    
    def listar_por_insumo(self, id_insumo):
        """
        Lista el inventario de un insumo en todas las sedes
        
        Args:
            id_insumo: ID del insumo
            
        Returns:
            Lista de objetos Inventario
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*, sede(nombre)")\
                .eq('id_insumo', id_insumo)\
                .order('id_sede')\
                .execute()
            
            inventarios = []
            if response.data:
                for inv_data in response.data:
                    inventario = Inventario.from_dict(inv_data)
                    if 'sede' in inv_data and inv_data['sede']:
                        inventario.nombre_sede = inv_data['sede'].get('nombre')
                    inventarios.append(inventario)
            
            return inventarios
            
        except Exception as e:
            print(f"Error al listar inventario por insumo: {e}")
            return []
    
    def listar_stock_bajo(self, id_sede=None, cantidad_minima=10):
        """
        Lista inventario con stock bajo
        
        Args:
            id_sede: ID de la sede (opcional, None para todas)
            cantidad_minima: Umbral de cantidad mínima
            
        Returns:
            Lista de objetos Inventario con stock bajo
        """
        try:
            query = self.supabase.table(self.tabla)\
                .select("*, insumo(nombre), sede(nombre)")\
                .lt('cantidad', cantidad_minima)
            
            if id_sede:
                query = query.eq('id_sede', id_sede)
            
            response = query.order('cantidad').execute()
            
            inventarios = []
            if response.data:
                for inv_data in response.data:
                    inventario = Inventario.from_dict(inv_data)
                    if 'insumo' in inv_data and inv_data['insumo']:
                        inventario.nombre_insumo = inv_data['insumo'].get('nombre')
                    if 'sede' in inv_data and inv_data['sede']:
                        inventario.nombre_sede = inv_data['sede'].get('nombre')
                    inventarios.append(inventario)
            
            return inventarios
            
        except Exception as e:
            print(f"Error al listar stock bajo: {e}")
            return []
    
    def crear(self, inventario):
        """
        Crea un nuevo registro de inventario
        
        Args:
            inventario: Objeto Inventario
            
        Returns:
            Objeto Inventario creado o None si hay error
        """
        try:
            datos = {
                'id_insumo': inventario.id_insumo,
                'id_sede': inventario.id_sede,
                'cantidad': int(inventario.cantidad)
            }
            
            response = self.supabase.table(self.tabla)\
                .insert(datos)\
                .execute()
            
            if response.data:
                return Inventario.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al crear inventario: {e}")
            return None
    
    def actualizar_cantidad(self, id_inventario, nueva_cantidad):
        """
        Actualiza la cantidad en inventario
        
        Args:
            id_inventario: ID del inventario
            nueva_cantidad: Nueva cantidad
            
        Returns:
            Objeto Inventario actualizado o None si hay error
        """
        try:
            response = self.supabase.table(self.tabla)\
                .update({'cantidad': int(nueva_cantidad)})\
                .eq('id_inventario', id_inventario)\
                .execute()
            
            if response.data:
                return Inventario.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al actualizar cantidad: {e}")
            return None
    
    def ajustar_cantidad(self, id_inventario, cantidad, operacion='sumar'):
        """
        Ajusta la cantidad sumando o restando
        
        Args:
            id_inventario: ID del inventario
            cantidad: Cantidad a ajustar
            operacion: 'sumar' o 'restar'
            
        Returns:
            Objeto Inventario actualizado o None si hay error
        """
        try:
            # Obtener cantidad actual
            inventario = self.obtener_por_id(id_inventario)
            if not inventario:
                return None
            
            nueva_cantidad = inventario.cantidad
            if operacion == 'sumar':
                nueva_cantidad += int(cantidad)
            elif operacion == 'restar':
                nueva_cantidad -= int(cantidad)
                if nueva_cantidad < 0:
                    nueva_cantidad = 0
            
            return self.actualizar_cantidad(id_inventario, nueva_cantidad)
            
        except Exception as e:
            print(f"Error al ajustar cantidad: {e}")
            return None
    
    def eliminar(self, id_inventario):
        """
        Elimina un registro de inventario
        
        Args:
            id_inventario: ID del inventario
            
        Returns:
            True si se eliminó, False si hay error
        """
        try:
            response = self.supabase.table(self.tabla)\
                .delete()\
                .eq('id_inventario', id_inventario)\
                .execute()
            
            return True
            
        except Exception as e:
            print(f"Error al eliminar inventario: {e}")
            return False