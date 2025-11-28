#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from manager.compraManager import CompraManager
import json
import logging

logger = logging.getLogger(__name__)
compra_manager = CompraManager()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_compra(request):
    """
    Crea una nueva compra a proveedor con sus detalles
    
    POST /api/compras/crear/
    Body: {
        "id_proveedor": 1,
        "detalles": [
            {"id_insumo": 1, "cantidad": 50, "precio_unitario": 2.5},
            {"id_insumo": 2, "cantidad": 30, "precio_unitario": 1.8}
        ],
        "registrar_en_inventario": true,
        "id_sede": 1
    }
    """
    try:
        data = json.loads(request.body)
        
        id_proveedor = data.get('id_proveedor')
        detalles = data.get('detalles', [])
        registrar_en_inventario = data.get('registrar_en_inventario', True)
        id_sede = data.get('id_sede')
        
        # Obtener ID de usuario autenticado
        id_usuario = request.user.id
        
        resultado = compra_manager.crearCompra(
            id_proveedor=id_proveedor,
            id_usuario=id_usuario,
            detalles=detalles,
            registrar_en_inventario=registrar_en_inventario,
            id_sede=id_sede
        )
        
        if resultado['success']:
            return JsonResponse(resultado, status=201)
        else:
            return JsonResponse(resultado, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido en el cuerpo de la solicitud'
        }, status=400)
    except Exception as e:
        logger.error(f"Error al crear compra: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=500)


@api_view(['GET'])
def listar_compras(request):
    """
    Lista todas las compras con filtros opcionales
    
    GET /api/compras/
    GET /api/compras/?estado=pendiente
    GET /api/compras/?id_proveedor=1
    GET /api/compras/?fecha_desde=2025-01-01&fecha_hasta=2025-01-31
    """
    try:
        estado = request.GET.get('estado')
        id_proveedor = request.GET.get('id_proveedor')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        limite = int(request.GET.get('limite', 100))
        
        # Convertir id_proveedor a int si existe
        if id_proveedor:
            try:
                id_proveedor = int(id_proveedor)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'id_proveedor debe ser un número'
                }, status=400)
        
        resultado = compra_manager.listarCompras(
            estado=estado,
            id_proveedor=id_proveedor,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limite=limite
        )
        
        return JsonResponse(resultado, status=200)
        
    except Exception as e:
        logger.error(f"Error al listar compras: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}',
            'data': []
        }, status=500)


@api_view(['GET'])
def obtener_compra(request, id_compra):
    """
    Obtiene una compra específica con sus detalles
    
    GET /api/compras/{id_compra}/
    """
    try:
        resultado = compra_manager.obtenerCompra(id_compra)
        
        if resultado['success']:
            return JsonResponse(resultado, status=200)
        else:
            return JsonResponse(resultado, status=404)
            
    except Exception as e:
        logger.error(f"Error al obtener compra {id_compra}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=500)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cambiar_estado_compra(request, id_compra):
    """
    Cambia el estado de una compra
    
    PATCH /api/compras/{id_compra}/estado/
    Body: {"estado": "recibida"}
    
    Estados válidos: pendiente, recibida, cancelada
    """
    try:
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        if not nuevo_estado:
            return JsonResponse({
                'success': False,
                'message': 'El campo estado es requerido'
            }, status=400)
        
        resultado = compra_manager.cambiarEstadoCompra(id_compra, nuevo_estado)
        
        if resultado['success']:
            return JsonResponse(resultado, status=200)
        else:
            return JsonResponse(resultado, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido en el cuerpo de la solicitud'
        }, status=400)
    except Exception as e:
        logger.error(f"Error al cambiar estado de compra {id_compra}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_detalle_compra(request, id_compra):
    """
    Agrega un detalle a una compra existente
    
    POST /api/compras/{id_compra}/detalle/
    Body: {
        "id_insumo": 1,
        "cantidad": 10,
        "precio_unitario": 2.5
    }
    """
    try:
        data = json.loads(request.body)
        
        id_insumo = data.get('id_insumo')
        cantidad = data.get('cantidad')
        precio_unitario = data.get('precio_unitario')
        
        if not all([id_insumo, cantidad, precio_unitario]):
            return JsonResponse({
                'success': False,
                'message': 'id_insumo, cantidad y precio_unitario son requeridos'
            }, status=400)
        
        resultado = compra_manager.agregarDetalleCompra(
            id_compra=id_compra,
            id_insumo=id_insumo,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        
        if resultado['success']:
            return JsonResponse(resultado, status=201)
        else:
            return JsonResponse(resultado, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido en el cuerpo de la solicitud'
        }, status=400)
    except Exception as e:
        logger.error(f"Error al agregar detalle a compra {id_compra}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }, status=500)


@api_view(['GET'])
def listar_compras_por_proveedor(request, id_proveedor):
    """
    Lista todas las compras de un proveedor específico
    
    GET /api/compras/proveedor/{id_proveedor}/
    """
    try:
        limite = int(request.GET.get('limite', 100))
        
        resultado = compra_manager.listarCompras(
            id_proveedor=id_proveedor,
            limite=limite
        )
        
        return JsonResponse(resultado, status=200)
        
    except Exception as e:
        logger.error(f"Error al listar compras del proveedor {id_proveedor}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}',
            'data': []
        }, status=500)


@api_view(['GET'])
def obtener_historial_insumo(request, id_insumo):
    """
    Obtiene el historial de compras de un insumo
    
    GET /api/compras/insumo/{id_insumo}/historial/
    """
    try:
        limite = int(request.GET.get('limite', 50))
        
        resultado = compra_manager.obtenerHistorialInsumo(
            id_insumo=id_insumo,
            limite=limite
        )
        
        return JsonResponse(resultado, status=200)
        
    except Exception as e:
        logger.error(f"Error al obtener historial de insumo {id_insumo}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}',
            'data': []
        }, status=500)


@api_view(['GET'])
def listar_compras_por_estado(request):
    """
    Lista compras filtradas por estado
    
    GET /api/compras/estado/?estado=pendiente
    """
    try:
        estado = request.GET.get('estado')
        limite = int(request.GET.get('limite', 100))
        
        if not estado:
            return JsonResponse({
                'success': False,
                'message': 'El parámetro estado es requerido'
            }, status=400)
        
        resultado = compra_manager.listarCompras(
            estado=estado,
            limite=limite
        )
        
        return JsonResponse(resultado, status=200)
        
    except Exception as e:
        logger.error(f"Error al listar compras por estado: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}',
            'data': []
        }, status=500)
