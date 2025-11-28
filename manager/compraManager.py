#!/usr/bin/python
# -*- coding: utf-8 -*-

from dao.compraDAO import CompraDAO
from dao.detalleCompraDAO import DetalleCompraDAO
from dao.proveedorDAO import ProveedorDAO
from entidades.compra import Compra
from entidades.detalleCompra import DetalleCompra
from manager.inventarioManager import InventarioManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CompraManager:
    """
    Manager para la gestión de compras a proveedores con integración al inventario
    """
    
    def __init__(self):
        self.compra_dao = CompraDAO()
        self.detalle_dao = DetalleCompraDAO()
        self.proveedor_dao = ProveedorDAO()
        self.inventario_manager = InventarioManager()
    
    def crearCompra(self, id_proveedor, id_usuario, detalles, registrar_en_inventario=True, id_sede=None):
        """
        Crea una compra completa con sus detalles y registra entradas en inventario
        
        Args:
            id_proveedor: ID del proveedor
            id_usuario: ID del usuario que registra la compra
            detalles: Lista de dict [{'id_insumo': int, 'cantidad': float, 'precio_unitario': float}]
            registrar_en_inventario: Si True, registra automáticamente las entradas en inventario
            id_sede: ID de la sede donde se registra el inventario (requerido si registrar_en_inventario=True)
        
        Returns:
            dict: {'success': bool, 'message': str, 'data': {...}}
        """
        try:
            # Validaciones
            if not id_proveedor or not id_usuario:
                return {
                    'success': False,
                    'message': 'Proveedor y usuario son requeridos'
                }
            
            if not detalles or len(detalles) == 0:
                return {
                    'success': False,
                    'message': 'Debe incluir al menos un detalle de compra'
                }
            
            if registrar_en_inventario and not id_sede:
                return {
                    'success': False,
                    'message': 'Debe especificar la sede para registrar en inventario'
                }
            
            # Verificar que el proveedor existe y está activo
            proveedor = self.proveedor_dao.obtenerPorId(id_proveedor)
            if not proveedor:
                return {
                    'success': False,
                    'message': f'El proveedor con ID {id_proveedor} no existe'
                }
            
            if not proveedor.get('activo', False):
                return {
                    'success': False,
                    'message': f'El proveedor {proveedor.get("nombre")} está inactivo'
                }
            
            # Calcular total de la compra
            total = 0.0
            detalles_validados = []
            
            for detalle in detalles:
                # Validar campos
                if 'id_insumo' not in detalle or 'cantidad' not in detalle or 'precio_unitario' not in detalle:
                    return {
                        'success': False,
                        'message': 'Cada detalle debe incluir id_insumo, cantidad y precio_unitario'
                    }
                
                try:
                    cantidad = float(detalle['cantidad'])
                    precio_unitario = float(detalle['precio_unitario'])
                except (ValueError, TypeError):
                    return {
                        'success': False,
                        'message': 'Cantidad y precio_unitario deben ser numéricos'
                    }
                
                # Validar valores positivos
                if cantidad <= 0:
                    return {
                        'success': False,
                        'message': 'La cantidad debe ser mayor a 0'
                    }
                
                if precio_unitario < 0:
                    return {
                        'success': False,
                        'message': 'El precio unitario no puede ser negativo'
                    }
                
                # Calcular subtotal
                subtotal = cantidad * precio_unitario
                total += subtotal
                
                detalles_validados.append({
                    'id_insumo': detalle['id_insumo'],
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal
                })
            
            # Crear la compra
            compra = Compra(
                id_proveedor=id_proveedor,
                id_usuario=id_usuario,
                fecha=datetime.now(),
                total=total,
                estado='pendiente'
            )
            
            id_compra = self.compra_dao.crear(compra)
            
            if not id_compra:
                return {
                    'success': False,
                    'message': 'Error al crear la compra en la base de datos'
                }
            
            # Crear los detalles
            detalles_creados = []
            for det in detalles_validados:
                detalle_obj = DetalleCompra(
                    id_compra=id_compra,
                    id_insumo=det['id_insumo'],
                    cantidad=det['cantidad'],
                    precio_unitario=det['precio_unitario'],
                    subtotal=det['subtotal']
                )
                
                id_detalle = self.detalle_dao.crear(detalle_obj)
                if id_detalle:
                    detalles_creados.append({
                        'id_detalle_compra': id_detalle,
                        'id_insumo': det['id_insumo'],
                        'cantidad': det['cantidad'],
                        'precio_unitario': det['precio_unitario'],
                        'subtotal': det['subtotal']
                    })
            
            # Registrar entradas en inventario si se solicita
            inventario_registrado = []
            if registrar_en_inventario:
                for det in detalles_validados:
                    resultado = self.inventario_manager.registrarEntradaStock(
                        id_insumo=det['id_insumo'],
                        id_sede=id_sede,
                        cantidad=det['cantidad'],
                        motivo=f"Compra #{id_compra} - Proveedor: {proveedor.get('nombre')}",
                        id_usuario=id_usuario
                    )
                    # Compatibilidad: InventarioManager retorna claves 'exito' y 'inventario' al nivel raíz
                    ok = (resultado.get('success') is True) or (resultado.get('exito') is True)
                    if ok:
                        inv_obj = resultado.get('inventario')
                        if inv_obj is None:
                            inv_obj = resultado.get('data', {}).get('inventario')
                        inventario_registrado.append({
                            'id_insumo': det['id_insumo'],
                            'cantidad': det['cantidad'],
                            'inventario': inv_obj
                        })
            
            # Actualizar estado si todo fue exitoso
            if registrar_en_inventario and len(inventario_registrado) == len(detalles_validados):
                self.compra_dao.actualizar_estado(id_compra, 'recibida')
            
            return {
                'success': True,
                'message': 'Compra registrada exitosamente',
                'data': {
                    'id_compra': id_compra,
                    'id_proveedor': id_proveedor,
                    'nombre_proveedor': proveedor.get('nombre'),
                    'total': total,
                    'estado': 'recibida' if registrar_en_inventario else 'pendiente',
                    'detalles': detalles_creados,
                    'inventario_actualizado': len(inventario_registrado) > 0,
                    'items_en_inventario': len(inventario_registrado)
                }
            }
            
        except Exception as e:
            logger.error(f"Error al crear compra: {str(e)}")
            return {
                'success': False,
                'message': f'Error al crear compra: {str(e)}'
            }
    
    def obtenerCompra(self, id_compra):
        """
        Obtiene una compra con sus detalles
        
        Args:
            id_compra: ID de la compra
            
        Returns:
            dict: {'success': bool, 'message': str, 'data': {...}}
        """
        try:
            compra = self.compra_dao.obtener_por_id(id_compra)
            
            if not compra:
                return {
                    'success': False,
                    'message': f'Compra {id_compra} no encontrada'
                }
            
            # Obtener detalles
            detalles = self.detalle_dao.listar_por_compra(id_compra)
            compra['detalles'] = detalles
            
            return {
                'success': True,
                'message': 'Compra obtenida exitosamente',
                'data': compra
            }
            
        except Exception as e:
            logger.error(f"Error al obtener compra {id_compra}: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener compra: {str(e)}'
            }
    
    def listarCompras(self, estado=None, id_proveedor=None, fecha_desde=None, fecha_hasta=None, limite=100):
        """
        Lista compras con filtros opcionales
        
        Args:
            estado: Filtrar por estado (pendiente, recibida, cancelada)
            id_proveedor: Filtrar por proveedor
            fecha_desde: Fecha inicial (formato ISO o datetime)
            fecha_hasta: Fecha final (formato ISO o datetime)
            limite: Número máximo de resultados
            
        Returns:
            dict: {'success': bool, 'message': str, 'data': [...]}
        """
        try:
            if estado:
                compras = self.compra_dao.listar_por_estado(estado, limite)
            elif id_proveedor:
                compras = self.compra_dao.listar_por_proveedor(id_proveedor, limite)
            elif fecha_desde or fecha_hasta:
                compras = self.compra_dao.listar_por_fecha(fecha_desde, fecha_hasta, limite)
            else:
                compras = self.compra_dao.listar_todas(limite)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(compras)} compras',
                'data': compras
            }
            
        except Exception as e:
            logger.error(f"Error al listar compras: {str(e)}")
            return {
                'success': False,
                'message': f'Error al listar compras: {str(e)}',
                'data': []
            }
    
    def cambiarEstadoCompra(self, id_compra, nuevo_estado):
        """
        Cambia el estado de una compra
        
        Args:
            id_compra: ID de la compra
            nuevo_estado: Nuevo estado (pendiente, recibida, cancelada)
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Validar estado
            estados_validos = ['pendiente', 'recibida', 'cancelada']
            if nuevo_estado not in estados_validos:
                return {
                    'success': False,
                    'message': f'Estado inválido. Use: {", ".join(estados_validos)}'
                }
            
            # Verificar que la compra existe
            compra = self.compra_dao.obtener_por_id(id_compra)
            if not compra:
                return {
                    'success': False,
                    'message': f'Compra {id_compra} no encontrada'
                }
            
            # Actualizar estado
            if self.compra_dao.actualizar_estado(id_compra, nuevo_estado):
                return {
                    'success': True,
                    'message': f'Estado actualizado a {nuevo_estado}'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al actualizar el estado'
                }
                
        except Exception as e:
            logger.error(f"Error al cambiar estado de compra {id_compra}: {str(e)}")
            return {
                'success': False,
                'message': f'Error al cambiar estado: {str(e)}'
            }
    
    def agregarDetalleCompra(self, id_compra, id_insumo, cantidad, precio_unitario):
        """
        Agrega un detalle a una compra existente
        
        Args:
            id_compra: ID de la compra
            id_insumo: ID del insumo
            cantidad: Cantidad comprada
            precio_unitario: Precio por unidad
            
        Returns:
            dict: {'success': bool, 'message': str, 'data': {...}}
        """
        try:
            # Validaciones
            if cantidad <= 0:
                return {
                    'success': False,
                    'message': 'La cantidad debe ser mayor a 0'
                }
            
            if precio_unitario < 0:
                return {
                    'success': False,
                    'message': 'El precio unitario no puede ser negativo'
                }
            
            # Verificar que la compra existe
            compra = self.compra_dao.obtener_por_id(id_compra)
            if not compra:
                return {
                    'success': False,
                    'message': f'Compra {id_compra} no encontrada'
                }
            
            # Calcular subtotal
            subtotal = float(cantidad) * float(precio_unitario)
            
            # Crear detalle
            detalle = DetalleCompra(
                id_compra=id_compra,
                id_insumo=id_insumo,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
            
            id_detalle = self.detalle_dao.crear(detalle)
            
            if not id_detalle:
                return {
                    'success': False,
                    'message': 'Error al crear el detalle'
                }
            
            # Recalcular y actualizar el total de la compra
            nuevo_total = self.detalle_dao.calcular_total_compra(id_compra)
            self.compra_dao.actualizar_total(id_compra, nuevo_total)
            
            return {
                'success': True,
                'message': 'Detalle agregado exitosamente',
                'data': {
                    'id_detalle_compra': id_detalle,
                    'id_insumo': id_insumo,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal,
                    'nuevo_total_compra': nuevo_total
                }
            }
            
        except Exception as e:
            logger.error(f"Error al agregar detalle a compra {id_compra}: {str(e)}")
            return {
                'success': False,
                'message': f'Error al agregar detalle: {str(e)}'
            }
    
    def obtenerHistorialInsumo(self, id_insumo, limite=50):
        """
        Obtiene el historial de compras de un insumo específico
        
        Args:
            id_insumo: ID del insumo
            limite: Número máximo de resultados
            
        Returns:
            dict: {'success': bool, 'message': str, 'data': [...]}
        """
        try:
            historial = self.detalle_dao.listar_por_insumo(id_insumo, limite)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(historial)} compras del insumo',
                'data': historial
            }
            
        except Exception as e:
            logger.error(f"Error al obtener historial de insumo {id_insumo}: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener historial: {str(e)}',
                'data': []
            }
