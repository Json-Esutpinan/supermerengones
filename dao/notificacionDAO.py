#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from config import get_supabase_client

logger = logging.getLogger(__name__)


class NotificacionDAO:
    """
    DAO para gestión de notificaciones (HU16)
    """

    def __init__(self):
        self.supabase = get_supabase_client()

    def crear(self, notificacion):
        """Crea una nueva notificación para un cliente"""
        try:
            datos = notificacion.to_dict()
            if 'id_notificacion' in datos and datos['id_notificacion'] is None:
                datos.pop('id_notificacion')
            
            return self.supabase.table('notificacion').insert(datos).execute()
        except Exception as e:
            logger.error(f"Error al crear notificación: {str(e)}")
            raise

    def obtener_por_id(self, id_notificacion):
        """Obtiene una notificación por ID con datos del cliente"""
        try:
            return self.supabase.table('notificacion')\
                .select('*, cliente(id_cliente, usuario(nombre, email))')\
                .eq('id_notificacion', id_notificacion)\
                .execute()
        except Exception as e:
            logger.error(f"Error al obtener notificación: {str(e)}")
            raise

    def listar_por_cliente(self, id_cliente, solo_no_leidas=False, limite=50):
        """Lista notificaciones de un cliente"""
        try:
            query = self.supabase.table('notificacion')\
                .select('*')\
                .eq('id_cliente', id_cliente)
            
            if solo_no_leidas:
                query = query.eq('leida', False)
            
            return query.order('fecha', desc=True).limit(limite).execute()
        except Exception as e:
            logger.error(f"Error al listar notificaciones del cliente: {str(e)}")
            raise

    def contar_no_leidas(self, id_cliente):
        """Cuenta notificaciones no leídas de un cliente"""
        try:
            resp = self.supabase.table('notificacion')\
                .select('id_notificacion')\
                .eq('id_cliente', id_cliente)\
                .eq('leida', False)\
                .execute()
            return len(resp.data) if resp.data else 0
        except Exception as e:
            logger.error(f"Error al contar notificaciones no leídas: {str(e)}")
            raise

    def marcar_como_leida(self, id_notificacion):
        """Marca una notificación como leída"""
        try:
            return self.supabase.table('notificacion')\
                .update({"leida": True})\
                .eq('id_notificacion', id_notificacion)\
                .execute()
        except Exception as e:
            logger.error(f"Error al marcar notificación como leída: {str(e)}")
            raise

    def marcar_todas_leidas(self, id_cliente):
        """Marca todas las notificaciones de un cliente como leídas"""
        try:
            return self.supabase.table('notificacion')\
                .update({"leida": True})\
                .eq('id_cliente', id_cliente)\
                .eq('leida', False)\
                .execute()
        except Exception as e:
            logger.error(f"Error al marcar todas como leídas: {str(e)}")
            raise

    def eliminar(self, id_notificacion):
        """Elimina una notificación"""
        try:
            return self.supabase.table('notificacion')\
                .delete()\
                .eq('id_notificacion', id_notificacion)\
                .execute()
        except Exception as e:
            logger.error(f"Error al eliminar notificación: {str(e)}")
            raise

    def listar_todas(self, limite=100):
        """Lista todas las notificaciones (para administradores)"""
        try:
            return self.supabase.table('notificacion')\
                .select('*, cliente(id_cliente, usuario(nombre, email))')\
                .order('fecha', desc=True)\
                .limit(limite)\
                .execute()
        except Exception as e:
            logger.error(f"Error al listar todas las notificaciones: {str(e)}")
            raise

    # NUEVO: listado filtrado y paginado para panel admin
    def listar_admin_filtrado(self, sede=None, rol=None, leidas=None, page=1, page_size=25):
        """Lista notificaciones con filtros opcionales.

        Args:
            sede (int|None): filtra por sede del cliente (join implícito vía RPC o vista futura).
            rol (str|None): 'cliente' (otros roles futura extensión).
            leidas (bool|None): True solo leídas, False solo no leídas.
            page (int): página 1-based.
            page_size (int): tamaño página.
        """
        try:
            query = self.supabase.table('notificacion').select('*, cliente(id_cliente, usuario(nombre, email))')
            if rol == 'cliente':
                # ya filtramos por tener cliente asociado (todas son cliente actualmente)
                pass
            if leidas is True:
                query = query.eq('leida', True)
            elif leidas is False:
                query = query.eq('leida', False)
            # sede filtrado: requiere que tabla notificacion tenga id_cliente -> cliente -> sede
            if sede is not None:
                # Supabase no soporta eq profundo directo en embed, workaround: usar RPC en futuro.
                # Aquí intentamos filtrar por sede si la columna directa existe en notificacion (extensión futura).
                try:
                    query = query.eq('id_sede', sede)
                except Exception:
                    pass
            # Paginación
            if page < 1:
                page = 1
            start = (page - 1) * page_size
            end = start + page_size - 1
            query = query.order('fecha', desc=True).range(start, end)
            resp = query.execute()
            # Total aproximado (para simple paginación) - segunda consulta ligera
            total_resp = self.supabase.table('notificacion').select('id_notificacion', count='exact').execute()
            total = total_resp.count if hasattr(total_resp, 'count') else (len(total_resp.data) if total_resp.data else 0)
            return {'data': resp.data or [], 'page': page, 'page_size': page_size, 'total': total}
        except Exception as e:
            logger.error(f"Error en listar_admin_filtrado: {str(e)}")
            return {'data': [], 'page': page, 'page_size': page_size, 'total': 0, 'error': str(e)}
