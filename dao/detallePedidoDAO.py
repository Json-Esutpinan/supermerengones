#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from config import get_supabase_client

logger = logging.getLogger(__name__)


class DetallePedidoDAO:
    """DAO para gestionar líneas de detalle de pedidos."""

    def listar_por_pedido(self, id_pedido, limite=500):
        try:
            supabase = get_supabase_client()
            resp = supabase.table('detalle_pedido').select('*').eq('id_pedido', id_pedido).limit(limite).execute()
            lineas = resp.data or []
            # Enriquecer con nombres de producto
            producto_ids = sorted({int(l.get('id_producto')) for l in lineas if l.get('id_producto') is not None})
            nombres_map = {}
            if producto_ids:
                try:
                    prod_resp = supabase.table('producto').select('id_producto,nombre').in_('id_producto', producto_ids).execute()
                    for p in (prod_resp.data or []):
                        nombres_map[int(p.get('id_producto'))] = p.get('nombre')
                except Exception:
                    logger.exception('Error obteniendo nombres de productos')
            for l in lineas:
                pid = l.get('id_producto')
                l['producto_nombre'] = nombres_map.get(int(pid)) if pid is not None else None
            return type('Resp', (), {'success': True, 'data': lineas})
        except Exception as e:
            logger.exception('Error listar_por_pedido')
            return type('Resp', (), {'success': False, 'message': str(e), 'data': []})

    def agregar_linea(self, id_pedido, id_producto, cantidad, precio_unitario):
        try:
            supabase = get_supabase_client()
            row = {
                'id_pedido': int(id_pedido),
                'id_producto': int(id_producto),
                'cantidad': int(cantidad),
                'precio_unitario': float(precio_unitario),
                'subtotal': float(precio_unitario) * int(cantidad),
            }
            resp = supabase.table('detalle_pedido').insert(row).execute()
            return type('Resp', (), {'success': True, 'data': resp.data or []})
        except Exception as e:
            logger.exception('Error agregar_linea')
            return type('Resp', (), {'success': False, 'message': str(e)})

    def ventas_por_producto(self, fecha_inicio=None, fecha_fin=None):
        """Agregación simple: total cantidad y subtotal por id_producto en rango.

        Nota: si la base no soporta agregaciones directas aquí, se puede filtrar y sumar en Python.
        """
        try:
            supabase = get_supabase_client()
            q = supabase.table('detalle_pedido').select('*')
            if fecha_inicio:
                q = q.gte('fecha_creacion', fecha_inicio)
            if fecha_fin:
                q = q.lte('fecha_creacion', fecha_fin)
            resp = q.execute()
            rows = resp.data or []
            agg = {}
            for r in rows:
                pid = r.get('id_producto')
                cant = int(r.get('cantidad') or 0)
                sub = float(r.get('subtotal') or 0)
                if pid not in agg:
                    agg[pid] = {'id_producto': pid, 'cantidad_total': 0, 'subtotal_total': 0.0}
                agg[pid]['cantidad_total'] += cant
                agg[pid]['subtotal_total'] += sub
            return type('Resp', (), {'success': True, 'data': list(agg.values())})
        except Exception as e:
            logger.exception('Error ventas_por_producto')
            return type('Resp', (), {'success': False, 'message': str(e), 'data': []})