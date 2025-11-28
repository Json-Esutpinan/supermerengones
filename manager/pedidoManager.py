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
        """Crea un nuevo pedido para un cliente a partir de detalles.
        detalles: lista de dicts {'id_producto': int, 'cantidad': int}
        Returns dict with success, message, data (Pedido)
        """
        try:
            if not id_cliente:
                return {'success': False, 'message': 'Cliente inválido', 'data': None}
            if not detalles or not isinstance(detalles, list):
                return {'success': False, 'message': 'Detalles vacíos', 'data': None}
            pedido = self.dao.crear_pedido(id_cliente, detalles)
            if not pedido:
                return {'success': False, 'message': 'No fue posible crear el pedido', 'data': None}
            return {'success': True, 'message': 'Pedido creado correctamente', 'data': pedido}
        except Exception as e:
            return {'success': False, 'message': f'Error al crear pedido: {str(e)}', 'data': None}

    def actualizarEstado(self, id_pedido, nuevo_estado, id_empleado=None):
        """
        Actualiza el estado de un pedido con validaciones (HU20)
        
        Args:
            id_pedido: ID del pedido a actualizar
            nuevo_estado: Nuevo estado del pedido
            id_empleado: ID del empleado que realiza el cambio (opcional)
            
        Returns:
            dict con 'success', 'message' y 'data' (pedido actualizado)
        """
        try:
            # Validar que el estado sea válido
            estados_validos = ['pendiente', 'en_proceso', 'completado', 'cancelado']
            if nuevo_estado not in estados_validos:
                return {
                    'success': False,
                    'message': f'Estado inválido. Estados permitidos: {", ".join(estados_validos)}',
                    'data': None
                }
            
            # Verificar que el pedido existe
            pedido_actual = self.dao.obtener_por_id(id_pedido)
            if not pedido_actual:
                return {
                    'success': False,
                    'message': 'Pedido no encontrado',
                    'data': None
                }
            
            # Validar transiciones de estado permitidas
            transiciones_validas = {
                'pendiente': ['en_proceso', 'cancelado'],
                'en_proceso': ['completado', 'cancelado'],
                'completado': [],  # No se puede cambiar desde completado
                'cancelado': []    # No se puede cambiar desde cancelado
            }
            
            estado_actual = pedido_actual.estado
            if nuevo_estado not in transiciones_validas.get(estado_actual, []):
                return {
                    'success': False,
                    'message': f'Transición de estado no permitida: {estado_actual} → {nuevo_estado}',
                    'data': None
                }
            
            # Actualizar el estado
            pedido_actualizado = self.dao.actualizar_estado(id_pedido, nuevo_estado)
            
            if not pedido_actualizado:
                return {
                    'success': False,
                    'message': 'Error al actualizar el estado del pedido',
                    'data': None
                }
            
            return {
                'success': True,
                'message': f'Estado del pedido actualizado de "{estado_actual}" a "{nuevo_estado}"',
                'data': pedido_actualizado
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al actualizar estado: {str(e)}',
                'data': None
            }

    def procesarPago(self, id_pedido, metodo_pago, transaccion_id=None):
        """
        Procesa el pago de un pedido (HU15 - Pago en Línea)
        
        Args:
            id_pedido: ID del pedido
            metodo_pago: Método de pago (efectivo, tarjeta, transferencia, yape, plin)
            transaccion_id: ID de transacción del procesador (opcional)
            
        Returns:
            dict con 'success', 'message' y 'data' (pedido actualizado)
        """
        try:
            # Validar que el pedido existe
            pedido = self.dao.obtener_por_id(id_pedido)
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido no encontrado',
                    'data': None
                }
            
            # Validar método de pago
            metodos_validos = ['efectivo', 'tarjeta', 'transferencia', 'yape', 'plin']
            if metodo_pago not in metodos_validos:
                return {
                    'success': False,
                    'message': f'Método de pago inválido. Métodos permitidos: {", ".join(metodos_validos)}',
                    'data': None
                }
            
            # Validar que el pedido no esté cancelado
            if pedido.estado == 'cancelado':
                return {
                    'success': False,
                    'message': 'No se puede procesar el pago de un pedido cancelado',
                    'data': None
                }
            
            # Validar que el pago no haya sido procesado ya
            if pedido.estado_pago == 'pagado':
                return {
                    'success': False,
                    'message': 'El pago de este pedido ya fue procesado',
                    'data': None
                }
            
            # Actualizar información de pago
            pedido_actualizado = self.dao.actualizar_pago(id_pedido, metodo_pago, 'pagado', transaccion_id)
            
            if not pedido_actualizado:
                return {
                    'success': False,
                    'message': 'Error al procesar el pago',
                    'data': None
                }
            
            return {
                'success': True,
                'message': f'Pago procesado exitosamente con {metodo_pago}',
                'data': pedido_actualizado
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al procesar pago: {str(e)}',
                'data': None
            }

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

