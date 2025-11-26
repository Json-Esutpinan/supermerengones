#!/usr/bin/python
# -*- coding: utf-8 -*-

from dao.reclamoDAO import ReclamoDAO
from datetime import datetime


class ReclamoManager:
    """
    Gestión de Reclamos - HU19
    """
    
    def __init__(self):
        self.dao = ReclamoDAO()
    
    def crearReclamo(self, id_pedido, id_cliente, descripcion):
        """
        Crea un nuevo reclamo
        
        Args:
            id_pedido: ID del pedido asociado
            id_cliente: ID del cliente que hace el reclamo
            descripcion: Descripción del reclamo
            
        Returns:
            dict con 'success', 'message' y 'data'
        """
        try:
            # Validaciones
            if not descripcion or len(descripcion.strip()) < 10:
                return {
                    'success': False,
                    'message': 'La descripción debe tener al menos 10 caracteres',
                    'data': None
                }
            
            if len(descripcion) > 1000:
                return {
                    'success': False,
                    'message': 'La descripción no puede exceder 1000 caracteres',
                    'data': None
                }
            
            # Crear reclamo
            reclamo_data = {
                'id_pedido': id_pedido,
                'id_cliente': id_cliente,
                'descripcion': descripcion.strip(),
                'estado': 'abierto'
            }
            
            reclamo = self.dao.insertar(reclamo_data)
            
            if reclamo:
                return {
                    'success': True,
                    'message': 'Reclamo creado exitosamente',
                    'data': reclamo
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al crear el reclamo',
                    'data': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al crear reclamo: {str(e)}',
                'data': None
            }
    
    def obtenerReclamo(self, id_reclamo):
        """
        Obtiene un reclamo por su ID
        
        Args:
            id_reclamo: ID del reclamo
            
        Returns:
            dict con 'success', 'message' y 'data'
        """
        try:
            reclamo = self.dao.obtener_por_id(id_reclamo)
            
            if reclamo:
                return {
                    'success': True,
                    'message': 'Reclamo encontrado',
                    'data': reclamo
                }
            else:
                return {
                    'success': False,
                    'message': 'Reclamo no encontrado',
                    'data': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al obtener reclamo: {str(e)}',
                'data': None
            }
    
    def listarReclamosCliente(self, id_cliente):
        """
        Lista todos los reclamos de un cliente
        
        Args:
            id_cliente: ID del cliente
            
        Returns:
            dict con 'success', 'message' y 'data'
        """
        try:
            reclamos = self.dao.listar_por_cliente(id_cliente)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(reclamos)} reclamos',
                'data': reclamos
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al listar reclamos: {str(e)}',
                'data': []
            }
    
    def listarReclamosPedido(self, id_pedido):
        """
        Lista todos los reclamos de un pedido
        
        Args:
            id_pedido: ID del pedido
            
        Returns:
            dict con 'success', 'message' y 'data'
        """
        try:
            reclamos = self.dao.listar_por_pedido(id_pedido)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(reclamos)} reclamos',
                'data': reclamos
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al listar reclamos: {str(e)}',
                'data': []
            }
    
    def listarReclamosPorEstado(self, estado):
        """
        Lista reclamos por estado
        
        Args:
            estado: Estado del reclamo (abierto, en_revision, resuelto, cerrado)
            
        Returns:
            dict con 'success', 'message' y 'data'
        """
        try:
            estados_validos = ['abierto', 'en_revision', 'resuelto', 'cerrado']
            if estado not in estados_validos:
                return {
                    'success': False,
                    'message': f'Estado inválido. Debe ser uno de: {", ".join(estados_validos)}',
                    'data': []
                }
            
            reclamos = self.dao.listar_por_estado(estado)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(reclamos)} reclamos con estado {estado}',
                'data': reclamos
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al listar reclamos: {str(e)}',
                'data': []
            }
    
    def listarTodosReclamos(self, limite=100):
        """
        Lista todos los reclamos
        
        Args:
            limite: Número máximo de reclamos
            
        Returns:
            dict con 'success', 'message' y 'data'
        """
        try:
            reclamos = self.dao.listar_todos(limite)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(reclamos)} reclamos',
                'data': reclamos
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al listar reclamos: {str(e)}',
                'data': []
            }
    
    def cambiarEstadoReclamo(self, id_reclamo, nuevo_estado):
        """
        Cambia el estado de un reclamo
        
        Args:
            id_reclamo: ID del reclamo
            nuevo_estado: Nuevo estado
            
        Returns:
            dict con 'success', 'message' y 'data'
        """
        try:
            estados_validos = ['abierto', 'en_revision', 'resuelto', 'cerrado']
            if nuevo_estado not in estados_validos:
                return {
                    'success': False,
                    'message': f'Estado inválido. Debe ser uno de: {", ".join(estados_validos)}',
                    'data': None
                }
            
            # Verificar que el reclamo existe
            reclamo = self.dao.obtener_por_id(id_reclamo)
            if not reclamo:
                return {
                    'success': False,
                    'message': 'Reclamo no encontrado',
                    'data': None
                }
            
            # Si se está resolviendo o cerrando, agregar fecha de resolución
            fecha_resolucion = None
            if nuevo_estado in ['resuelto', 'cerrado'] and not reclamo.fecha_resolucion:
                fecha_resolucion = datetime.now().isoformat()
            
            reclamo_actualizado = self.dao.cambiar_estado(id_reclamo, nuevo_estado, fecha_resolucion)
            
            if reclamo_actualizado:
                return {
                    'success': True,
                    'message': f'Estado del reclamo cambiado a {nuevo_estado}',
                    'data': reclamo_actualizado
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al cambiar el estado del reclamo',
                    'data': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al cambiar estado: {str(e)}',
                'data': None
            }
    
    def agregarRespuesta(self, id_reclamo, respuesta):
        """
        Agrega una respuesta/comentario al reclamo
        
        Args:
            id_reclamo: ID del reclamo
            respuesta: Texto de la respuesta
            
        Returns:
            dict con 'success', 'message' y 'data'
        """
        try:
            # Verificar que el reclamo existe
            reclamo = self.dao.obtener_por_id(id_reclamo)
            if not reclamo:
                return {
                    'success': False,
                    'message': 'Reclamo no encontrado',
                    'data': None
                }
            
            # Validar respuesta
            if not respuesta or len(respuesta.strip()) < 10:
                return {
                    'success': False,
                    'message': 'La respuesta debe tener al menos 10 caracteres',
                    'data': None
                }
            
            # Actualizar descripción agregando la respuesta
            nueva_descripcion = f"{reclamo.descripcion}\n\n--- RESPUESTA ---\n{respuesta.strip()}"
            
            datos = {
                'descripcion': nueva_descripcion,
                'estado': 'en_revision'  # Cambiar estado a en_revision
            }
            
            reclamo_actualizado = self.dao.actualizar(id_reclamo, datos)
            
            if reclamo_actualizado:
                return {
                    'success': True,
                    'message': 'Respuesta agregada exitosamente',
                    'data': reclamo_actualizado
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al agregar respuesta',
                    'data': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al agregar respuesta: {str(e)}',
                'data': None
            }
