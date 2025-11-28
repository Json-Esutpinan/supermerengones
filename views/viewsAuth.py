#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from manager.authManager import AuthManager
from datetime import datetime

# Instancia del manager
auth_manager = AuthManager()


@api_view(['POST'])
def login_view(request):
    """
    Inicia sesión de un usuario
    
    POST /api/auth/login/
    Body:
        - email: correo del usuario
        - password: contraseña
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email y contraseña son requeridos',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        resultado = auth_manager.login(email, password)

        if resultado['success']:
            # Serializar respuesta con perfil según rol
            data = {
                'usuario': resultado['data']['usuario'].to_dict(incluir_password=False),
                'rol': resultado['data']['rol']
            }
            
            # Agregar perfil según rol
            if resultado['data']['perfil']:
                data['perfil'] = resultado['data']['perfil'].to_dict()
            
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def registrar_cliente_view(request):
    """
    Registra un nuevo cliente
    
    POST /api/auth/registrar-cliente/
    Body:
        - nombre
        - telefono (opcional)
        - email
        - direccion (opcional)
        - password
    """
    try:
        nombre = request.data.get('nombre')
        telefono = request.data.get('telefono', '')
        email = request.data.get('email')
        direccion = request.data.get('direccion', '')
        password = request.data.get('password')

        resultado = auth_manager.registrarCliente(nombre, telefono, email, direccion, password)

        if resultado['success']:
            usuario = resultado['data']['usuario'].to_dict(incluir_password=False)
            cliente = resultado['data']['cliente'].to_dict()
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': {
                    'usuario': usuario,
                    'cliente': cliente
                }
            }, status=status.HTTP_201_CREATED)
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


@api_view(['POST'])
def registrar_empleado_view(request):
    """
    Registra un nuevo empleado (requiere autenticación como administrador)
    
    POST /api/auth/registrar-empleado/
    Body:
        - nombre
        - email
        - password
        - id_sede
        - cargo
        - fecha_ingreso (opcional, formato YYYY-MM-DD)
    """
    try:
        # Verificar autenticación (solo admins pueden crear empleados)
        usuario_actual = auth_manager.usuarioLogueado()
        if not usuario_actual or usuario_actual.rol != 'administrador':
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        nombre = request.data.get('nombre')
        email = request.data.get('email')
        password = request.data.get('password')
        id_sede = request.data.get('id_sede')
        cargo = request.data.get('cargo', '')
        fecha_ingreso_str = request.data.get('fecha_ingreso')

        # Parsear fecha si viene como string
        fecha_ingreso = None
        if fecha_ingreso_str:
            try:
                fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

        resultado = auth_manager.registrarEmpleado(
            nombre=nombre,
            email=email,
            password=password,
            id_sede=id_sede,
            cargo=cargo,
            fecha_ingreso=fecha_ingreso
        )

        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': {
                    'usuario': resultado['data']['usuario'].to_dict(incluir_password=False),
                    'empleado': resultado['data']['empleado'].to_dict()
                }
            }, status=status.HTTP_201_CREATED)
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


@api_view(['POST'])
def registrar_administrador_view(request):
    """
    Registra un nuevo administrador (requiere autenticación como administrador)
    
    POST /api/auth/registrar-administrador/
    Body:
        - nombre
        - email
        - password
        - nivel_acceso (opcional: basico, intermedio, avanzado, total)
    """
    try:
        # Verificar autenticación (solo admins pueden crear otros admins)
        usuario_actual = auth_manager.usuarioLogueado()
        if not usuario_actual or usuario_actual.rol != 'administrador':
            return Response({
                'success': False,
                'message': 'Se requiere autenticación como administrador',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        nombre = request.data.get('nombre')
        email = request.data.get('email')
        password = request.data.get('password')
        nivel_acceso = request.data.get('nivel_acceso', 'basico')

        resultado = auth_manager.registrarAdministrador(
            nombre=nombre,
            email=email,
            password=password,
            nivel_acceso=nivel_acceso
        )

        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': {
                    'usuario': resultado['data']['usuario'].to_dict(incluir_password=False),
                    'administrador': resultado['data']['administrador'].to_dict()
                }
            }, status=status.HTTP_201_CREATED)
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
def usuario_actual_view(request):
    """
    Devuelve el usuario actualmente logueado
    
    GET /api/auth/usuario/
    """
    try:
        usuario = auth_manager.usuarioLogueado()

        if not usuario:
            return Response({
                'success': False,
                'message': 'Ningún usuario logueado',
                'data': None
            }, status=status.HTTP_200_OK)

        return Response({
            'success': True,
            'message': 'Usuario logueado',
            'data': usuario.to_dict(incluir_password=False)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def cerrar_sesion_view(request):
    """
    Cierra la sesión del usuario actual
    
    POST /api/auth/logout/
    """
    try:
        resultado = auth_manager.cerrarSesion()
        return Response({
            'success': True,
            'message': resultado['message'],
            'data': None
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
