#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from manager.reclamoManager import ReclamoManager
from datetime import datetime

manager = ReclamoManager()


@api_view(['GET'])
def listar_reclamos_cliente(request, id_cliente):
    """
    GET /api/reclamos/cliente/{id_cliente}/
    Lista todos los reclamos de un cliente
    """
    resultado = manager.listarReclamosCliente(id_cliente)
    
    if resultado['success']:
        return Response({
            'message': resultado['message'],
            'data': [r.to_dict() for r in resultado['data']]
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': resultado['message'],
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_reclamos_pedido(request, id_pedido):
    """
    GET /api/reclamos/pedido/{id_pedido}/
    Lista todos los reclamos de un pedido
    """
    resultado = manager.listarReclamosPedido(id_pedido)
    
    if resultado['success']:
        return Response({
            'message': resultado['message'],
            'data': [r.to_dict() for r in resultado['data']]
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': resultado['message'],
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_reclamo(request, id_reclamo):
    """
    GET /api/reclamos/{id_reclamo}/
    Obtiene el detalle de un reclamo específico
    """
    resultado = manager.obtenerReclamo(id_reclamo)
    
    if resultado['success']:
        return Response({
            'message': resultado['message'],
            'data': resultado['data'].to_dict()
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': resultado['message'],
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def listar_reclamos_por_estado(request):
    """
    GET /api/reclamos/estado/?estado=abierto
    Lista reclamos filtrados por estado
    Query params:
        - estado: abierto, en_revision, resuelto, cerrado
    """
    estado = request.GET.get('estado')
    
    if not estado:
        return Response({
            'message': 'Parámetro estado es requerido',
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)
    
    resultado = manager.listarReclamosPorEstado(estado)
    
    if resultado['success']:
        return Response({
            'message': resultado['message'],
            'data': [r.to_dict() for r in resultado['data']]
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': resultado['message'],
            'data': []
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_todos_reclamos(request):
    """
    GET /api/reclamos/
    Lista todos los reclamos
    Query params:
        - limite: número máximo de resultados (default: 100)
    """
    limite = request.GET.get('limite', 100)
    
    try:
        limite = int(limite)
    except ValueError:
        limite = 100
    
    resultado = manager.listarTodosReclamos(limite)
    
    if resultado['success']:
        return Response({
            'message': resultado['message'],
            'data': [r.to_dict() for r in resultado['data']]
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': resultado['message'],
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def crear_reclamo(request):
    """
    POST /api/reclamos/
    Crea un nuevo reclamo
    Body:
        {
            "id_pedido": 1,
            "id_cliente": 1,
            "descripcion": "Descripción del reclamo"
        }
    """
    id_pedido = request.data.get('id_pedido')
    id_cliente = request.data.get('id_cliente')
    descripcion = request.data.get('descripcion')
    
    if not all([id_pedido, id_cliente, descripcion]):
        return Response({
            'message': 'Faltan campos requeridos: id_pedido, id_cliente, descripcion',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    resultado = manager.crearReclamo(id_pedido, id_cliente, descripcion)
    
    if resultado['success']:
        return Response({
            'message': resultado['message'],
            'data': resultado['data'].to_dict()
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'message': resultado['message'],
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def cambiar_estado_reclamo(request, id_reclamo):
    """
    PATCH /api/reclamos/{id_reclamo}/estado/
    Cambia el estado de un reclamo
    Body:
        {
            "estado": "resuelto"
        }
    """
    nuevo_estado = request.data.get('estado')
    
    if not nuevo_estado:
        return Response({
            'message': 'Campo estado es requerido',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    resultado = manager.cambiarEstadoReclamo(id_reclamo, nuevo_estado)
    
    if resultado['success']:
        return Response({
            'message': resultado['message'],
            'data': resultado['data'].to_dict()
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': resultado['message'],
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def agregar_respuesta_reclamo(request, id_reclamo):
    """
    POST /api/reclamos/{id_reclamo}/respuesta/
    Agrega una respuesta al reclamo
    Body:
        {
            "respuesta": "Texto de la respuesta"
        }
    """
    respuesta = request.data.get('respuesta')
    
    if not respuesta:
        return Response({
            'message': 'Campo respuesta es requerido',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    resultado = manager.agregarRespuesta(id_reclamo, respuesta)
    
    if resultado['success']:
        return Response({
            'message': resultado['message'],
            'data': resultado['data'].to_dict()
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': resultado['message'],
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def resolver_reclamo(request, id_reclamo):
    """
    POST /api/reclamos/{id_reclamo}/resolver/
    Marca el reclamo como resuelto, con respuesta opcional.
    Body opcional:
        {
            "respuesta": "Texto de la respuesta"
        }
    """
    respuesta = request.data.get('respuesta')

    resultado = manager.resolver_reclamo(id_reclamo, respuesta)

    if resultado.get('success'):
        return Response({
            'success': True,
            'message': resultado.get('message'),
            'data': resultado.get('data').to_dict() if resultado.get('data') else None
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': resultado.get('message'),
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def rechazar_reclamo(request, id_reclamo):
    """
    POST /api/reclamos/{id_reclamo}/rechazar/
    Marca el reclamo como rechazado, con razón opcional.
    Body opcional:
        {
            "razon": "Texto de la razón"
        }
    """
    razon = request.data.get('razon')

    resultado = manager.rechazar_reclamo(id_reclamo, razon)

    if resultado.get('success'):
        return Response({
            'success': True,
            'message': resultado.get('message'),
            'data': resultado.get('data').to_dict() if resultado.get('data') else None
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': resultado.get('message'),
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def obtener_estadisticas_reclamos(request):
    """
    GET /api/reclamos/estadisticas/
    Devuelve estadísticas agregadas de reclamos: total y conteos por estado.
    """
    stats = manager.obtener_estadisticas()

    success = 'error' not in stats
    return Response({
        'success': success,
        'message': 'Estadísticas obtenidas' if success else f"Error: {stats.get('error')}",
        'data': {
            'total': stats.get('total', 0),
            'por_estado': stats.get('por_estado', {}),
            'por_tipo': stats.get('por_tipo', {})
        }
    }, status=status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR)
