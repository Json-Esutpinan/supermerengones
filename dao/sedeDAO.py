#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client
from entidades.sede import Sede

class SedeDAO:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.tabla = "sede"

    def crear(self, sede: Sede):
        data = {
            "nombre": sede.nombre,
            "direccion": sede.direccion,
            "telefono": sede.telefono,
            "activo": sede.activo
        }
        resp = self.supabase.table(self.tabla).insert(data).execute()
        return resp

    def obtener(self, id_sede: int):
        return self.supabase.table(self.tabla).select("*").eq("id_sede", id_sede).execute()

    def listar(self, solo_activos=True):
        query = self.supabase.table(self.tabla).select("*")
        if solo_activos:
            query = query.eq("activo", True)
        return query.execute()

    def modificar(self, id_sede: int, cambios: dict):
        return self.supabase.table(self.tabla).update(cambios).eq("id_sede", id_sede).execute()

    def desactivar(self, id_sede: int):
        return self.supabase.table(self.tabla).update({"activo": False}).eq("id_sede", id_sede).execute()
