#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from manager.insumoManager import InsumoManager

insumo_manager = InsumoManager()


@api_view(['POST'])
def crear_insumo(request):
    """Crea un nuevo insumo
    POST /api/insumos/crear/
    Body: { codigo, nombre, id_unidad, id_sede, descripcion?, stock_minimo? }
    """
    try:
        datos = request.data
        resultado = insumo_manager.crearInsumo(
            codigo=datos.get('codigo'),
            nombre=datos.get('nombre'),
            id_unidad=datos.get('id_unidad'),
            id_sede=datos.get('id_sede'),
            descripcion=datos.get('descripcion'),
            stock_minimo=datos.get('stock_minimo', 0)
        )
        if resultado.get('exito'):
            insumo = resultado.get('insumo')
            return Response({
                'success': True,
                'message': resultado.get('mensaje'),
                'data': insumo.to_dict() if hasattr(insumo, 'to_dict') and insumo else None
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'message': resultado.get('mensaje'), 'data': None}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'message': f'Error al crear insumo: {str(e)}', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_insumos(request):
    """Lista insumos activos, opcionalmente filtrados por id_sede
    GET /api/insumos/?id_sede=1
    """
    try:
        id_sede = request.query_params.get('id_sede')
        id_sede = int(id_sede) if id_sede is not None else None
        insumos = insumo_manager.listarInsumosActivos(id_sede=id_sede)
        insumos_dict = [i.to_dict() if hasattr(i, 'to_dict') else i for i in insumos]
        return Response({'success': True, 'message': 'Insumos encontrados', 'data': insumos_dict}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': f'Error al listar insumos: {str(e)}', 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_insumo(request, id_insumo: int):
    """Obtiene un insumo por ID
    GET /api/insumos/{id_insumo}/
    """
    try:
        insumo = insumo_manager.obtenerInsumoPorId(id_insumo)
        if insumo:
            return Response({'success': True, 'message': 'Insumo encontrado', 'data': insumo.to_dict() if hasattr(insumo, 'to_dict') else None}, status=status.HTTP_200_OK)
        return Response({'success': False, 'message': 'Insumo no encontrado', 'data': None}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'message': f'Error al obtener insumo: {str(e)}', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
def modificar_insumo(request, id_insumo: int):
    """Modifica un insumo
    PUT/PATCH /api/insumos/{id_insumo}/modificar/
    Body: campos a actualizar
    """
    try:
        datos = request.data
        resultado = insumo_manager.modificarInsumo(id_insumo, **datos)
        if resultado.get('exito'):
            insumo = resultado.get('insumo')
            return Response({'success': True, 'message': resultado.get('mensaje'), 'data': insumo.to_dict() if hasattr(insumo, 'to_dict') else None}, status=status.HTTP_200_OK)
        codigo = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado.get('mensaje', '').lower() else status.HTTP_400_BAD_REQUEST
        return Response({'success': False, 'message': resultado.get('mensaje'), 'data': None}, status=codigo)
    except Exception as e:
        return Response({'success': False, 'message': f'Error al modificar insumo: {str(e)}', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def desactivar_insumo(request, id_insumo: int):
    """Desactiva (eliminación lógica) un insumo
    DELETE /api/insumos/{id_insumo}/
    """
    try:
        resultado = insumo_manager.desactivarInsumo(id_insumo)
        if resultado.get('exito'):
            return Response({'success': True, 'message': resultado.get('mensaje'), 'data': None}, status=status.HTTP_200_OK)
        codigo = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado.get('mensaje', '').lower() else status.HTTP_400_BAD_REQUEST
        return Response({'success': False, 'message': resultado.get('mensaje'), 'data': None}, status=codigo)
    except Exception as e:
        return Response({'success': False, 'message': f'Error al desactivar insumo: {str(e)}', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
