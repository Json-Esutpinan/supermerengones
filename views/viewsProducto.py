from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from config import get_supabase_client, TABLA_PRODUCTO

supabase = get_supabase_client()


@api_view(['GET'])
def listar_productos(request):
    """Lista productos desde la tabla indicada en config.

    Parámetros opcionales:
    - activo: 'true'|'false' (por defecto solo activos)
    - q: búsqueda por nombre (contains)
    """
    try:
        solo_activos = request.GET.get('activo', 'true').lower() == 'true'
        q = request.GET.get('q')

        query = supabase.table(TABLA_PRODUCTO).select('*')
        if solo_activos:
            query = query.eq('activo', True)
        if q:
            # usar ilike para búsqueda parcial (supabase/postgrest)
            query = query.ilike('nombre', f"%{q}%")

        resp = query.execute()

        data = resp.data if resp and getattr(resp, 'data', None) is not None else []

        return Response({
            'success': True,
            'message': f'Se encontraron {len(data)} producto(s)',
            'data': data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al listar productos: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_producto(request, id_producto):
    """Obtiene un producto por su ID."""
    try:
        resp = supabase.table(TABLA_PRODUCTO).select('*').eq('id_producto', id_producto).execute()
        if resp and resp.data:
            return Response({'success': True, 'message': 'Producto encontrado', 'data': resp.data[0]}, status=status.HTTP_200_OK)

        return Response({'success': False, 'message': 'Producto no encontrado', 'data': None}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'success': False, 'message': f'Error al obtener producto: {str(e)}', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
