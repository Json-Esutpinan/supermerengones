#!/usr/bin/python
# -*- coding: utf-8 -*-

from dao.proveedorDAO import ProveedorDAO
from entidades.proveedor import Proveedor
import re

class ProveedorManager:
    def __init__(self):
        self.dao = ProveedorDAO()

    def crearProveedor(self, nombre, email, telefono, direccion):
        """
        Crea un nuevo proveedor con validaciones
        
        Args:
            nombre: Nombre del proveedor (requerido)
            email: Email del proveedor (opcional pero debe ser válido)
            telefono: Teléfono del proveedor (opcional)
            direccion: Dirección del proveedor (opcional)
            
        Returns:
            dict con 'success' (bool), 'message' (str) y 'data' (Proveedor o None)
        """
        # Validar nombre (requerido)
        if not nombre or not nombre.strip():
            return {
                'success': False,
                'message': 'El nombre es requerido',
                'data': None
            }
        
        # Validar longitud del nombre
        if len(nombre) > 100:
            return {
                'success': False,
                'message': 'El nombre no puede exceder 100 caracteres',
                'data': None
            }
        
        # Validar email si se proporciona
        if email and email.strip():
            if not self._validar_email(email):
                return {
                    'success': False,
                    'message': 'El formato del email es inválido',
                    'data': None
                }
            
            # Verificar que el email no esté en uso
            if self.dao.existe_email(email):
                return {
                    'success': False,
                    'message': 'Ya existe un proveedor con ese email',
                    'data': None
                }
        
        # Validar teléfono
        if telefono and len(telefono) > 20:
            return {
                'success': False,
                'message': 'El teléfono no puede exceder 20 caracteres',
                'data': None
            }
        
        # Validar dirección
        if direccion and len(direccion) > 255:
            return {
                'success': False,
                'message': 'La dirección no puede exceder 255 caracteres',
                'data': None
            }
        
        # Crear el proveedor
        nuevo_proveedor = Proveedor(
            nombre=nombre.strip(),
            email=email.strip() if email else None,
            telefono=telefono.strip() if telefono else None,
            direccion=direccion.strip() if direccion else None,
            activo=True
        )
        
        # Insertar en la base de datos
        proveedor_creado = self.dao.insertar(nuevo_proveedor)
        
        if proveedor_creado:
            return {
                'success': True,
                'message': 'Proveedor creado exitosamente',
                'data': proveedor_creado
            }
        else:
            return {
                'success': False,
                'message': 'Error al crear el proveedor en la base de datos',
                'data': None
            }

    def modificarProveedor(self, id_proveedor, data):
        """
        Modifica un proveedor existente
        
        Args:
            id_proveedor: ID del proveedor a modificar
            data: Diccionario con los campos a actualizar
            
        Returns:
            dict con 'success' (bool), 'message' (str) y 'data' (Proveedor o None)
        """
        # Validar que el proveedor existe
        proveedor_existente = self.dao.obtener_por_id(id_proveedor)
        if not proveedor_existente:
            return {
                'success': False,
                'message': 'Proveedor no encontrado',
                'data': None
            }
        
        # Validar los datos a actualizar
        datos_actualizacion = {}
        
        if 'nombre' in data:
            nombre = data['nombre']
            if not nombre or not nombre.strip():
                return {
                    'success': False,
                    'message': 'El nombre no puede estar vacío',
                    'data': None
                }
            if len(nombre) > 100:
                return {
                    'success': False,
                    'message': 'El nombre no puede exceder 100 caracteres',
                    'data': None
                }
            datos_actualizacion['nombre'] = nombre.strip()
        
        if 'email' in data:
            email = data['email']
            if email and email.strip():
                if not self._validar_email(email):
                    return {
                        'success': False,
                        'message': 'El formato del email es inválido',
                        'data': None
                    }
                # Verificar que el email no esté en uso por otro proveedor
                if self.dao.existe_email(email, excluir_id=id_proveedor):
                    return {
                        'success': False,
                        'message': 'Ya existe otro proveedor con ese email',
                        'data': None
                    }
                datos_actualizacion['email'] = email.strip()
            else:
                datos_actualizacion['email'] = None
        
        if 'telefono' in data:
            telefono = data['telefono']
            if telefono and len(telefono) > 20:
                return {
                    'success': False,
                    'message': 'El teléfono no puede exceder 20 caracteres',
                    'data': None
                }
            datos_actualizacion['telefono'] = telefono.strip() if telefono else None
        
        if 'direccion' in data:
            direccion = data['direccion']
            if direccion and len(direccion) > 255:
                return {
                    'success': False,
                    'message': 'La dirección no puede exceder 255 caracteres',
                    'data': None
                }
            datos_actualizacion['direccion'] = direccion.strip() if direccion else None
        
        if 'activo' in data:
            datos_actualizacion['activo'] = bool(data['activo'])
        
        # Actualizar en la base de datos
        proveedor_actualizado = self.dao.actualizar(id_proveedor, datos_actualizacion)
        
        if proveedor_actualizado:
            return {
                'success': True,
                'message': 'Proveedor actualizado exitosamente',
                'data': proveedor_actualizado
            }
        else:
            return {
                'success': False,
                'message': 'Error al actualizar el proveedor',
                'data': None
            }

    def listarProveedores(self, solo_activos=True):
        """
        Lista todos los proveedores
        
        Args:
            solo_activos: Si es True, solo retorna proveedores activos
            
        Returns:
            dict con 'success' (bool), 'message' (str) y 'data' (lista de Proveedores)
        """
        try:
            proveedores = self.dao.listar_todos(solo_activos=solo_activos)
            
            return {
                'success': True,
                'message': f'Se encontraron {len(proveedores)} proveedor(es)',
                'data': proveedores
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al listar proveedores: {str(e)}',
                'data': []
            }

    def obtenerProveedor(self, id_proveedor):
        """
        Obtiene un proveedor por su ID
        
        Args:
            id_proveedor: ID del proveedor
            
        Returns:
            dict con 'success' (bool), 'message' (str) y 'data' (Proveedor o None)
        """
        proveedor = self.dao.obtener_por_id(id_proveedor)
        
        if proveedor:
            return {
                'success': True,
                'message': 'Proveedor encontrado',
                'data': proveedor
            }
        else:
            return {
                'success': False,
                'message': 'Proveedor no encontrado',
                'data': None
            }

    def cambiarEstadoProveedor(self, id_proveedor, activo):
        """
        Cambia el estado de un proveedor (activar/desactivar)
        
        Args:
            id_proveedor: ID del proveedor
            activo: True para activar, False para desactivar
            
        Returns:
            dict con 'success' (bool), 'message' (str) y 'data' (Proveedor)
        """
        # Verificar que el proveedor existe
        proveedor = self.dao.obtener_por_id(id_proveedor)
        if not proveedor:
            return {
                'success': False,
                'message': 'Proveedor no encontrado',
                'data': None
            }
        
        # Verificar si ya está en el estado solicitado
        if proveedor.activo == activo:
            estado_actual = "activo" if activo else "inactivo"
            return {
                'success': False,
                'message': f'El proveedor ya está {estado_actual}',
                'data': None
            }
        
        # Cambiar el estado
        proveedor_actualizado = self.dao.actualizar(id_proveedor, {'activo': activo})
        
        if proveedor_actualizado:
            accion = "activado" if activo else "desactivado"
            return {
                'success': True,
                'message': f'Proveedor {accion} exitosamente',
                'data': proveedor_actualizado
            }
        else:
            return {
                'success': False,
                'message': 'Error al cambiar el estado del proveedor',
                'data': None
            }
    
    def desactivarProveedor(self, id_proveedor):
        """
        Desactiva un proveedor (atajo para cambiarEstadoProveedor)
        
        Args:
            id_proveedor: ID del proveedor a desactivar
            
        Returns:
            dict con 'success' (bool), 'message' (str) y 'data' (Proveedor)
        """
        return self.cambiarEstadoProveedor(id_proveedor, False)
    
    def activarProveedor(self, id_proveedor):
        """
        Activa un proveedor (atajo para cambiarEstadoProveedor)
        
        Args:
            id_proveedor: ID del proveedor a activar
            
        Returns:
            dict con 'success' (bool), 'message' (str) y 'data' (Proveedor)
        """
        return self.cambiarEstadoProveedor(id_proveedor, True)

    def buscarProveedores(self, nombre):
        """
        Busca proveedores por nombre
        
        Args:
            nombre: Texto a buscar en el nombre
            
        Returns:
            dict con 'success' (bool), 'message' (str) y 'data' (lista de Proveedores)
        """
        if not nombre or not nombre.strip():
            return {
                'success': False,
                'message': 'Debe proporcionar un nombre para buscar',
                'data': []
            }
        
        proveedores = self.dao.buscar_por_nombre(nombre.strip())
        
        return {
            'success': True,
            'message': f'Se encontraron {len(proveedores)} proveedor(es)',
            'data': proveedores
        }

    def _validar_email(self, email):
        """
        Valida el formato de un email
        
        Args:
            email: Email a validar
            
        Returns:
            True si el formato es válido, False en caso contrario
        """
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
