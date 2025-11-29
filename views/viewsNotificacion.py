#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from manager.notificacionManager import NotificacionManager

logger = logging.getLogger(__name__)
notificacion_manager = NotificacionManager()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_notificacion(request):
    """
    Crea una nueva notificación para un cliente (solo administradores)
    POST /api/notificaciones/crear/
    Body: {
        "id_cliente": 1,
        "mensaje": "Tu pedido está en camino"
    }
    """
    try:
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para crear notificaciones"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        id_cliente = request.data.get('id_cliente')
        mensaje = request.data.get('mensaje')
        
        result = notificacion_manager.crearNotificacion(id_cliente, mensaje)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al crear notificación: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al crear notificación: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enviar_notificacion_masiva(request):
    """
    Envía la misma notificación a múltiples clientes (solo administradores)
    POST /api/notificaciones/masiva/
    Body: {
        "clientes": [1, 2, 3, 4],
        "mensaje": "Tenemos nuevas promociones disponibles"
    }
    """
    try:
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para enviar notificaciones masivas"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        lista_clientes = request.data.get('clientes', [])
        mensaje = request.data.get('mensaje')
        
        result = notificacion_manager.enviarNotificacionMasiva(lista_clientes, mensaje)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al enviar notificaciones masivas: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al enviar notificaciones masivas: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_notificaciones_cliente(request):
    """
    Lista notificaciones del cliente autenticado
    GET /api/notificaciones/mis-notificaciones/?no_leidas=true&limite=50
    - Clientes solo ven sus propias notificaciones
    - Parámetros opcionales: no_leidas (true/false), limite (número)
    """
    try:
        # Solo clientes pueden ver sus notificaciones
        if not hasattr(request.user, 'cliente'):
            return Response(
                {"success": False, "message": "Solo clientes pueden ver notificaciones"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        id_cliente = request.user.cliente.id_cliente
        solo_no_leidas = request.query_params.get('no_leidas', 'false').lower() == 'true'
        limite = int(request.query_params.get('limite', 50))
        
        result = notificacion_manager.listarPorCliente(id_cliente, solo_no_leidas, limite)
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al listar notificaciones del cliente: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al listar notificaciones: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contar_no_leidas(request):
    """
    Cuenta notificaciones no leídas del cliente autenticado
    GET /api/notificaciones/no-leidas/count/
    """
    try:
        if not hasattr(request.user, 'cliente'):
            return Response(
                {"success": False, "message": "Solo clientes pueden ver notificaciones"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        id_cliente = request.user.cliente.id_cliente
        result = notificacion_manager.contarNoLeidas(id_cliente)
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al contar notificaciones: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al contar notificaciones: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_notificacion(request, id_notificacion):
    """
    Obtiene una notificación específica
    GET /api/notificaciones/{id_notificacion}/
    - Clientes solo pueden ver sus propias notificaciones
    - Administradores pueden ver cualquier notificación
    """
    try:
        result = notificacion_manager.obtenerNotificacion(id_notificacion)
        
        if not result['success']:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar permisos
        notificacion = result['data']
        es_admin = hasattr(request.user, 'administrador')
        es_cliente_propietario = False
        
        if hasattr(request.user, 'cliente'):
            es_cliente_propietario = (request.user.cliente.id_cliente == notificacion['id_cliente'])
        
        if not es_admin and not es_cliente_propietario:
            return Response(
                {"success": False, "message": "No tienes permisos para ver esta notificación"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al obtener notificación: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al obtener notificación: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def marcar_como_leida(request, id_notificacion):
    """
    Marca una notificación como leída
    PATCH /api/notificaciones/{id_notificacion}/leer/
    - Clientes solo pueden marcar sus propias notificaciones
    """
    try:
        # Verificar que la notificación existe y pertenece al cliente
        resp_notif = notificacion_manager.obtenerNotificacion(id_notificacion)
        
        if not resp_notif['success']:
            return Response(resp_notif, status=status.HTTP_404_NOT_FOUND)
        
        notificacion = resp_notif['data']
        
        # Verificar permisos
        if hasattr(request.user, 'cliente'):
            if request.user.cliente.id_cliente != notificacion['id_cliente']:
                return Response(
                    {"success": False, "message": "No tienes permisos para modificar esta notificación"},
                    status=status.HTTP_403_FORBIDDEN
                )
        elif not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para modificar notificaciones"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result = notificacion_manager.marcarComoLeida(id_notificacion)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al marcar notificación como leída: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al marcar como leída: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_todas_leidas(request):
    """
    Marca todas las notificaciones del cliente como leídas
    POST /api/notificaciones/leer-todas/
    """
    try:
        if not hasattr(request.user, 'cliente'):
            return Response(
                {"success": False, "message": "Solo clientes pueden marcar notificaciones"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        id_cliente = request.user.cliente.id_cliente
        result = notificacion_manager.marcarTodasLeidas(id_cliente)
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al marcar todas como leídas: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al marcar todas como leídas: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_notificacion(request, id_notificacion):
    """
    Elimina una notificación
    DELETE /api/notificaciones/{id_notificacion}/
    - Clientes pueden eliminar sus propias notificaciones
    - Administradores pueden eliminar cualquier notificación
    """
    try:
        # Verificar que existe
        resp_notif = notificacion_manager.obtenerNotificacion(id_notificacion)
        
        if not resp_notif['success']:
            return Response(resp_notif, status=status.HTTP_404_NOT_FOUND)
        
        notificacion = resp_notif['data']
        
        # Verificar permisos
        es_admin = hasattr(request.user, 'administrador')
        es_cliente_propietario = False
        
        if hasattr(request.user, 'cliente'):
            es_cliente_propietario = (request.user.cliente.id_cliente == notificacion['id_cliente'])
        
        if not es_admin and not es_cliente_propietario:
            return Response(
                {"success": False, "message": "No tienes permisos para eliminar esta notificación"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result = notificacion_manager.eliminarNotificacion(id_notificacion)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error al eliminar notificación: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al eliminar notificación: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_todas_notificaciones(request):
    """
    Lista todas las notificaciones (solo administradores)
    GET /api/notificaciones/?limite=100
    """
    try:
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para ver todas las notificaciones"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        limite = int(request.query_params.get('limite', 100))
        result = notificacion_manager.listarTodas(limite)
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al listar todas las notificaciones: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al listar notificaciones: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
