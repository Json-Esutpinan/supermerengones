#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "tu-supabase-anon-key")

# Cliente de Supabase (singleton)
_supabase_client = None

def get_supabase_client():
    """
    Retorna una instancia única del cliente de Supabase
    Compatible con diferentes versiones del cliente
    """
    global _supabase_client
    if _supabase_client is None:
        try:
            # Intentar importar supabase
            from supabase import create_client, Client
            
            # Crear cliente sin parámetros adicionales para mayor compatibilidad
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            
        except Exception as e:
            print(f"Error al crear cliente de Supabase: {e}")
            print("\nIntenta reinstalar supabase:")
            print("pip uninstall supabase -y")
            print("pip install supabase==2.0.3")
            raise
    
    return _supabase_client

# Nombres de tablas
TABLA_PROVEEDOR = "proveedor"
TABLA_USUARIO = "usuario"
TABLA_CLIENTE = "cliente"
TABLA_EMPLEADO = "empleado"
TABLA_ADMINISTRADOR = "administrador"
TABLA_SEDE = "sede"
TABLA_PRODUCTO = "producto"
TABLA_INSUMO = "insumo"
TABLA_INVENTARIO = "inventario"
TABLA_PEDIDO = "pedido"
TABLA_COMPRA = "compra"
TABLA_DETALLE_PEDIDO = "detalle_pedido"
TABLA_DETALLE_COMPRA = "detalle_compra"
TABLA_MOVIMIENTO_INVENTARIO = "movimiento_inventario"
TABLA_PRODUCTO_INSUMO = "producto_insumo"
TABLA_RECLAMO = "reclamo"
TABLA_NOTIFICACION = "notificacion"
TABLA_TURNO = "turno"
TABLA_UNIDAD_MEDIDA = "unidad_medida"
TABLA_PROMOCION = "promocion"
TABLA_PROMOCION_PRODUCTO = "promocion_producto"
