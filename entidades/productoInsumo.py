#!/usr/bin/python
# -*- coding: utf-8 -*-

class ProductoInsumo:
    """Relación producto -> insumo (receta / composición)."""

    def __init__(self, id_producto_insumo=None, id_producto=None, id_insumo=None, cantidad_necesaria=None):
        self.id_producto_insumo = id_producto_insumo
        self.id_producto = id_producto
        self.id_insumo = id_insumo
        # cantidad necesaria del insumo por unidad de producto (float para soportar fracciones)
        self.cantidad_necesaria = float(cantidad_necesaria) if cantidad_necesaria is not None else None

    def to_dict(self):
        return {
            'id_producto_insumo': self.id_producto_insumo,
            'id_producto': self.id_producto,
            'id_insumo': self.id_insumo,
            'cantidad_necesaria': self.cantidad_necesaria
        }

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return ProductoInsumo(
            id_producto_insumo=data.get('id_producto_insumo'),
            id_producto=data.get('id_producto'),
            id_insumo=data.get('id_insumo'),
            cantidad_necesaria=data.get('cantidad_necesaria')
        )

    def __repr__(self):
        return f"ProductoInsumo(id={self.id_producto_insumo}, producto={self.id_producto}, insumo={self.id_insumo}, cant={self.cantidad_necesaria})"
