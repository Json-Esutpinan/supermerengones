#!/usr/bin/python
# -*- coding: utf-8 -*-

from dao.pedidoDAO import PedidoDAO
from datetime import datetime


class PedidoManager:
    """
    Gestión de Pedidos - Especializado en historial de pedidos (HU17)
    """
    
    def __init__(self):
        self.dao = PedidoDAO()

    def obtenerHistorialCliente(self, id_cliente, filtros=None):
        """
        Obtiene el historial completo de pedidos de un cliente
        
        Args:
            id_cliente: ID del cliente
            filtros: dict opcional con filtros adicionales
                - estado: filtrar por estado específico
                - fecha_inicio: fecha de inicio (YYYY-MM-DD)
                - fecha_fin: fecha de fin (YYYY-MM-DD)
                
        Returns:
            dict con 'success', 'message' y 'data' (lista de pedidos)
        """
        try:
            # Obtener pedidos del cliente
            pedidos = self.dao.listar_por_cliente(id_cliente)
            
            # Aplicar filtros si existen
            if filtros:
                if 'estado' in filtros and filtros['estado']:
                    pedidos = [p for p in pedidos if p.estado == filtros['estado']]
                
                if 'fecha_inicio' in filtros and filtros['fecha_inicio']:
                    # Extraer solo la parte de fecha para comparar (YYYY-MM-DD)
                    pedidos = [p for p in pedidos if p.fecha and str(p.fecha)[:10] >= filtros['fecha_inicio']]
                
                if 'fecha_fin' in filtros and filtros['fecha_fin']:
                    # Extraer solo la parte de fecha para comparar (YYYY-MM-DD)
                    pedidos = [p for p in pedidos if p.fecha and str(p.fecha)[:10] <= filtros['fecha_fin']]
            
            return {
                'success': True,
                'message': f'Se encontraron {len(pedidos)} pedidos',
                'data': pedidos
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al obtener historial: {str(e)}',
                'data': []
            }
    
    def obtenerDetallePedido(self, id_pedido):
        """
        Obtiene el detalle completo de un pedido específico
        
        Args:
            id_pedido: ID del pedido
            
        Returns:
            dict con 'success', 'message' y 'data' (pedido con detalles)
        """
        try:
            pedido = self.dao.obtener_por_id(id_pedido)
            
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido no encontrado',
                    'data': None
                }
            
            return {
                'success': True,
                'message': 'Pedido encontrado',
                'data': pedido
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al obtener pedido: {str(e)}',
                'data': None
            }
    
    def listarPedidosPorEstado(self, estado):
        """
        Lista todos los pedidos con un estado específico
        
        Args:
            estado: Estado del pedido (pendiente, en_proceso, completado, cancelado)
            
        Returns:
            dict con 'success', 'message' y 'data' (lista de pedidos)
        """
        try:
            pedidos = self.dao.listar_por_estado(estado)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(pedidos)} pedidos con estado {estado}',
                'data': pedidos
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al listar pedidos: {str(e)}',
                'data': []
            }
    
    def listarPedidosPorFecha(self, fecha_inicio, fecha_fin):
        """
        Lista pedidos en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            
        Returns:
            dict con 'success', 'message' y 'data' (lista de pedidos)
        """
        try:
            # Validar formato de fechas
            try:
                datetime.fromisoformat(fecha_inicio)
                datetime.fromisoformat(fecha_fin)
            except ValueError:
                return {
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD',
                    'data': []
                }
            
            pedidos = self.dao.listar_por_fecha(fecha_inicio, fecha_fin)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(pedidos)} pedidos entre {fecha_inicio} y {fecha_fin}',
                'data': pedidos
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al listar pedidos por fecha: {str(e)}',
                'data': []
            }
    
    def listarTodosPedidos(self, limite=100):
        """
        Lista todos los pedidos con límite opcional
        
        Args:
            limite: Número máximo de pedidos a retornar
            
        Returns:
            dict con 'success', 'message' y 'data' (lista de pedidos)
        """
        try:
            pedidos = self.dao.listar_todos(limite)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(pedidos)} pedidos',
                'data': pedidos
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al listar pedidos: {str(e)}',
                'data': []
            }
    
    # Métodos pendientes de implementación (para otras HUs)
    def obtenerPersonalizacion(self):
        """
        TODO: Implementar en otra HU
        Devuelve productos y toppings disponibles
        """
        pass

    def crearPedido(self, id_cliente, detalles):
        """
        TODO: Implementar en otra HU
        Crea un nuevo pedido
        """
        pass

    def actualizarEstado(self, id_pedido, estado, id_empleado):
        """
        TODO: Implementar en otra HU
        Cambia el estado del pedido
        """
        pass

    def listarPedidoPorCliente(self, id_cliente):
        """
        Alias de obtenerHistorialCliente para compatibilidad
        """
        return self.obtenerHistorialCliente(id_cliente)

    def listarPedidoPorSede(self, id_sede, estado):
        """
        TODO: Implementar en otra HU
        Ver cola de pedidos por sede
        """
        pass

    def agregarReclamo(self, id_pedido, id_cliente, descripcion):
        """
        TODO: Implementar en otra HU
        Registrar reclamo
        """
        pass
