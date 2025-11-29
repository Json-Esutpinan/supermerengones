#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

class Promocion:
    """
    Entidad que representa una promoción en el sistema
    """
    
    def __init__(self, id_promocion=None, titulo=None, descripcion=None, 
                 descripcion_corta=None, tipo=None, valor=0.0, imagen_url=None,
                 fecha_inicio=None, fecha_fin=None, activo=True, 
                 created_at=None, updated_at=None):
        """
        Constructor de Promocion
        
        Args:
            id_promocion: ID único de la promoción
            titulo: Título de la promoción
            descripcion: Descripción completa
            descripcion_corta: Descripción resumida
            tipo: Tipo de promoción (descuento_porcentaje, descuento_monto, combo)
            valor: Valor del descuento (porcentaje o monto)
            imagen_url: URL de la imagen promocional
            fecha_inicio: Fecha de inicio de la promoción
            fecha_fin: Fecha de finalización
            activo: Si la promoción está activa
            created_at: Fecha de creación
            updated_at: Fecha de última actualización
        """
        self.id_promocion = id_promocion
        self.titulo = titulo
        self.descripcion = descripcion
        self.descripcion_corta = descripcion_corta
        self.tipo = tipo
        self.valor = float(valor) if valor else 0.0
        self.imagen_url = imagen_url
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.activo = activo
        self.created_at = created_at
        self.updated_at = updated_at
        
        # Lista de productos asociados (se carga por separado)
        self.productos = []
    
    def to_dict(self):
        """
        Convierte la promoción a diccionario
        
        Returns:
            dict con los datos de la promoción
        """
        return {
            'id_promocion': self.id_promocion,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'descripcion_corta': self.descripcion_corta,
            'tipo': self.tipo,
            'valor': float(self.valor),
            'imagen_url': self.imagen_url,
            'fecha_inicio': self.fecha_inicio.isoformat() if isinstance(self.fecha_inicio, datetime) else self.fecha_inicio,
            'fecha_fin': self.fecha_fin.isoformat() if isinstance(self.fecha_fin, datetime) else self.fecha_fin,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'productos': self.productos
        }
    
    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Promocion desde un diccionario
        
        Args:
            data: diccionario con los datos de la promoción
            
        Returns:
            Objeto Promocion
        """
        return Promocion(
            id_promocion=data.get('id_promocion'),
            titulo=data.get('titulo'),
            descripcion=data.get('descripcion'),
            descripcion_corta=data.get('descripcion_corta'),
            tipo=data.get('tipo'),
            valor=data.get('valor', 0.0),
            imagen_url=data.get('imagen_url'),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            activo=data.get('activo', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def esta_vigente(self):
        """
        Verifica si la promoción está vigente (dentro del rango de fechas)
        
        Returns:
            bool: True si está vigente
        """
        if not self.activo:
            return False
        
        ahora = datetime.now()
        
        # Si no tiene fecha_inicio, se considera que ya empezó
        if self.fecha_inicio:
            inicio = self.fecha_inicio if isinstance(self.fecha_inicio, datetime) else datetime.fromisoformat(self.fecha_inicio)
            if ahora < inicio:
                return False
        
        # Si no tiene fecha_fin, no caduca
        if self.fecha_fin:
            fin = self.fecha_fin if isinstance(self.fecha_fin, datetime) else datetime.fromisoformat(self.fecha_fin)
            if ahora > fin:
                return False
        
        return True
    
    def calcular_descuento(self, monto):
        """
        Calcula el descuento aplicable según el tipo de promoción
        
        Args:
            monto: Monto original
            
        Returns:
            float: Monto del descuento
        """
        if not self.esta_vigente():
            return 0.0
        
        if self.tipo == 'descuento_porcentaje':
            return monto * (self.valor / 100.0)
        elif self.tipo == 'descuento_monto':
            return self.valor
        elif self.tipo == 'combo':
            # Para combos, la lógica se maneja en el manager
            return 0.0
        
        return 0.0
    
    def __str__(self):
        return f"Promoción: {self.titulo} - {self.tipo} ({self.valor})"
    
    def __repr__(self):
        return f"Promocion(id={self.id_promocion}, titulo='{self.titulo}', tipo='{self.tipo}', valor={self.valor})"
