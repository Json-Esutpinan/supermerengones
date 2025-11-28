#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from manager.productoManager import ProductoManager


producto_manager = ProductoManager()


@api_view(['GET'])
def listar_productos(request):
    """
    Lista productos con filtros opcionales
    
    Query params:
    - activo: 'true'|'false' - filtrar solo activos
    - stock_bajo: 'true' - solo productos con stock bajo
    - stock_minimo: número - umbral para stock bajo (default: 10)
    - q: término - búsqueda por nombre
    """
    try:
        # Si hay búsqueda por nombre
        q = request.GET.get('q')
        if q:
            resultado = producto_manager.buscarProductos(q)
            productos_list = [p.to_dict() for p in resultado['productos']]
            
            return Response({
                'success': resultado['exito'],
                'message': resultado['mensaje'],
                'data': productos_list
            }, status=status.HTTP_200_OK)
        
        # Filtros
        solo_activos = request.GET.get('activo', 'true').lower() == 'true'
        stock_bajo = request.GET.get('stock_bajo', 'false').lower() == 'true'
        stock_minimo = int(request.GET.get('stock_minimo', 10))
        
        resultado = producto_manager.listarProductos(
            solo_activos=solo_activos,
            stock_bajo=stock_bajo,
            stock_minimo=stock_minimo
        )
        
        productos_list = [p.to_dict() for p in resultado['productos']]
        
        return Response({
            'success': resultado['exito'],
            'message': resultado['mensaje'],
            'data': productos_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al listar productos: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_producto(request, id_producto):
    """Obtiene un producto por su ID"""
    try:
        resultado = producto_manager.obtenerProducto(id_producto)
        
        if resultado['exito']:
            producto_dict = resultado['producto'].to_dict()
            return Response({
                'success': True,
                'message': resultado['mensaje'],
                'data': producto_dict
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': resultado['mensaje'],
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener producto: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_producto(request):
    """
    Crea un nuevo producto
    
    Body (JSON):
    {
        "codigo": "PROD001",
        "nombre": "Producto Ejemplo",
        "descripcion": "Descripción del producto",
        "id_unidad": 1,
        "contenido": 500,
        "precio": 15.50,
        "stock": 100
    }
    """
    try:
        datos = request.data
        
        # Validar campos requeridos
        campos_requeridos = ['codigo', 'nombre', 'id_unidad', 'contenido', 'precio']
        for campo in campos_requeridos:
            if campo not in datos:
                return Response({
                    'success': False,
                    'message': f'El campo {campo} es requerido',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = producto_manager.crearProducto(
            codigo=datos['codigo'],
            nombre=datos['nombre'],
            descripcion=datos.get('descripcion', ''),
            id_unidad=datos['id_unidad'],
            contenido=datos['contenido'],
            precio=datos['precio'],
            stock=datos.get('stock', 0)
        )
        
        if resultado['exito']:
            producto_dict = resultado['producto'].to_dict()
            return Response({
                'success': True,
                'message': resultado['mensaje'],
                'data': producto_dict
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': resultado['mensaje'],
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al crear producto: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def modificar_producto(request, id_producto):
    """
    Modifica un producto existente
    
    Body (JSON) - todos los campos son opcionales:
    {
        "codigo": "PROD001-NEW",
        "nombre": "Nuevo Nombre",
        "descripcion": "Nueva descripción",
        "id_unidad": 2,
        "contenido": 750,
        "precio": 20.00,
        "stock": 150
    }
    """
    try:
        datos = request.data
        
        if not datos:
            return Response({
                'success': False,
                'message': 'Debe proporcionar al menos un campo para actualizar',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = producto_manager.modificarProducto(id_producto, datos)
        
        if resultado['exito']:
            producto_dict = resultado['producto'].to_dict()
            return Response({
                'success': True,
                'message': resultado['mensaje'],
                'data': producto_dict
            }, status=status.HTTP_200_OK)
        
        # Determinar código de error apropiado
        status_code = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['mensaje'].lower() else status.HTTP_400_BAD_REQUEST
        
        return Response({
            'success': False,
            'message': resultado['mensaje'],
            'data': None
        }, status=status_code)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al modificar producto: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cambiar_estado_producto(request, id_producto):
    """
    Cambia el estado de un producto (activo/inactivo)
    
    Body (JSON):
    {
        "activo": true/false
    }
    """
    try:
        activo = request.data.get('activo')
        
        if activo is None:
            return Response({
                'success': False,
                'message': 'El campo "activo" es requerido',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(activo, bool):
            return Response({
                'success': False,
                'message': 'El campo "activo" debe ser true o false',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = producto_manager.cambiarEstado(id_producto, activo)
        
        if resultado['exito']:
            producto_dict = resultado['producto'].to_dict()
            return Response({
                'success': True,
                'message': resultado['mensaje'],
                'data': producto_dict
            }, status=status.HTTP_200_OK)
        
        status_code = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['mensaje'].lower() else status.HTTP_400_BAD_REQUEST
        
        return Response({
            'success': False,
            'message': resultado['mensaje'],
            'data': None
        }, status=status_code)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al cambiar estado: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_stock_producto(request, id_producto):
    """
    Actualiza el stock de un producto
    
    Body (JSON):
    {
        "cantidad": 50,
        "operacion": "sumar"  // o "restar"
    }
    """
    try:
        cantidad = request.data.get('cantidad')
        operacion = request.data.get('operacion', 'sumar')
        
        if cantidad is None:
            return Response({
                'success': False,
                'message': 'El campo "cantidad" es requerido',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = producto_manager.actualizarStock(id_producto, cantidad, operacion)
        
        if resultado['exito']:
            producto_dict = resultado['producto'].to_dict()
            return Response({
                'success': True,
                'message': resultado['mensaje'],
                'data': producto_dict
            }, status=status.HTTP_200_OK)
        
        status_code = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['mensaje'].lower() else status.HTTP_400_BAD_REQUEST
        
        return Response({
            'success': False,
            'message': resultado['mensaje'],
            'data': None
        }, status=status_code)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al actualizar stock: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def verificar_disponibilidad_producto(request, id_producto):
    """
    Verifica si un producto tiene stock disponible para una cantidad dada.

    Query params:
    - cantidad: entero > 0 (requerido)
    """
    try:
        cantidad = request.GET.get('cantidad')
        if cantidad is None:
            return Response({
                'success': False,
                'message': 'El parámetro "cantidad" es requerido',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        disponible = producto_manager.verificar_disponibilidad(id_producto, cantidad)

        return Response({
            'success': True,
            'message': 'Verificación realizada',
            'data': { 'disponible': bool(disponible) }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al verificar disponibilidad: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
