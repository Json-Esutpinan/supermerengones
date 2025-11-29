#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import get_supabase_client, TABLA_PRODUCTO_INSUMO
from entidades.productoInsumo import ProductoInsumo


class ProductoInsumoDAO:
    """DAO para la tabla producto_insumo (recetas / composición de productos)."""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.tabla = TABLA_PRODUCTO_INSUMO

    # CRUD BÁSICO -----------------------------------------------------------
    def insertar(self, item):
        """Inserta una relación producto-insumo.

        Args:
            item (ProductoInsumo | dict)
        Returns:
            ProductoInsumo o None
        """
        try:
            data = item.to_dict() if hasattr(item, 'to_dict') else dict(item)
            # quitar id para autogeneración si viene None
            if data.get('id_producto_insumo') is None:
                data.pop('id_producto_insumo', None)
            resp = self.supabase.table(self.tabla).insert(data).execute()
            if resp.data:
                return ProductoInsumo.from_dict(resp.data[0])
            return None
        except Exception as e:
            print(f"Error insertar producto_insumo: {e}")
            return None

    def obtener_por_id(self, id_producto_insumo):
        try:
            resp = self.supabase.table(self.tabla).select('*').eq('id_producto_insumo', id_producto_insumo).execute()
            if resp.data:
                return ProductoInsumo.from_dict(resp.data[0])
            return None
        except Exception as e:
            print(f"Error obtener producto_insumo por id: {e}")
            return None

    def listar_por_producto(self, id_producto):
        """Lista todos los insumos asociados a un producto."""
        try:
            resp = self.supabase.table(self.tabla).select('*').eq('id_producto', id_producto).order('id_insumo').execute()
            return [ProductoInsumo.from_dict(r) for r in resp.data] if resp.data else []
        except Exception as e:
            print(f"Error listar insumos de producto: {e}")
            return []

    def listar_por_insumo(self, id_insumo):
        """Lista todos los productos que utilizan un insumo."""
        try:
            resp = self.supabase.table(self.tabla).select('*').eq('id_insumo', id_insumo).order('id_producto').execute()
            return [ProductoInsumo.from_dict(r) for r in resp.data] if resp.data else []
        except Exception as e:
            print(f"Error listar productos por insumo: {e}")
            return []

    def actualizar(self, id_producto_insumo, datos):
        """Actualiza la cantidad necesaria u otras columnas permitidas."""
        try:
            permitidos = {'cantidad_necesaria', 'id_producto', 'id_insumo'}
            update_data = {k: v for k, v in datos.items() if k in permitidos}
            if 'cantidad_necesaria' in update_data:
                update_data['cantidad_necesaria'] = float(update_data['cantidad_necesaria'])
            resp = self.supabase.table(self.tabla).update(update_data).eq('id_producto_insumo', id_producto_insumo).execute()
            if resp.data:
                return ProductoInsumo.from_dict(resp.data[0])
            return None
        except Exception as e:
            print(f"Error actualizar producto_insumo: {e}")
            return None

    def eliminar(self, id_producto_insumo):
        try:
            resp = self.supabase.table(self.tabla).delete().eq('id_producto_insumo', id_producto_insumo).execute()
            return bool(resp.data)
        except Exception as e:
            print(f"Error eliminar producto_insumo: {e}")
            return False

    # OPERACIONES MAS COMPLETAS ---------------------------------------------
    def reemplazar_insumos_de_producto(self, id_producto, lista_insumos):
        """Reemplaza toda la 'receta' del producto.

        Args:
            id_producto (int)
            lista_insumos (list[dict]): cada dict con keys 'id_insumo','cantidad_necesaria'
        Returns:
            list[ProductoInsumo] nueva lista o [] si error
        """
        try:
            # eliminar actuales
            self.supabase.table(self.tabla).delete().eq('id_producto', id_producto).execute()
            # Normalizar: merge duplicados y filtrar cantidades inválidas
            acumulados = {}
            for item in lista_insumos:
                iid = item.get('id_insumo')
                cant = item.get('cantidad_necesaria')
                if iid is None:
                    continue
                try:
                    cant_f = float(cant)
                except Exception:
                    continue
                # Ignorar no positivos
                if cant_f <= 0:
                    continue
                acumulados[iid] = acumulados.get(iid, 0.0) + cant_f

            # preparar nuevos registros únicos
            bulk = []
            for iid, cant_f in acumulados.items():
                bulk.append({
                    'id_producto': id_producto,
                    'id_insumo': iid,
                    'cantidad_necesaria': cant_f
                })
            if not bulk:
                return []
            resp = self.supabase.table(self.tabla).insert(bulk).execute()
            return [ProductoInsumo.from_dict(r) for r in resp.data] if resp.data else []
        except Exception as e:
            print(f"Error reemplazar insumos del producto: {e}")
            return []

    def obtener_receta_producto(self, id_producto):
        """Alias semántico."""
        return self.listar_por_producto(id_producto)

    # UTILITY ---------------------------------------------------------------
    def calcular_total_insumos(self, id_producto):
        """Retorna suma de cantidades_necesarias (útil para validaciones)."""
        try:
            receta = self.listar_por_producto(id_producto)
            return sum(r.cantidad_necesaria for r in receta if r.cantidad_necesaria is not None)
        except Exception:
            return 0.0

    def calcular_costo_producto(self, id_producto, costos_insumos):
        """Calcula costo estimado del producto dada la receta y costos de insumos.

        Args:
            id_producto (int)
            costos_insumos (dict): {id_insumo: costo_unitario}

        Returns:
            float costo_total (None si receta vacía)

        Nota: costos_insumos debe llegar desde lógica externa (p.e. promedio últimas compras).
        """
        try:
            receta = self.listar_por_producto(id_producto)
            if not receta:
                return None
            total = 0.0
            for r in receta:
                costo_unit = costos_insumos.get(r.id_insumo)
                if costo_unit is not None and r.cantidad_necesaria is not None:
                    total += costo_unit * r.cantidad_necesaria
            return total
        except Exception:
            return None