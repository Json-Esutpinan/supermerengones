#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from manager.inventarioManager import InventarioManager


inventario_manager = InventarioManager()


@api_view(['GET'])
def listar_inventario_por_sede(request, id_sede):
    """
    Lista todo el inventario de una sede específica
    """
    try:
        resultado = inventario_manager.obtenerInventarioPorSede(id_sede)
        
        inventarios_list = [inv.to_dict() for inv in resultado['inventarios']]
        
        # Agregar información adicional si existe
        for i, inv in enumerate(resultado['inventarios']):
            if hasattr(inv, 'nombre_insumo'):
                inventarios_list[i]['nombre_insumo'] = inv.nombre_insumo
            if hasattr(inv, 'nombre_unidad'):
                inventarios_list[i]['nombre_unidad'] = inv.nombre_unidad
            if hasattr(inv, 'abreviatura_unidad'):
                inventarios_list[i]['abreviatura_unidad'] = inv.abreviatura_unidad
        
        return Response({
            'success': resultado['exito'],
            'message': resultado['mensaje'],
            'data': inventarios_list
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al listar inventario: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_inventario_por_insumo(request, id_insumo):
    """
    Lista el inventario de un insumo en todas las sedes
    """
    try:
        resultado = inventario_manager.obtenerInventarioPorInsumo(id_insumo)
        
        inventarios_list = [inv.to_dict() for inv in resultado['inventarios']]
        
        # Agregar nombre de sede si existe
        for i, inv in enumerate(resultado['inventarios']):
            if hasattr(inv, 'nombre_sede'):
                inventarios_list[i]['nombre_sede'] = inv.nombre_sede
        
        return Response({
            'success': resultado['exito'],
            'message': resultado['mensaje'],
            'data': inventarios_list
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al listar inventario: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_stock_bajo(request):
    """
    Lista inventario con stock bajo
    
    Query params:
    - id_sede: ID de la sede (opcional)
    - minimo: Cantidad mínima (default: 10)
    """
    try:
        id_sede = request.GET.get('id_sede')
        cantidad_minima = int(request.GET.get('minimo', 10))
        
        if id_sede:
            id_sede = int(id_sede)
        
        resultado = inventario_manager.obtenerStockBajo(id_sede, cantidad_minima)
        
        inventarios_list = [inv.to_dict() for inv in resultado['inventarios']]
        
        # Agregar información adicional
        for i, inv in enumerate(resultado['inventarios']):
            if hasattr(inv, 'nombre_insumo'):
                inventarios_list[i]['nombre_insumo'] = inv.nombre_insumo
            if hasattr(inv, 'nombre_sede'):
                inventarios_list[i]['nombre_sede'] = inv.nombre_sede
        
        return Response({
            'success': resultado['exito'],
            'message': resultado['mensaje'],
            'data': inventarios_list
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al listar stock bajo: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_entrada_stock(request):
    """
    Registra una entrada de stock
    
    Body (JSON):
    {
        "id_insumo": 1,
        "id_sede": 1,
        "cantidad": 50,
        "motivo": "Compra a proveedor"
    }
    """
    try:
        datos = request.data
        
        # Validar campos requeridos
        campos_requeridos = ['id_insumo', 'id_sede', 'cantidad', 'motivo']
        for campo in campos_requeridos:
            if campo not in datos:
                return Response({
                    'success': False,
                    'message': f'El campo {campo} es requerido',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener ID de usuario desde request (si está autenticado)
        id_usuario = request.user.id if hasattr(request.user, 'id') else None
        
        resultado = inventario_manager.registrarEntradaStock(
            id_insumo=datos['id_insumo'],
            id_sede=datos['id_sede'],
            cantidad=datos['cantidad'],
            motivo=datos['motivo'],
            id_usuario=id_usuario
        )
        
        if resultado['exito']:
            response_data = {
                'inventario': resultado['inventario'].to_dict() if resultado['inventario'] else None,
                'movimiento': resultado['movimiento'].to_dict() if resultado['movimiento'] else None
            }
            
            return Response({
                'success': True,
                'message': resultado['mensaje'],
                'data': response_data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': resultado['mensaje'],
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al registrar entrada: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_salida_stock(request):
    """
    Registra una salida de stock
    
    Body (JSON):
    {
        "id_insumo": 1,
        "id_sede": 1,
        "cantidad": 20,
        "motivo": "Producción"
    }
    """
    try:
        datos = request.data
        
        # Validar campos requeridos
        campos_requeridos = ['id_insumo', 'id_sede', 'cantidad', 'motivo']
        for campo in campos_requeridos:
            if campo not in datos:
                return Response({
                    'success': False,
                    'message': f'El campo {campo} es requerido',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener ID de usuario desde request
        id_usuario = request.user.id if hasattr(request.user, 'id') else None
        
        resultado = inventario_manager.registrarSalidaStock(
            id_insumo=datos['id_insumo'],
            id_sede=datos['id_sede'],
            cantidad=datos['cantidad'],
            motivo=datos['motivo'],
            id_usuario=id_usuario
        )
        
        if resultado['exito']:
            response_data = {
                'inventario': resultado['inventario'].to_dict() if resultado['inventario'] else None,
                'movimiento': resultado['movimiento'].to_dict() if resultado['movimiento'] else None
            }
            
            return Response({
                'success': True,
                'message': resultado['mensaje'],
                'data': response_data
            }, status=status.HTTP_201_CREATED)
        
        status_code = status.HTTP_404_NOT_FOUND if 'No existe inventario' in resultado['mensaje'] else status.HTTP_400_BAD_REQUEST
        
        return Response({
            'success': False,
            'message': resultado['mensaje'],
            'data': None
        }, status=status_code)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al registrar salida: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transferir_entre_sedes(request):
    """
    Transfiere insumo de una sede a otra
    
    Body (JSON):
    {
        "id_sede_origen": 1,
        "id_sede_destino": 2,
        "id_insumo": 1,
        "cantidad": 30
    }
    """
    try:
        datos = request.data
        
        # Validar campos requeridos
        campos_requeridos = ['id_sede_origen', 'id_sede_destino', 'id_insumo', 'cantidad']
        for campo in campos_requeridos:
            if campo not in datos:
                return Response({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener ID de usuario desde request
        id_usuario = request.user.id if hasattr(request.user, 'id') else None
        
        resultado = inventario_manager.transferirInsumoEntreSedes(
            id_sede_origen=datos['id_sede_origen'],
            id_sede_destino=datos['id_sede_destino'],
            id_insumo=datos['id_insumo'],
            cantidad=datos['cantidad'],
            id_usuario=id_usuario
        )
        
        if resultado['exito']:
            return Response({
                'success': True,
                'message': resultado['mensaje']
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': resultado['mensaje']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al transferir: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_historial_movimientos(request):
    """
    Obtiene historial de movimientos de inventario
    
    Query params:
    - id_sede: ID de la sede (opcional)
    - tipo: 'entrada' o 'salida' (opcional)
    - limite: Número máximo de movimientos (default: 100)
    """
    try:
        id_sede = request.GET.get('id_sede')
        tipo = request.GET.get('tipo')
        limite = int(request.GET.get('limite', 100))
        
        if id_sede:
            id_sede = int(id_sede)
        
        resultado = inventario_manager.obtenerHistorialMovimientos(id_sede, tipo, limite)
        
        movimientos_list = [mov.to_dict() for mov in resultado['movimientos']]
        
        # Agregar información adicional
        for i, mov in enumerate(resultado['movimientos']):
            if hasattr(mov, 'nombre_insumo'):
                movimientos_list[i]['nombre_insumo'] = mov.nombre_insumo
            if hasattr(mov, 'nombre_sede'):
                movimientos_list[i]['nombre_sede'] = mov.nombre_sede
        
        return Response({
            'success': resultado['exito'],
            'message': resultado['mensaje'],
            'data': movimientos_list
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener historial: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_alertas_reposicion(request):
    """
    Obtiene alertas de reposición (stock bajo)
    
    Query params:
    - id_sede: ID de la sede (opcional)
    """
    try:
        id_sede = request.GET.get('id_sede')
        
        if id_sede:
            id_sede = int(id_sede)
        
        resultado = inventario_manager.verificarAlertasReposicion(id_sede)
        
        return Response({
            'success': resultado['exito'],
            'message': resultado['mensaje'],
            'data': resultado['alertas']
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener alertas: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def verificar_stock_disponible(request, id_insumo):
    """
    Verifica si existe stock suficiente de un insumo en una sede.

    Query params:
    - id_sede: ID de la sede (requerido)
    - cantidad: cantidad solicitada (requerido)
    """
    try:
        id_sede = request.GET.get('id_sede')
        cantidad = request.GET.get('cantidad')

        if id_sede is None or cantidad is None:
            return Response({
                'success': False,
                'message': 'Los parámetros "id_sede" y "cantidad" son requeridos',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        disponible = inventario_manager.verificar_stock_disponible(id_insumo, id_sede, cantidad)

        return Response({
            'success': True,
            'message': 'Verificación realizada',
            'data': { 'disponible': bool(disponible) }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al verificar stock: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
