#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from manager.asistenciaManager import AsistenciaManager
from manager.authManager import AuthManager
import logging

logger = logging.getLogger(__name__)
asistencia_manager = AsistenciaManager()
auth_manager = AuthManager()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_entrada(request):
    """
    POST /api/asistencia/entrada/
    Registra la entrada (clock-in) del empleado autenticado
    Body: { "id_turno": 1 } (opcional)
    """
    try:
        # Obtener empleado del usuario autenticado
        id_usuario = request.user.id
        resp_empleado = auth_manager.obtenerEmpleadoPorUsuario(id_usuario)
        
        if not resp_empleado.get('success') or not resp_empleado.get('data'):
            return Response({
                "success": False,
                "message": "El usuario no está asociado a un empleado"
            }, status=status.HTTP_403_FORBIDDEN)
        
        empleado = resp_empleado['data']
        id_empleado = empleado['id_empleado']
        
        # Obtener id_turno si se proporciona
        id_turno = request.data.get('id_turno')
        
        resp = asistencia_manager.registrarEntrada(id_empleado, id_turno)
        
        if not resp["success"]:
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(resp, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error en registrar_entrada: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al registrar entrada: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_salida(request):
    """
    POST /api/asistencia/salida/
    Registra la salida (clock-out) del empleado autenticado
    Body: {} (vacío, busca asistencia activa automáticamente)
    """
    try:
        # Obtener empleado del usuario autenticado
        id_usuario = request.user.id
        resp_empleado = auth_manager.obtenerEmpleadoPorUsuario(id_usuario)
        
        if not resp_empleado.get('success') or not resp_empleado.get('data'):
            return Response({
                "success": False,
                "message": "El usuario no está asociado a un empleado"
            }, status=status.HTTP_403_FORBIDDEN)
        
        empleado = resp_empleado['data']
        id_empleado = empleado['id_empleado']
        
        resp = asistencia_manager.registrarSalidaPorEmpleado(id_empleado)
        
        if not resp["success"]:
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en registrar_salida: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al registrar salida: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_registros(request):
    """
    GET /api/asistencia/mis-registros/
    Obtiene los registros de asistencia del empleado autenticado
    Query params: limite (default: 50)
    """
    try:
        # Obtener empleado del usuario autenticado
        id_usuario = request.user.id
        resp_empleado = auth_manager.obtenerEmpleadoPorUsuario(id_usuario)
        
        if not resp_empleado.get('success') or not resp_empleado.get('data'):
            return Response({
                "success": False,
                "message": "El usuario no está asociado a un empleado"
            }, status=status.HTTP_403_FORBIDDEN)
        
        empleado = resp_empleado['data']
        id_empleado = empleado['id_empleado']
        
        limite = int(request.GET.get('limite', 50))
        
        resp = asistencia_manager.listarPorEmpleado(id_empleado, limite)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en mis_registros: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al obtener registros: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_asistencias(request):
    """
    GET /api/asistencia/
    Lista todas las asistencias (solo administradores)
    Query params: limite (default: 100)
    """
    try:
        # Verificar que es administrador
        id_usuario = request.user.id
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        
        if not resp_admin.get('success') or not resp_admin.get('data'):
            return Response({
                "success": False,
                "message": "Acceso denegado. Solo administradores"
            }, status=status.HTTP_403_FORBIDDEN)
        
        limite = int(request.GET.get('limite', 100))
        
        resp = asistencia_manager.listarTodas(limite)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en listar_asistencias: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al listar asistencias: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asistencias_por_fecha(request, fecha):
    """
    GET /api/asistencia/fecha/{fecha}/
    Lista asistencias de una fecha específica (solo administradores)
    Params: fecha (YYYY-MM-DD)
    Query params: limite (default: 100)
    """
    try:
        # Verificar que es administrador
        id_usuario = request.user.id
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        
        if not resp_admin.get('success') or not resp_admin.get('data'):
            return Response({
                "success": False,
                "message": "Acceso denegado. Solo administradores"
            }, status=status.HTTP_403_FORBIDDEN)
        
        limite = int(request.GET.get('limite', 100))
        
        resp = asistencia_manager.listarPorFecha(fecha, limite)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en asistencias_por_fecha: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al listar asistencias: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asistencias_por_empleado(request, id_empleado):
    """
    GET /api/asistencia/empleado/{id}/
    Lista asistencias de un empleado específico (solo administradores)
    Params: id_empleado
    Query params: limite (default: 50)
    """
    try:
        # Verificar que es administrador
        id_usuario = request.user.id
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        
        if not resp_admin.get('success') or not resp_admin.get('data'):
            return Response({
                "success": False,
                "message": "Acceso denegado. Solo administradores"
            }, status=status.HTTP_403_FORBIDDEN)
        
        limite = int(request.GET.get('limite', 50))
        
        resp = asistencia_manager.listarPorEmpleado(id_empleado, limite)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en asistencias_por_empleado: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al listar asistencias: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_asistencia(request, id_asistencia):
    """
    GET /api/asistencia/{id}/
    Obtiene una asistencia específica
    Los empleados solo pueden ver sus propias asistencias
    Los administradores pueden ver cualquiera
    """
    try:
        id_usuario = request.user.id
        
        # Verificar si es administrador
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        es_admin = resp_admin.get('success') and resp_admin.get('data')
        
        resp = asistencia_manager.obtenerAsistencia(id_asistencia)
        
        if not resp["success"]:
            return Response(resp, status=status.HTTP_404_NOT_FOUND)
        
        # Si no es admin, verificar que sea su propia asistencia
        if not es_admin:
            resp_empleado = auth_manager.obtenerEmpleadoPorUsuario(id_usuario)
            if not resp_empleado.get('success') or not resp_empleado.get('data'):
                return Response({
                    "success": False,
                    "message": "Acceso denegado"
                }, status=status.HTTP_403_FORBIDDEN)
            
            empleado = resp_empleado['data']
            asistencia = resp['data']
            
            if asistencia['id_empleado'] != empleado['id_empleado']:
                return Response({
                    "success": False,
                    "message": "Acceso denegado. Solo puedes ver tus propias asistencias"
                }, status=status.HTTP_403_FORBIDDEN)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en obtener_asistencia: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al obtener asistencia: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modificar_asistencia(request, id_asistencia):
    """
    PATCH /api/asistencia/{id}/
    Modifica una asistencia (solo administradores)
    Body: { "id_turno": 2, "fecha": "2025-01-21", "hora_entrada": "08:00", "hora_salida": "17:00", "estado": "asistio", "observaciones": "..." }
    """
    try:
        # Verificar que es administrador
        id_usuario = request.user.id
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        
        if not resp_admin.get('success') or not resp_admin.get('data'):
            return Response({
                "success": False,
                "message": "Acceso denegado. Solo administradores"
            }, status=status.HTTP_403_FORBIDDEN)
        
        resp = asistencia_manager.modificarAsistencia(id_asistencia, request.data)
        
        if not resp["success"]:
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en modificar_asistencia: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al modificar asistencia: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_asistencia(request, id_asistencia):
    """
    DELETE /api/asistencia/{id}/
    Elimina una asistencia (solo administradores)
    """
    try:
        # Verificar que es administrador
        id_usuario = request.user.id
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        
        if not resp_admin.get('success') or not resp_admin.get('data'):
            return Response({
                "success": False,
                "message": "Acceso denegado. Solo administradores"
            }, status=status.HTTP_403_FORBIDDEN)
        
        resp = asistencia_manager.eliminarAsistencia(id_asistencia)
        
        if not resp["success"]:
            return Response(resp, status=status.HTTP_404_NOT_FOUND)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en eliminar_asistencia: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al eliminar asistencia: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_mensual(request):
    """
    GET /api/asistencia/reporte-mensual/
    Obtiene reporte mensual de asistencias
    Query params: id_empleado (opcional para admin), year, month
    Si no se especifica id_empleado, retorna el del usuario autenticado
    """
    try:
        year = request.GET.get('year')
        month = request.GET.get('month')
        id_empleado_param = request.GET.get('id_empleado')
        
        if not year or not month:
            return Response({
                "success": False,
                "message": "Se requieren parámetros year y month"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        id_usuario = request.user.id
        
        # Verificar si es administrador
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        es_admin = resp_admin.get('success') and resp_admin.get('data')
        
        # Determinar id_empleado
        if id_empleado_param:
            # Si se especifica id_empleado, debe ser admin
            if not es_admin:
                return Response({
                    "success": False,
                    "message": "Solo administradores pueden consultar reportes de otros empleados"
                }, status=status.HTTP_403_FORBIDDEN)
            id_empleado = int(id_empleado_param)
        else:
            # Si no se especifica, obtener del usuario autenticado
            resp_empleado = auth_manager.obtenerEmpleadoPorUsuario(id_usuario)
            if not resp_empleado.get('success') or not resp_empleado.get('data'):
                return Response({
                    "success": False,
                    "message": "El usuario no está asociado a un empleado"
                }, status=status.HTTP_403_FORBIDDEN)
            empleado = resp_empleado['data']
            id_empleado = empleado['id_empleado']
        
        resp = asistencia_manager.obtenerReporteMensual(id_empleado, int(year), int(month))
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en reporte_mensual: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al generar reporte: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def actualizar_estado(request, id_asistencia):
    """
    POST /api/asistencia/{id}/estado/
    Actualiza el estado de una asistencia (solo administradores)
    Body: { "estado": "falta", "observaciones": "Ausencia no justificada" }
    """
    try:
        # Verificar que es administrador
        id_usuario = request.user.id
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        
        if not resp_admin.get('success') or not resp_admin.get('data'):
            return Response({
                "success": False,
                "message": "Acceso denegado. Solo administradores"
            }, status=status.HTTP_403_FORBIDDEN)
        
        estado = request.data.get('estado')
        observaciones = request.data.get('observaciones')
        
        if not estado:
            return Response({
                "success": False,
                "message": "El campo 'estado' es requerido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resp = asistencia_manager.actualizarEstado(id_asistencia, estado, observaciones)
        
        if not resp["success"]:
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en actualizar_estado: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al actualizar estado: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asistencias_por_estado(request, estado):
    """
    GET /api/asistencia/estado/{estado}/
    Lista asistencias por estado (solo administradores)
    Params: estado (pendiente, asistio, falta, tardanza, justificado)
    Query params: limite (default: 100)
    """
    try:
        # Verificar que es administrador
        id_usuario = request.user.id
        resp_admin = auth_manager.obtenerAdministradorPorUsuario(id_usuario)
        
        if not resp_admin.get('success') or not resp_admin.get('data'):
            return Response({
                "success": False,
                "message": "Acceso denegado. Solo administradores"
            }, status=status.HTTP_403_FORBIDDEN)
        
        limite = int(request.GET.get('limite', 100))
        
        resp = asistencia_manager.listarPorEstado(estado, limite)
        
        if not resp["success"]:
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(resp, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error en asistencias_por_estado: {str(e)}")
        return Response({
            "success": False,
            "message": f"Error al listar asistencias: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
