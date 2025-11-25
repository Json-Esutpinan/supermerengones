#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from manager.proveedorManager import ProveedorManager
from manager.pedidoManager import PedidoManager
import json

# Instancias de los managers
proveedor_manager = ProveedorManager()
pedido_manager = PedidoManager()


@api_view(['POST'])
def crear_proveedor(request):
    """
    Crea un nuevo proveedor
    
    POST /api/proveedores/
    Body: {
        "nombre": "Proveedor Ejemplo",
        "email": "contacto@proveedor.com",
        "telefono": "3001234567",
        "direccion": "Calle 123 #45-67"
    }
    """
    try:
        datos = request.data
        
        # Validar que se envió el nombre
        if 'nombre' not in datos:
            return Response({
                'success': False,
                'message': 'El campo nombre es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el proveedor
        resultado = proveedor_manager.crearProveedor(
            nombre=datos.get('nombre'),
            email=datos.get('email', ''),
            telefono=datos.get('telefono', ''),
            direccion=datos.get('direccion', '')
        )
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado['data'] else None
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': resultado['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_proveedores(request):
    """
    Lista todos los proveedores activos
    
    GET /api/proveedores/
    Query params (opcionales):
        - todos: true/false (incluir inactivos)
        - buscar: texto para buscar en el nombre
    """
    try:
        # Verificar si se solicita buscar por nombre
        buscar = request.GET.get('buscar', None)
        
        if buscar:
            resultado = proveedor_manager.buscarProveedores(buscar)
        else:
            # Verificar si se solicita incluir inactivos
            solo_activos = request.GET.get('todos', 'false').lower() != 'true'
            resultado = proveedor_manager.listarProveedores(solo_activos=solo_activos)
        
        if resultado['success']:
            proveedores_dict = [p.to_dict() for p in resultado['data']]
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': proveedores_dict
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
def obtener_proveedor(request, id_proveedor):
    """
    Obtiene un proveedor por su ID
    
    GET /api/proveedores/{id_proveedor}/
    """
    try:
        resultado = proveedor_manager.obtenerProveedor(id_proveedor)
        
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


@api_view(['PUT', 'PATCH'])
def modificar_proveedor(request, id_proveedor):
    """
    Modifica un proveedor existente
    
    PUT/PATCH /api/proveedores/{id_proveedor}/
    Body: {
        "nombre": "Nuevo nombre",
        "email": "nuevo@email.com",
        "telefono": "3009876543",
        "direccion": "Nueva dirección",
        "activo": true
    }
    """
    try:
        datos = request.data
        
        # Modificar el proveedor
        resultado = proveedor_manager.modificarProveedor(id_proveedor, datos)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado['data'] else None
            }, status=status.HTTP_200_OK)
        else:
            codigo_estado = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'].lower() else status.HTTP_400_BAD_REQUEST
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=codigo_estado)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
def cambiar_estado_proveedor(request, id_proveedor):
    """
    Cambia el estado de un proveedor (activar/desactivar)
    
    PATCH /api/proveedores/{id_proveedor}/estado/
    Body: {
        "activo": true  // o false
    }
    """
    try:
        activo = request.data.get('activo')
        
        if activo is None:
            return Response({
                'success': False,
                'message': 'El campo "activo" es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(activo, bool):
            return Response({
                'success': False,
                'message': 'El campo "activo" debe ser un booleano (true/false)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = proveedor_manager.cambiarEstadoProveedor(id_proveedor, activo)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado['data'] else None
            }, status=status.HTTP_200_OK)
        else:
            codigo_estado = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'].lower() else status.HTTP_400_BAD_REQUEST
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=codigo_estado)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def desactivar_proveedor(request, id_proveedor):
    """
    Desactiva un proveedor (eliminación lógica)
    
    DELETE /api/proveedores/{id_proveedor}/
    """
    try:
        resultado = proveedor_manager.desactivarProveedor(id_proveedor)
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado['data'] else None
            }, status=status.HTTP_200_OK)
        else:
            codigo_estado = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'].lower() else status.HTTP_400_BAD_REQUEST
            return Response({
                'success': False,
                'message': resultado['message'],
                'data': None
            }, status=codigo_estado)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
