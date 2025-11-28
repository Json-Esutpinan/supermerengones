from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from manager.sedeManager import SedeManager

sede_manager = SedeManager()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_sede(request):
    """
    Crea una nueva sede
    """
    try:
        datos = request.data

        if 'nombre' not in datos:
            return Response({
                'success': False,
                'message': 'El campo nombre es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        resultado = sede_manager.crearSede(
            nombre=datos.get("nombre"),
            direccion=datos.get("direccion"),
            telefono=datos.get("telefono"),
        )

        if resultado['success']:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado.get('data') else None
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'message': resultado['message']
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': f"Error al procesar la solicitud: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_sedes(request):
    """
    Lista todas las sedes
    """
    try:
        solo_activos = request.GET.get('todos', 'false').lower() != 'true'

        resultado = sede_manager.listarSedes(solo_activos=solo_activos)

        if resultado['success']:
            sedes_dict = [s.to_dict() for s in resultado['data']]
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': sedes_dict
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': resultado['message'],
            'data': []
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f"Error al procesar la solicitud: {str(e)}",
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_sede(request, id_sede):
    """
    Obtiene una sede por ID
    """
    try:
        resultado = sede_manager.obtenerSede(id_sede)

        if resultado["success"]:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado.get('data') else None
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': resultado['message'],
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'message': f"Error al procesar la solicitud: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def modificar_sede(request, id_sede):
    """
    Modifica una sede existente
    """
    try:
        resultado = sede_manager.modificarSede(id_sede, request.data)

        if resultado["success"]:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado.get('data') else None
            }, status=status.HTTP_200_OK)

        codigo_estado = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'].lower() else status.HTTP_400_BAD_REQUEST
        
        return Response({
            'success': False,
            'message': resultado['message'],
            'data': None
        }, status=codigo_estado)

    except Exception as e:
        return Response({
            'success': False,
            'message': f"Error al procesar la solicitud: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def desactivar_sede(request, id_sede):
    """
    Desactiva una sede
    """
    try:
        resultado = sede_manager.desactivarSede(id_sede)

        if resultado["success"]:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado.get('data') else None
            }, status=status.HTTP_200_OK)

        codigo_estado = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'].lower() else status.HTTP_400_BAD_REQUEST

        return Response({
            'success': False,
            'message': resultado['message'],
            'data': None
        }, status=codigo_estado)

    except Exception as e:
        return Response({
            'success': False,
            'message': f"Error al procesar la solicitud: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cambiar_estado_sede(request, id_sede):
    """
    Cambia el estado de una sede (activo/inactivo)
    
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
                'message': 'El campo "activo" es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(activo, bool):
            return Response({
                'success': False,
                'message': 'El campo "activo" debe ser true o false'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = sede_manager.cambiarEstado(id_sede, activo)
        
        if resultado["success"]:
            return Response({
                'success': True,
                'message': resultado['message'],
                'data': resultado['data'].to_dict() if resultado.get('data') else None
            }, status=status.HTTP_200_OK)
        
        codigo_estado = status.HTTP_404_NOT_FOUND if 'no encontrado' in resultado['message'].lower() else status.HTTP_400_BAD_REQUEST
        
        return Response({
            'success': False,
            'message': resultado['message'],
            'data': None
        }, status=codigo_estado)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f"Error al procesar la solicitud: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def vista_consolidada_sede(request, id_sede):
    """
    Retorna la vista consolidada de la sede
    """
    try:
        filtro = request.GET.get("filtro", None)
        resultado = sede_manager.vistaConsolidada(id_sede, filtro)

        if resultado["success"]:
            data = resultado.get("data")

            if isinstance(data, list):
                data = [d.to_dict() if hasattr(d, "to_dict") else d for d in data]
            elif hasattr(data, "to_dict"):
                data = data.to_dict()

            return Response({
                'success': True,
                'message': resultado['message'],
                'data': data
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': resultado['message'],
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': f"Error al procesar la solicitud: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
