#!/usr/bin/python
# -*- coding: utf-8 -*-

class PedidoManager:
    """
    Gestión de Pedidos y Personalización. 
    Maneja todo el ciclo de vida de un pedido, desde que el cliente lo arma hasta que se entrega.
    """
    def __init__(self):
        pass

    def obtenerPersonalizacion(self, ):
        """Devuelve un diccionario con los Productos (bases, ej. "Merengón Grande") y los Insumos (toppings, ej. "Adición de Fresa") disponibles para que el cliente arme su pedido."""
        pass

    def crearPedido(self, id_cliente, deatlles):
        """
        Recibe el ID del cliente y una lista de diccionarios.
        [{'id_producto': 101, 'cantidad': 1}, {'id_producto': 103, 'cantidad': 1}].

        Debe crear el Pedido, crear los DetallePedido, y luego llamar a InventarioManager.descontarStockPorPedido(id_pedido) para descontar el insumo.
        """
        pass

    def actualizarEstado(self, id_pedido, estado, id_empleado):
        """Cambia el estado del pedido y hace una notificación al cliente."""
        pass

    def listarPedidoPorCliente(self, id_cliente):
        """Historial del cliente"""
        pass

    def listarPedidoPorSede(self, id_sede, estado):
        """
        Ver cola de pedidos. 
        Se pasa un estado por el que se quiere filtrar.
        """
        pass

    def obtenerDetallePedido(self, id_pedido):
        """Devuelve un pedido con toda su información y detalles."""
        pass

    def agregarReclamo(self, id_pedido, id_cliente, descripcion):
        """Permite al cliente registrar un reclamo sobre un pedido."""
        pass
