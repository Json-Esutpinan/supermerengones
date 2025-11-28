#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client, TABLA_PEDIDO, TABLA_DETALLE_PEDIDO
from entidades.pedido import Pedido
from entidades.detallePedido import DetallePedido


class PedidoDAO:
    """
    Data Access Object para la gestión de pedidos
    """
    
    def __init__(self):
        """Constructor que inicializa la conexión a Supabase"""
        self.supabase = get_supabase_client()
        self.tabla_pedido = TABLA_PEDIDO
        self.tabla_detalle = TABLA_DETALLE_PEDIDO
    
    def obtener_por_id(self, id_pedido):
        """
        Obtiene un pedido por su ID incluyendo sus detalles
        
        Args:
            id_pedido: ID del pedido
            
        Returns:
            Objeto Pedido con sus detalles o None si no existe
        """
        try:
            # Obtener pedido con información de sede (incluyendo campos de pago HU15)
            response = self.supabase.table(self.tabla_pedido)\
                .select("*, sede(nombre)")\
                .eq('id_pedido', id_pedido)\
                .execute()
            
            if not response.data:
                return None
            
            pedido = Pedido.from_dict(response.data[0])
            
            # Obtener detalles del pedido con información del producto (incluyendo personalizacion HU14)
            detalles_response = self.supabase.table(self.tabla_detalle)\
                .select("*, producto(nombre)")\
                .eq('id_pedido', id_pedido)\
                .execute()
            
            if detalles_response.data:
                for detalle_data in detalles_response.data:
                    detalle = DetallePedido.from_dict(detalle_data)
                    # Agregar nombre del producto si existe
                    if 'producto' in detalle_data and detalle_data['producto']:
                        detalle.nombre_producto = detalle_data['producto'].get('nombre')
                    pedido.detalles.append(detalle)
            
            return pedido
            
        except Exception as e:
            print(f"Error al obtener pedido: {e}")
            return None
    
    def listar_por_cliente(self, id_cliente):
        """
        Lista todos los pedidos de un cliente específico
        
        Args:
            id_cliente: ID del cliente
            
        Returns:
            Lista de objetos Pedido
        """
        try:
            response = self.supabase.table(self.tabla_pedido)\
                .select("*")\
                .eq('id_cliente', id_cliente)\
                .order('fecha', desc=True)\
                .execute()
            
            pedidos = []
            if response.data:
                for pedido_data in response.data:
                    pedido = Pedido.from_dict(pedido_data)
                    # Obtener detalles
                    pedido = self._cargar_detalles(pedido)
                    pedidos.append(pedido)
            
            return pedidos
            
        except Exception as e:
            print(f"Error al listar pedidos del cliente: {e}")
            return []
    
    def listar_por_estado(self, estado):
        """
        Lista todos los pedidos con un estado específico
        
        Args:
            estado: Estado del pedido (pendiente, en_proceso, completado, cancelado)
            
        Returns:
            Lista de objetos Pedido
        """
        try:
            response = self.supabase.table(self.tabla_pedido)\
                .select("*")\
                .eq('estado', estado)\
                .order('fecha', desc=True)\
                .execute()
            
            pedidos = []
            if response.data:
                for pedido_data in response.data:
                    pedido = Pedido.from_dict(pedido_data)
                    pedido = self._cargar_detalles(pedido)
                    pedidos.append(pedido)
            
            return pedidos
            
        except Exception as e:
            print(f"Error al listar pedidos por estado: {e}")
            return []
    
    def listar_por_fecha(self, fecha_inicio, fecha_fin):
        """
        Lista pedidos en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio (formato: YYYY-MM-DD)
            fecha_fin: Fecha de fin (formato: YYYY-MM-DD)
            
        Returns:
            Lista de objetos Pedido
        """
        try:
            response = self.supabase.table(self.tabla_pedido)\
                .select("*")\
                .gte('fecha', fecha_inicio)\
                .lte('fecha', fecha_fin)\
                .order('fecha', desc=True)\
                .execute()
            
            pedidos = []
            if response.data:
                for pedido_data in response.data:
                    pedido = Pedido.from_dict(pedido_data)
                    pedido = self._cargar_detalles(pedido)
                    pedidos.append(pedido)
            
            return pedidos
            
        except Exception as e:
            print(f"Error al listar pedidos por fecha: {e}")
            return []
    
    def listar_todos(self, limite=100):
        """
        Lista todos los pedidos con límite opcional
        
        Args:
            limite: Número máximo de pedidos a retornar
            
        Returns:
            Lista de objetos Pedido
        """
        try:
            response = self.supabase.table(self.tabla_pedido)\
                .select("*")\
                .order('fecha', desc=True)\
                .limit(limite)\
                .execute()
            
            pedidos = []
            if response.data:
                for pedido_data in response.data:
                    pedido = Pedido.from_dict(pedido_data)
                    pedido = self._cargar_detalles(pedido)
                    pedidos.append(pedido)
            
            return pedidos
            
        except Exception as e:
            print(f"Error al listar todos los pedidos: {e}")
            return []
    
    def actualizar_estado(self, id_pedido, nuevo_estado):
        """
        Actualiza el estado de un pedido
        
        Args:
            id_pedido: ID del pedido a actualizar
            nuevo_estado: Nuevo estado del pedido (pendiente, en_proceso, completado, cancelado)
            
        Returns:
            Objeto Pedido actualizado o None si hay error
        """
        try:
            response = self.supabase.table(self.tabla_pedido)\
                .update({'estado': nuevo_estado})\
                .eq('id_pedido', id_pedido)\
                .execute()
            
            if response.data:
                return Pedido.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al actualizar estado del pedido: {e}")
            return None
    
    def actualizar_pago(self, id_pedido, metodo_pago, estado_pago, transaccion_id=None):
        """
        Actualiza la información de pago de un pedido (HU15)
        
        Args:
            id_pedido: ID del pedido
            metodo_pago: Método de pago (efectivo, tarjeta, transferencia, etc.)
            estado_pago: Estado del pago (pendiente, pagado, fallido, reembolsado)
            transaccion_id: ID de la transacción (opcional)
            
        Returns:
            Objeto Pedido actualizado o None si hay error
        """
        try:
            from datetime import datetime
            
            datos_actualizacion = {
                'metodo_pago': metodo_pago,
                'estado_pago': estado_pago
            }
            
            if transaccion_id:
                datos_actualizacion['transaccion_id'] = transaccion_id
            
            # Si el pago es exitoso, registrar fecha de pago
            if estado_pago == 'pagado':
                datos_actualizacion['fecha_pago'] = datetime.now().isoformat()
            
            response = self.supabase.table(self.tabla_pedido)\
                .update(datos_actualizacion)\
                .eq('id_pedido', id_pedido)\
                .execute()
            
            if response.data:
                return Pedido.from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            print(f"Error al actualizar pago del pedido: {e}")
            return None
    
    def _cargar_detalles(self, pedido):
        """
        Carga los detalles de un pedido (método privado)
        Incluye personalización de productos (HU14)
        
        Args:
            pedido: Objeto Pedido
            
        Returns:
            Objeto Pedido con detalles cargados
        """
        try:
            response = self.supabase.table(self.tabla_detalle)\
                .select("*, producto(nombre)")\
                .eq('id_pedido', pedido.id_pedido)\
                .execute()
            
            if response.data:
                for detalle_data in response.data:
                    detalle = DetallePedido.from_dict(detalle_data)
                    if 'producto' in detalle_data and detalle_data['producto']:
                        detalle.nombre_producto = detalle_data['producto'].get('nombre')
                    pedido.detalles.append(detalle)
            
            return pedido
            
        except Exception as e:
            print(f"Error al cargar detalles del pedido: {e}")
            return pedido