#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client, TABLA_PRODUCTO
from entidades.producto import Producto


class ProductoDAO:
    """
    Data Access Object para la gestión de productos
    """
    
    def __init__(self):
        """Constructor que inicializa la conexión a Supabase"""
        self.supabase = get_supabase_client()
        self.tabla = TABLA_PRODUCTO
    
    def insertar(self, producto):
        """
        Inserta un nuevo producto en la base de datos
        
        Args:
            producto: Objeto Producto con los datos a insertar
            
        Returns:
            Objeto Producto con el ID asignado o None si hay error
        """
        try:
            datos = {
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'id_unidad': producto.id_unidad,
                'contenido': producto.contenido,
                'precio': float(producto.precio),
                'stock': int(producto.stock),
                'activo': producto.activo
            }
            
            response = self.supabase.table(self.tabla)\
                .insert(datos)\
                .execute()
            
            if response.data:
                return Producto.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al insertar producto: {e}")
            return None
    
    def obtener_por_id(self, id_producto):
        """
        Obtiene un producto por su ID
        
        Args:
            id_producto: ID del producto
            
        Returns:
            Objeto Producto o None si no existe
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*, unidad_medida(nombre, abreviatura)")\
                .eq('id_producto', id_producto)\
                .execute()
            
            if response.data:
                producto = Producto.from_dict(response.data[0])
                # Agregar información de la unidad de medida si existe
                if 'unidad_medida' in response.data[0] and response.data[0]['unidad_medida']:
                    producto.nombre_unidad = response.data[0]['unidad_medida'].get('nombre')
                    producto.abreviatura_unidad = response.data[0]['unidad_medida'].get('abreviatura')
                return producto
            
            return None
            
        except Exception as e:
            print(f"Error al obtener producto: {e}")
            return None
    
    def obtener_por_codigo(self, codigo):
        """
        Obtiene un producto por su código
        
        Args:
            codigo: Código del producto
            
        Returns:
            Objeto Producto o None si no existe
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('codigo', codigo)\
                .execute()
            
            if response.data:
                return Producto.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al obtener producto por código: {e}")
            return None
    
    def listar_todos(self, limite=100):
        """
        Lista todos los productos con límite opcional
        
        Args:
            limite: Número máximo de productos a retornar
            
        Returns:
            Lista de objetos Producto
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*, unidad_medida(nombre, abreviatura)")\
                .order('nombre')\
                .limit(limite)\
                .execute()
            
            productos = []
            if response.data:
                for producto_data in response.data:
                    producto = Producto.from_dict(producto_data)
                    if 'unidad_medida' in producto_data and producto_data['unidad_medida']:
                        producto.nombre_unidad = producto_data['unidad_medida'].get('nombre')
                        producto.abreviatura_unidad = producto_data['unidad_medida'].get('abreviatura')
                    productos.append(producto)
            
            return productos
            
        except Exception as e:
            print(f"Error al listar productos: {e}")
            return []
    
    def listar_activos(self):
        """
        Lista solo los productos activos
        
        Returns:
            Lista de objetos Producto activos
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*, unidad_medida(nombre, abreviatura)")\
                .eq('activo', True)\
                .order('nombre')\
                .execute()
            
            productos = []
            if response.data:
                for producto_data in response.data:
                    producto = Producto.from_dict(producto_data)
                    if 'unidad_medida' in producto_data and producto_data['unidad_medida']:
                        producto.nombre_unidad = producto_data['unidad_medida'].get('nombre')
                        producto.abreviatura_unidad = producto_data['unidad_medida'].get('abreviatura')
                    productos.append(producto)
            
            return productos
            
        except Exception as e:
            print(f"Error al listar productos activos: {e}")
            return []
    
    def buscar_por_nombre(self, termino):
        """
        Busca productos por nombre (búsqueda parcial)
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            Lista de objetos Producto que coinciden
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .ilike('nombre', f'%{termino}%')\
                .order('nombre')\
                .execute()
            
            productos = []
            if response.data:
                for producto_data in response.data:
                    productos.append(Producto.from_dict(producto_data))
            
            return productos
            
        except Exception as e:
            print(f"Error al buscar productos: {e}")
            return []
    
    def actualizar(self, id_producto, datos):
        """
        Actualiza los datos de un producto
        
        Args:
            id_producto: ID del producto a actualizar
            datos: Diccionario con los campos a actualizar
            
        Returns:
            Objeto Producto actualizado o None si hay error
        """
        try:
            # Filtrar solo los campos permitidos
            campos_permitidos = ['nombre', 'descripcion', 'id_unidad', 'contenido', 
                               'precio', 'stock', 'activo']
            datos_actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}
            
            # Convertir tipos si es necesario
            if 'precio' in datos_actualizacion:
                datos_actualizacion['precio'] = float(datos_actualizacion['precio'])
            if 'stock' in datos_actualizacion:
                datos_actualizacion['stock'] = int(datos_actualizacion['stock'])
            
            response = self.supabase.table(self.tabla)\
                .update(datos_actualizacion)\
                .eq('id_producto', id_producto)\
                .execute()
            
            if response.data:
                return Producto.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            return None
    
    def cambiar_estado(self, id_producto, activo):
        """
        Cambia el estado activo/inactivo de un producto
        
        Args:
            id_producto: ID del producto
            activo: True para activar, False para desactivar
            
        Returns:
            Objeto Producto actualizado o None si hay error
        """
        try:
            response = self.supabase.table(self.tabla)\
                .update({'activo': activo})\
                .eq('id_producto', id_producto)\
                .execute()
            
            if response.data:
                return Producto.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al cambiar estado del producto: {e}")
            return None
    
    def actualizar_stock(self, id_producto, cantidad, operacion='sumar'):
        """
        Actualiza el stock de un producto
        
        Args:
            id_producto: ID del producto
            cantidad: Cantidad a sumar o restar
            operacion: 'sumar' o 'restar'
            
        Returns:
            Objeto Producto actualizado o None si hay error
        """
        try:
            # Obtener stock actual
            producto = self.obtener_por_id(id_producto)
            if not producto:
                return None
            
            nuevo_stock = producto.stock
            if operacion == 'sumar':
                nuevo_stock += int(cantidad)
            elif operacion == 'restar':
                nuevo_stock -= int(cantidad)
                if nuevo_stock < 0:
                    nuevo_stock = 0
            
            response = self.supabase.table(self.tabla)\
                .update({'stock': nuevo_stock})\
                .eq('id_producto', id_producto)\
                .execute()
            
            if response.data:
                return Producto.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al actualizar stock: {e}")
            return None
    
    def listar_con_stock_bajo(self, stock_minimo=10):
        """
        Lista productos con stock menor al mínimo especificado
        
        Args:
            stock_minimo: Umbral de stock mínimo
            
        Returns:
            Lista de objetos Producto con stock bajo
        """
        try:
            response = self.supabase.table(self.tabla)\
                .select("*")\
                .eq('activo', True)\
                .lt('stock', stock_minimo)\
                .order('stock')\
                .execute()
            
            productos = []
            if response.data:
                for producto_data in response.data:
                    productos.append(Producto.from_dict(producto_data))
            
            return productos
            
        except Exception as e:
            print(f"Error al listar productos con stock bajo: {e}")
            return []
