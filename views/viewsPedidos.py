#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from manager.pedidoManager import PedidoManager

# Instancia del manager
pedido_manager = PedidoManager()


@api_view(['GET'])
def historial_pedidos_cliente(request, id_cliente):
    """
    Obtiene el historial de pedidos de un cliente
    
    GET /api/pedidos/cliente/{id_cliente}/historial/
    Query params opcionales:
        - estado: filtrar por estado (pendiente, en_proceso, completado, cancelado)
        - fecha_inicio: filtrar desde fecha (YYYY-MM-DD)
        - fecha_fin: filtrar hasta fecha (YYYY-MM-DD)
    """
    try:
        # Obtener filtros de query params
        filtros = {}
        if request.GET.get('estado'):
            filtros['estado'] = request.GET.get('estado')
        if request.GET.get('fecha_inicio'):
            filtros['fecha_inicio'] = request.GET.get('fecha_inicio')
        if request.GET.get('fecha_fin'):
            filtros['fecha_fin'] = request.GET.get('fecha_fin')
        
        resultado = pedido_manager.obtenerHistorialCliente(id_cliente, filtros if filtros else None)
        
        if resultado['success']:
            pedidos_dict = [p.to_dict() for p in resultado['data']]
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': pedidos_dict
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': []
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_detalle_pedido(request, id_pedido):
    """
    Obtiene el detalle completo de un pedido
    
    GET /api/pedidos/{id_pedido}/
    """
    try:
        resultado = pedido_manager.obtenerDetallePedido(id_pedido)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado['data'] else None
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_pedidos_por_estado(request, estado):
    """
    Lista todos los pedidos con un estado específico
    
    GET /api/pedidos/estado/{estado}/
    """
    try:
        resultado = pedido_manager.listarPedidosPorEstado(estado)
        
        if resultado['success']:
            pedidos_dict = [p.to_dict() for p in resultado['data']]
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': pedidos_dict
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': []
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_pedidos_por_fecha(request):
    """
    Lista pedidos en un rango de fechas
    
    GET /api/pedidos/fecha/
    Query params requeridos:
        - fecha_inicio: fecha de inicio (YYYY-MM-DD)
        - fecha_fin: fecha de fin (YYYY-MM-DD)
    """
    try:
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return Response({
                'success': False,
                'message': 'Los parámetros fecha_inicio y fecha_fin son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = pedido_manager.listarPedidosPorFecha(fecha_inicio, fecha_fin)
        
        if resultado['success']:
            pedidos_dict = [p.to_dict() for p in resultado['data']]
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': pedidos_dict
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_todos_pedidos(request):
    """
    Lista todos los pedidos
    
    GET /api/pedidos/
    Query params opcionales:
        - limite: número máximo de pedidos a retornar (default: 100)
    """
    try:
        limite = int(request.GET.get('limite', 100))
        
        resultado = pedido_manager.listarTodosPedidos(limite)
        
        if resultado['success']:
            pedidos_dict = [p.to_dict() for p in resultado['data']]
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': pedidos_dict
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': []
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
def actualizar_estado_pedido(request, id_pedido):
    """
    Actualiza el estado de un pedido (HU20)
    
    PATCH /api/pedidos/{id_pedido}/estado/
    
    Body JSON:
    {
        "estado": "en_proceso",  // pendiente, en_proceso, completado, cancelado
        "id_empleado": 1         // (opcional) ID del empleado que actualiza
    }
    
    Transiciones permitidas:
    - pendiente → en_proceso, cancelado
    - en_proceso → completado, cancelado
    - completado → (ninguna)
    - cancelado → (ninguna)
    """
    try:
        # Obtener datos del body
        nuevo_estado = request.data.get('estado')
        id_empleado = request.data.get('id_empleado')
        
        if not nuevo_estado:
            return Response({
                'success': False,
                'message': 'El campo "estado" es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar el estado
        resultado = pedido_manager.actualizarEstado(id_pedido, nuevo_estado, id_empleado)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado['data'] else None
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
