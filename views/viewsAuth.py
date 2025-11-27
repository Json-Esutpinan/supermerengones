#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from manager.authManager import AuthManager

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
        - telefono
        - email
        - password
    """
    try:
        nombre = request.data.get('nombre')
        telefono = request.data.get('telefono')
        email = request.data.get('email')
        direccion = request.data.get('direccion')
        password = request.data.get('password')

        if not nombre or not email or not password:
            return Response({
                'success': False,
                'message': 'Nombre, email y contraseña son requeridos',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        resultado = auth_manager.registrarCliente(nombre, telefono, email, direccion, password)

        if resultado['success']:
            usuario = resultado['data']['usuario'].to_dict()
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
            'data': usuario.to_dict()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
