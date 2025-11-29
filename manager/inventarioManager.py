#!/usr/bin/python
# -*- coding: utf-8 -*-

from dao.inventarioDAO import InventarioDAO
from dao.movimientoInventarioDAO import MovimientoInventarioDAO
from entidades.inventario import Inventario
from entidades.movimientoInventario import MovimientoInventario
from datetime import datetime


class InventarioManager:
    """
    Manager para la gestión de inventario con lógica de negocio
    """
    
    def __init__(self):
        """Constructor que inicializa los DAOs"""
        self.inventario_dao = InventarioDAO()
        self.movimiento_dao = MovimientoInventarioDAO()
    
    def obtenerInventarioPorSede(self, id_sede):
        """
        Obtiene todo el inventario de una sede
        
        Args:
            id_sede: ID de la sede
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'inventarios': list}
        """
        try:
            inventarios = self.inventario_dao.listar_por_sede(id_sede)
            
            return {
                'exito': True,
                'mensaje': f'Se encontraron {len(inventarios)} registros de inventario',
                'inventarios': inventarios
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al obtener inventario: {str(e)}',
                'inventarios': []
            }
    
    def obtenerInventarioPorInsumo(self, id_insumo):
        """
        Obtiene el inventario de un insumo en todas las sedes
        
        Args:
            id_insumo: ID del insumo
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'inventarios': list}
        """
        try:
            inventarios = self.inventario_dao.listar_por_insumo(id_insumo)
            
            return {
                'exito': True,
                'mensaje': f'Inventario del insumo en {len(inventarios)} sede(s)',
                'inventarios': inventarios
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al obtener inventario: {str(e)}',
                'inventarios': []
            }
    
    def obtenerStockBajo(self, id_sede=None, cantidad_minima=10):
        """
        Obtiene inventario con stock bajo
        
        Args:
            id_sede: ID de la sede (opcional)
            cantidad_minima: Umbral de stock mínimo
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'inventarios': list}
        """
        try:
            inventarios = self.inventario_dao.listar_stock_bajo(id_sede, cantidad_minima)
            
            return {
                'exito': True,
                'mensaje': f'{len(inventarios)} insumo(s) con stock bajo',
                'inventarios': inventarios
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al obtener stock bajo: {str(e)}',
                'inventarios': []
            }
    
    def registrarEntradaStock(self, id_insumo, id_sede, cantidad, motivo, id_usuario=None):
        """
        Registra una entrada de stock (compra, devolución, ajuste)
        
        Args:
            id_insumo: ID del insumo
            id_sede: ID de la sede
            cantidad: Cantidad a agregar
            motivo: Razón de la entrada
            id_usuario: ID del usuario que registra (opcional)
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'inventario': Inventario, 'movimiento': MovimientoInventario}
        """
        # Validaciones
        try:
            cantidad_int = int(cantidad)
            if cantidad_int <= 0:
                return {
                    'exito': False,
                    'mensaje': 'La cantidad debe ser mayor a 0',
                    'inventario': None,
                    'movimiento': None
                }
        except (ValueError, TypeError):
            return {
                'exito': False,
                'mensaje': 'La cantidad debe ser un número válido',
                'inventario': None,
                'movimiento': None
            }
        
        if not motivo or not motivo.strip():
            return {
                'exito': False,
                'mensaje': 'El motivo es requerido',
                'inventario': None,
                'movimiento': None
            }
        
        try:
            # Buscar o crear registro de inventario
            inventario = self.inventario_dao.obtener_por_insumo_y_sede(id_insumo, id_sede)
            
            if inventario:
                # Actualizar cantidad existente
                inventario_actualizado = self.inventario_dao.ajustar_cantidad(
                    inventario.id_inventario, 
                    cantidad_int, 
                    'sumar'
                )
            else:
                # Crear nuevo registro
                nuevo_inventario = Inventario(
                    id_insumo=id_insumo,
                    id_sede=id_sede,
                    cantidad=cantidad_int
                )
                inventario_actualizado = self.inventario_dao.crear(nuevo_inventario)
            
            if not inventario_actualizado:
                return {
                    'exito': False,
                    'mensaje': 'Error al actualizar inventario',
                    'inventario': None,
                    'movimiento': None
                }
            
            # Registrar movimiento
            movimiento = MovimientoInventario(
                id_inventario=inventario_actualizado.id_inventario,
                tipo='entrada',
                cantidad=cantidad_int,
                motivo=motivo.strip(),
                fecha=datetime.now(),
                id_usuario=id_usuario
            )
            
            movimiento_creado = self.movimiento_dao.crear(movimiento)
            
            return {
                'exito': True,
                'mensaje': f'Entrada registrada: {cantidad_int} unidades agregadas',
                'inventario': inventario_actualizado,
                'movimiento': movimiento_creado
            }
            
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al registrar entrada: {str(e)}',
                'inventario': None,
                'movimiento': None
            }
    
    def registrarSalidaStock(self, id_insumo, id_sede, cantidad, motivo, id_usuario=None):
        """
        Registra una salida de stock (producción, merma, ajuste)
        
        Args:
            id_insumo: ID del insumo
            id_sede: ID de la sede
            cantidad: Cantidad a restar
            motivo: Razón de la salida
            id_usuario: ID del usuario que registra (opcional)
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'inventario': Inventario, 'movimiento': MovimientoInventario}
        """
        # Validaciones
        try:
            cantidad_int = int(cantidad)
            if cantidad_int <= 0:
                return {
                    'exito': False,
                    'mensaje': 'La cantidad debe ser mayor a 0',
                    'inventario': None,
                    'movimiento': None
                }
        except (ValueError, TypeError):
            return {
                'exito': False,
                'mensaje': 'La cantidad debe ser un número válido',
                'inventario': None,
                'movimiento': None
            }
        
        if not motivo or not motivo.strip():
            return {
                'exito': False,
                'mensaje': 'El motivo es requerido',
                'inventario': None,
                'movimiento': None
            }
        
        try:
            # Verificar que existe inventario
            inventario = self.inventario_dao.obtener_por_insumo_y_sede(id_insumo, id_sede)
            
            if not inventario:
                return {
                    'exito': False,
                    'mensaje': 'No existe inventario para este insumo en la sede',
                    'inventario': None,
                    'movimiento': None
                }
            
            # Verificar stock suficiente
            if inventario.cantidad < cantidad_int:
                return {
                    'exito': False,
                    'mensaje': f'Stock insuficiente. Disponible: {inventario.cantidad}, Solicitado: {cantidad_int}',
                    'inventario': inventario,
                    'movimiento': None
                }
            
            # Actualizar cantidad
            inventario_actualizado = self.inventario_dao.ajustar_cantidad(
                inventario.id_inventario, 
                cantidad_int, 
                'restar'
            )
            
            if not inventario_actualizado:
                return {
                    'exito': False,
                    'mensaje': 'Error al actualizar inventario',
                    'inventario': None,
                    'movimiento': None
                }
            
            # Registrar movimiento
            movimiento = MovimientoInventario(
                id_inventario=inventario_actualizado.id_inventario,
                tipo='salida',
                cantidad=cantidad_int,
                motivo=motivo.strip(),
                fecha=datetime.now(),
                id_usuario=id_usuario
            )
            
            movimiento_creado = self.movimiento_dao.crear(movimiento)
            
            return {
                'exito': True,
                'mensaje': f'Salida registrada: {cantidad_int} unidades restadas',
                'inventario': inventario_actualizado,
                'movimiento': movimiento_creado
            }
            
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al registrar salida: {str(e)}',
                'inventario': None,
                'movimiento': None
            }
    
    def transferirInsumoEntreSedes(self, id_sede_origen, id_sede_destino, id_insumo, cantidad, id_usuario=None):
        """
        Transfiere insumo de una sede a otra
        
        Args:
            id_sede_origen: ID de la sede origen
            id_sede_destino: ID de la sede destino
            id_insumo: ID del insumo
            cantidad: Cantidad a transferir
            id_usuario: ID del usuario que registra
            
        Returns:
            dict: {'exito': bool, 'mensaje': str}
        """
        # Validaciones
        if id_sede_origen == id_sede_destino:
            return {
                'exito': False,
                'mensaje': 'La sede origen y destino no pueden ser la misma'
            }
        
        try:
            cantidad_int = int(cantidad)
            if cantidad_int <= 0:
                return {
                    'exito': False,
                    'mensaje': 'La cantidad debe ser mayor a 0'
                }
        except (ValueError, TypeError):
            return {
                'exito': False,
                'mensaje': 'La cantidad debe ser un número válido'
            }
        
        # Registrar salida en sede origen
        motivo_salida = f'Transferencia a sede {id_sede_destino}'
        resultado_salida = self.registrarSalidaStock(
            id_insumo, 
            id_sede_origen, 
            cantidad_int, 
            motivo_salida, 
            id_usuario
        )
        
        if not resultado_salida['exito']:
            return {
                'exito': False,
                'mensaje': f'Error en sede origen: {resultado_salida["mensaje"]}'
            }
        
        # Registrar entrada en sede destino
        motivo_entrada = f'Transferencia desde sede {id_sede_origen}'
        resultado_entrada = self.registrarEntradaStock(
            id_insumo, 
            id_sede_destino, 
            cantidad_int, 
            motivo_entrada, 
            id_usuario
        )
        
        if not resultado_entrada['exito']:
            # Rollback: devolver a sede origen
            self.registrarEntradaStock(
                id_insumo, 
                id_sede_origen, 
                cantidad_int, 
                'Reversión por error en transferencia', 
                id_usuario
            )
            return {
                'exito': False,
                'mensaje': f'Error en sede destino: {resultado_entrada["mensaje"]}'
            }
        
        return {
            'exito': True,
            'mensaje': f'Transferencia exitosa: {cantidad_int} unidades de sede {id_sede_origen} a sede {id_sede_destino}'
        }
    
    def obtenerHistorialMovimientos(self, id_sede=None, tipo=None, limite=100):
        """
        Obtiene el historial de movimientos con filtros
        
        Args:
            id_sede: ID de la sede (opcional)
            tipo: 'entrada' o 'salida' (opcional)
            limite: Número máximo de movimientos
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'movimientos': list}
        """
        try:
            if id_sede:
                movimientos = self.movimiento_dao.listar_por_sede(id_sede, tipo=tipo, limite=limite)
            elif tipo:
                movimientos = self.movimiento_dao.listar_por_tipo(tipo, limite=limite)
            else:
                movimientos = self.movimiento_dao.listar_todos(limite=limite)
            
            return {
                'exito': True,
                'mensaje': f'Se encontraron {len(movimientos)} movimientos',
                'movimientos': movimientos
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al obtener movimientos: {str(e)}',
                'movimientos': []
            }
    
    def verificarAlertasReposicion(self, id_sede=None):
        """
        Verifica alertas de reposición (stock bajo)
        
        Args:
            id_sede: ID de la sede (opcional, None para todas)
            
        Returns:
            dict: {'exito': bool, 'mensaje': str, 'alertas': list}
        """
        try:
            inventarios_bajo = self.inventario_dao.listar_stock_bajo(id_sede, cantidad_minima=10)
            
            alertas = []
            for inv in inventarios_bajo:
                alerta = {
                    'id_inventario': inv.id_inventario,
                    'id_insumo': inv.id_insumo,
                    'id_sede': inv.id_sede,
                    'cantidad_actual': inv.cantidad,
                    'nivel': 'critico' if inv.cantidad < 5 else 'bajo',
                    'mensaje': f'Stock bajo: {inv.cantidad} unidades'
                }
                if hasattr(inv, 'nombre_insumo'):
                    alerta['nombre_insumo'] = inv.nombre_insumo
                if hasattr(inv, 'nombre_sede'):
                    alerta['nombre_sede'] = inv.nombre_sede
                
                alertas.append(alerta)
            
            return {
                'exito': True,
                'mensaje': f'{len(alertas)} alerta(s) de reposición',
                'alertas': alertas
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al verificar alertas: {str(e)}',
                'alertas': []
            }

    def verificar_stock_disponible(self, id_insumo, id_sede, cantidad):
        """
        Verifica si existe stock suficiente de un insumo en una sede.

        Args:
            id_insumo: ID del insumo
            id_sede: ID de la sede
            cantidad: Cantidad solicitada

        Returns:
            bool: True si hay suficiente stock, False en caso contrario
        """
        try:
            cantidad_int = int(cantidad)
            if cantidad_int <= 0:
                return False
        except (TypeError, ValueError):
            return False

        try:
            inventario = self.inventario_dao.obtener_por_insumo_y_sede(id_insumo, id_sede)
            if not inventario:
                return False
            return int(inventario.cantidad) >= cantidad_int
        except Exception:
            return False
    
    def descontarStockPorPedido(self, id_pedido):
        """
        Descuenta stock de insumos según los productos de un pedido
        (Requiere consulta a detalle_pedido y producto_insumo)
        
        Args:
            id_pedido: ID del pedido
            
        Returns:
            dict: {'exito': bool, 'mensaje': str}
        """
        # TODO: Implementar cuando se tengan las relaciones producto-insumo
        return {
            'exito': False,
            'mensaje': 'Funcionalidad pendiente de implementación'
        }
