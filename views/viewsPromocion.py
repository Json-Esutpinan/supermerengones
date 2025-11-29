from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from config import get_supabase_client
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

supabase = get_supabase_client()



@api_view(['GET'])
def listar_promociones(request):
    """Lista promociones activas desde la tabla 'promocion'."""
    try:
        solo_activos = request.GET.get('activo', 'true').lower() == 'true'
        q = request.GET.get('q')

        query = supabase.table('promocion').select('*')
        if solo_activos:
            query = query.eq('activo', True)
        if q:
            try:
                query = query.ilike('titulo', f"%{q}%")
            except Exception:
                pass

        resp = query.execute()
        data = resp.data if resp and getattr(resp, 'data', None) is not None else []

        return Response({'success': True, 'message': f'Se encontraron {len(data)} promoción(es)', 'data': data},
                        status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'message': str(e), 'data': []},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_promocion(request, id_promocion):
    """Obtiene una promoción con sus productos relacionados."""
    try:
        resp = supabase.table('promocion').select('*').eq('id_promocion', id_promocion).execute()
        if resp and resp.data:
            promo = resp.data[0]
            # Obtener productos relacionados si existe la tabla
            try:
                rel = supabase.table('promocion_producto').select('id_producto').eq('id_promocion', id_promocion).execute()
                producto_ids = [r['id_producto'] for r in (rel.data or [])]
                # Obtener detalles de productos
                if producto_ids:
                    prod_resp = supabase.table('producto').select('*').in_('id_producto', producto_ids).execute()
                    promo['productos'] = prod_resp.data or []
                else:
                    promo['productos'] = []
            except Exception:
                promo['productos'] = []

            return Response({'success': True, 'message': 'Promoción encontrada', 'data': promo},
                            status=status.HTTP_200_OK)

        return Response({'success': False, 'message': 'Promoción no encontrada', 'data': None},
                        status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'success': False, 'message': str(e), 'data': None},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= Administrador =============

@api_view(['POST'])
@login_required
def crear_promocion(request):
    """Crea una promoción (requiere estar autenticado como admin)."""
    try:
        datos = request.data
        if not datos.get('titulo'):
            return Response({'success': False, 'message': 'Título requerido'}, status=status.HTTP_400_BAD_REQUEST)

        promo_data = {
            'titulo': datos.get('titulo'),
            'descripcion': datos.get('descripcion'),
            'tipo': datos.get('tipo', 'descuento_porcentaje'),
            'valor': datos.get('valor'),
            'imagen_url': datos.get('imagen_url'),
            'fecha_inicio': datos.get('fecha_inicio'),
            'fecha_fin': datos.get('fecha_fin'),
            'activo': datos.get('activo', True),
        }

        resp = supabase.table('promocion').insert(promo_data).execute()
        if resp and resp.data:
            # Asociar productos si se envían
            producto_ids = datos.get('producto_ids', [])
            if producto_ids:
                for pid in producto_ids:
                    try:
                        supabase.table('promocion_producto').insert({
                            'id_promocion': resp.data[0]['id_promocion'],
                            'id_producto': pid
                        }).execute()
                    except Exception:
                        pass

            return Response({'success': True, 'message': 'Promoción creada', 'data': resp.data[0]},
                            status=status.HTTP_201_CREATED)

        return Response({'success': False, 'message': 'Error al crear promoción'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@login_required
def modificar_promocion(request, id_promocion):
    """Modifica una promoción existente."""
    try:
        resp = supabase.table('promocion').update(request.data).eq('id_promocion', id_promocion).execute()
        if resp and resp.data:
            return Response({'success': True, 'message': 'Promoción actualizada', 'data': resp.data[0]},
                            status=status.HTTP_200_OK)

        return Response({'success': False, 'message': 'Promoción no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@login_required
def eliminar_promocion(request, id_promocion):
    """Elimina una promoción."""
    try:
        resp = supabase.table('promocion').delete().eq('id_promocion', id_promocion).execute()
        return Response({'success': True, 'message': 'Promoción eliminada'},
                        status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
