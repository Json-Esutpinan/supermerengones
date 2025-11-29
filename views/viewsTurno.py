#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from manager.turnoManager import TurnoManager

logger = logging.getLogger(__name__)
turno_manager = TurnoManager()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_turno(request):
    """
    Crea un nuevo turno (solo administradores)
    POST /api/turnos/
    Body: {
        "id_empleado": 5,
        "fecha": "2025-01-21",
        "hora_inicio": "08:00",
        "hora_fin": "17:00"
    }
    """
    try:
        # Solo administradores pueden crear turnos
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para crear turnos"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        id_empleado = request.data.get('id_empleado')
        fecha = request.data.get('fecha')
        hora_inicio = request.data.get('hora_inicio')
        hora_fin = request.data.get('hora_fin')
        
        result = turno_manager.crearTurno(id_empleado, fecha, hora_inicio, hora_fin)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al crear turno: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al crear turno: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_turnos(request):
    """
    Lista todos los turnos (solo administradores)
    GET /api/turnos/?limite=100
    """
    try:
        # Solo administradores pueden ver todos los turnos
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para ver todos los turnos"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        limite = int(request.query_params.get('limite', 100))
        result = turno_manager.listarTodos(limite)
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al listar turnos: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al listar turnos: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_turnos_empleado(request, id_empleado):
    """
    Lista turnos de un empleado específico
    GET /api/turnos/empleado/{id_empleado}/?limite=50
    - Empleados solo pueden ver sus propios turnos
    - Administradores pueden ver turnos de cualquier empleado
    """
    try:
        # Verificar permisos
        es_admin = hasattr(request.user, 'administrador')
        es_empleado_propietario = False
        
        if hasattr(request.user, 'empleado'):
            es_empleado_propietario = (request.user.empleado.id_empleado == id_empleado)
        
        if not es_admin and not es_empleado_propietario:
            return Response(
                {"success": False, "message": "No tienes permisos para ver estos turnos"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        limite = int(request.query_params.get('limite', 50))
        result = turno_manager.listarPorEmpleado(id_empleado, limite)
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al listar turnos del empleado: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al listar turnos: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_turnos_fecha(request, fecha):
    """
    Lista todos los turnos en una fecha específica (solo administradores)
    GET /api/turnos/fecha/{fecha}/?limite=100
    fecha formato: YYYY-MM-DD
    """
    try:
        # Solo administradores pueden ver turnos por fecha
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para ver turnos por fecha"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        limite = int(request.query_params.get('limite', 100))
        result = turno_manager.listarPorFecha(fecha, limite)
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al listar turnos por fecha: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al listar turnos: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_turnos_sede_fecha(request, id_sede, fecha):
    """
    Lista turnos de una sede en una fecha específica (solo administradores)
    GET /api/turnos/sede/{id_sede}/fecha/{fecha}/?limite=100
    """
    try:
        # Solo administradores pueden ver turnos por sede y fecha
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para ver turnos por sede"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        limite = int(request.query_params.get('limite', 100))
        result = turno_manager.listarPorSedeFecha(id_sede, fecha, limite)
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al listar turnos por sede y fecha: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al listar turnos: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_turno(request, id_turno):
    """
    Obtiene los detalles de un turno específico
    GET /api/turnos/{id_turno}/
    - Empleados solo pueden ver sus propios turnos
    - Administradores pueden ver cualquier turno
    """
    try:
        result = turno_manager.obtenerTurno(id_turno)
        
        if not result['success']:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar permisos
        turno = result['data']
        es_admin = hasattr(request.user, 'administrador')
        es_empleado_propietario = False
        
        if hasattr(request.user, 'empleado'):
            es_empleado_propietario = (request.user.empleado.id_empleado == turno['id_empleado'])
        
        if not es_admin and not es_empleado_propietario:
            return Response(
                {"success": False, "message": "No tienes permisos para ver este turno"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al obtener turno: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al obtener turno: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modificar_turno(request, id_turno):
    """
    Modifica un turno existente (solo administradores)
    PATCH /api/turnos/{id_turno}/
    Body: {
        "fecha": "2025-01-22",
        "hora_inicio": "09:00",
        "hora_fin": "18:00",
        "id_empleado": 6  // opcional, para reasignar
    }
    """
    try:
        # Solo administradores pueden modificar turnos
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para modificar turnos"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result = turno_manager.modificarTurno(id_turno, request.data)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error al modificar turno: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al modificar turno: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_turno(request, id_turno):
    """
    Elimina un turno (solo administradores)
    DELETE /api/turnos/{id_turno}/
    """
    try:
        # Solo administradores pueden eliminar turnos
        if not hasattr(request.user, 'administrador'):
            return Response(
                {"success": False, "message": "No tienes permisos para eliminar turnos"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result = turno_manager.eliminarTurno(id_turno)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error al eliminar turno: {str(e)}")
        return Response(
            {"success": False, "message": f"Error al eliminar turno: {str(e)}", "data": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
