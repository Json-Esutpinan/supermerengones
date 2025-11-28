#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from manager.personalManager import PersonalManager
from manager.authManager import AuthManager

personal_manager = PersonalManager()
auth_manager = AuthManager()


def _verificar_autenticacion_admin():
    """Verifica que el usuario actual sea administrador"""
    usuario_actual = auth_manager.usuarioLogueado()
    if not usuario_actual or usuario_actual.rol != 'administrador':
        return False, None
    return True, usuario_actual


# ------------------------------------------------------------------
# LISTAR EMPLEADOS
# ------------------------------------------------------------------
@api_view(['GET'])
def listar_empleados(request):
    """
    Lista empleados con filtros opcionales
    
    GET /api/empleados/
    Query params:
        - limite: número máximo de resultados
        - activos: true/false (solo empleados activos)
    """
    try:
        # Verificar autenticación admin
        es_admin, _ = _verificar_autenticacion_admin()
        if not es_admin:
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        limite = request.query_params.get('limite')
        solo_activos = request.query_params.get('activos', '').lower() == 'true'
        
        if limite:
            try:
                limite = int(limite)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'El parámetro limite debe ser un número',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if solo_activos:
            resultado = personal_manager.listarActivos(limite=limite)
        else:
            resultado = personal_manager.listarTodos(limite=limite)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data']
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


@api_view(['GET'])
def listar_empleados_por_sede(request, id_sede):
    """
    Lista empleados de una sede específica
    
    GET /api/empleados/sede/{id_sede}/
    Query params:
        - limite: número máximo de resultados
    """
    try:
        # Verificar autenticación admin
        es_admin, _ = _verificar_autenticacion_admin()
        if not es_admin:
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        limite = request.query_params.get('limite')
        if limite:
            try:
                limite = int(limite)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'El parámetro limite debe ser un número',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = personal_manager.listarPorSede(id_sede, limite=limite)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=status.HTTP_404_NOT_FOUND if 'no encontrada' in resultado['message'] else status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------------------------------------------------------
# OBTENER EMPLEADO
# ------------------------------------------------------------------
@api_view(['GET'])
def obtener_empleado(request, id_empleado):
    """
    Obtiene detalle de un empleado
    
    GET /api/empleados/{id_empleado}/
    """
    try:
        # Verificar autenticación admin
        es_admin, _ = _verificar_autenticacion_admin()
        if not es_admin:
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        resultado = personal_manager.obtenerEmpleado(id_empleado)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data']
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


# ------------------------------------------------------------------
# MODIFICAR EMPLEADO
# ------------------------------------------------------------------
@api_view(['PATCH'])
def modificar_empleado(request, id_empleado):
    """
    Modifica datos de un empleado
    
    PATCH /api/empleados/{id_empleado}/
    Body:
        - cargo: nuevo cargo (opcional)
        - id_sede: nueva sede (opcional)
    """
    try:
        # Verificar autenticación admin
        es_admin, _ = _verificar_autenticacion_admin()
        if not es_admin:
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        datos = {}
        if 'cargo' in request.data:
            datos['cargo'] = request.data['cargo']
        if 'id_sede' in request.data:
            datos['id_sede'] = request.data['id_sede']
        
        if not datos:
            return Response({
                'success': False,
                'message': 'Debe proporcionar al menos un campo para actualizar (cargo, id_sede)',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = personal_manager.modificarEmpleado(id_empleado, datos)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'] else status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------------------------------------------------------
# TRANSFERIR SEDE
# ------------------------------------------------------------------
@api_view(['POST'])
def transferir_sede(request, id_empleado):
    """
    Transfiere un empleado a otra sede
    
    POST /api/empleados/{id_empleado}/transferir/
    Body:
        - nueva_sede: ID de la sede destino
    """
    try:
        # Verificar autenticación admin
        es_admin, _ = _verificar_autenticacion_admin()
        if not es_admin:
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        nueva_sede = request.data.get('nueva_sede')
        if not nueva_sede:
            return Response({
                'success': False,
                'message': 'El campo nueva_sede es requerido',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = personal_manager.cambiarSede(id_empleado, nueva_sede)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=status.HTTP_404_NOT_FOUND if 'no encontrad' in resultado['message'] else status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------------------------------------------------------
# DESACTIVAR / ACTIVAR EMPLEADO
# ------------------------------------------------------------------
@api_view(['POST'])
def desactivar_empleado(request, id_empleado):
    """
    Desactiva un empleado
    
    POST /api/empleados/{id_empleado}/desactivar/
    """
    try:
        # Verificar autenticación admin
        es_admin, _ = _verificar_autenticacion_admin()
        if not es_admin:
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        resultado = personal_manager.desactivarEmpleado(id_empleado)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'] else status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def activar_empleado(request, id_empleado):
    """
    Activa un empleado
    
    POST /api/empleados/{id_empleado}/activar/
    """
    try:
        # Verificar autenticación admin
        es_admin, _ = _verificar_autenticacion_admin()
        if not es_admin:
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        resultado = personal_manager.activarEmpleado(id_empleado)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'] else status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
