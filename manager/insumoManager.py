#!/usr/bin/python
# -*- coding: utf-8 -*-

from dao.insumoDAO import InsumoDAO
from entidades.insumo import Insumo


class InsumoManager:
    """
    Gestión de Insumos
    """
    
    def __init__(self):
        self.dao = InsumoDAO()
    
    def crearInsumo(self, codigo, nombre, id_unidad, id_sede, descripcion=None, stock_minimo=0):
        """
        Crea un nuevo insumo
        
        Args:
            codigo: Código único del insumo
            nombre: Nombre del insumo
            id_unidad: ID de la unidad de medida
            id_sede: ID de la sede
            descripcion: Descripción opcional
            stock_minimo: Stock mínimo requerido
            
        Returns:
            dict con 'exito', 'mensaje' y 'insumo'
        """
        try:
            # Validaciones
            if not codigo or not nombre or not id_unidad or not id_sede:
                return {
                    'exito': False,
                    'mensaje': 'Código, nombre, unidad y sede son requeridos',
                    'insumo': None
                }
            
            if len(codigo.strip()) < 3:
                return {
                    'exito': False,
                    'mensaje': 'El código debe tener al menos 3 caracteres',
                    'insumo': None
                }
            
            if len(nombre.strip()) < 3:
                return {
                    'exito': False,
                    'mensaje': 'El nombre debe tener al menos 3 caracteres',
                    'insumo': None
                }
            
            # Crear insumo
            insumo = Insumo(
                codigo=codigo.strip(),
                nombre=nombre.strip(),
                descripcion=descripcion.strip() if descripcion else None,
                id_unidad=id_unidad,
                id_sede=id_sede,
                stock_minimo=stock_minimo,
                activo=True
            )
            
            resultado = self.dao.insertar(insumo)
            
            if resultado:
                return {
                    'exito': True,
                    'mensaje': 'Insumo creado exitosamente',
                    'insumo': resultado
                }
            else:
                return {
                    'exito': False,
                    'mensaje': 'Error al crear insumo en la base de datos',
                    'insumo': None
                }
                
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al crear insumo: {str(e)}',
                'insumo': None
            }
    
    def listarInsumosActivos(self, id_sede=None):
        """
        Lista insumos activos, opcionalmente filtrados por sede
        
        Args:
            id_sede: ID de sede opcional para filtrar
            
        Returns:
            Lista de insumos activos
        """
        try:
            if id_sede:
                return self.dao.listar_por_sede(id_sede, solo_activos=True)
            else:
                return self.dao.listar_todos(solo_activos=True)
        except Exception as e:
            print(f"Error al listar insumos: {e}")
            return []
    
    def obtenerInsumoPorId(self, id_insumo):
        """
        Obtiene un insumo por su ID
        
        Args:
            id_insumo: ID del insumo
            
        Returns:
            Objeto Insumo o None
        """
        try:
            return self.dao.obtener_por_id(id_insumo)
        except Exception as e:
            print(f"Error al obtener insumo: {e}")
            return None
    
    def modificarInsumo(self, id_insumo, **kwargs):
        """
        Modifica un insumo existente
        
        Args:
            id_insumo: ID del insumo
            **kwargs: Campos a actualizar (nombre, descripcion, stock_minimo, etc.)
            
        Returns:
            dict con 'exito', 'mensaje' y 'insumo'
        """
        try:
            # Verificar que el insumo existe
            insumo = self.dao.obtener_por_id(id_insumo)
            if not insumo:
                return {
                    'exito': False,
                    'mensaje': 'Insumo no encontrado',
                    'insumo': None
                }
            
            # Preparar datos para actualizar
            datos = {}
            
            if 'nombre' in kwargs and kwargs['nombre']:
                if len(kwargs['nombre'].strip()) < 3:
                    return {
                        'exito': False,
                        'mensaje': 'El nombre debe tener al menos 3 caracteres',
                        'insumo': None
                    }
                datos['nombre'] = kwargs['nombre'].strip()
            
            if 'descripcion' in kwargs:
                datos['descripcion'] = kwargs['descripcion'].strip() if kwargs['descripcion'] else None
            
            if 'stock_minimo' in kwargs:
                datos['stock_minimo'] = kwargs['stock_minimo']
            
            if 'id_unidad' in kwargs:
                datos['id_unidad'] = kwargs['id_unidad']
            
            if not datos:
                return {
                    'exito': False,
                    'mensaje': 'No hay datos para actualizar',
                    'insumo': None
                }
            
            # Actualizar
            resultado = self.dao.actualizar(id_insumo, datos)
            
            if resultado:
                return {
                    'exito': True,
                    'mensaje': 'Insumo actualizado exitosamente',
                    'insumo': resultado
                }
            else:
                return {
                    'exito': False,
                    'mensaje': 'Error al actualizar insumo',
                    'insumo': None
                }
                
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al modificar insumo: {str(e)}',
                'insumo': None
            }
    
    def desactivarInsumo(self, id_insumo):
        """
        Desactiva un insumo (soft delete)
        
        Args:
            id_insumo: ID del insumo
            
        Returns:
            dict con 'exito' y 'mensaje'
        """
        try:
            # Verificar que existe
            insumo = self.dao.obtener_por_id(id_insumo)
            if not insumo:
                return {
                    'exito': False,
                    'mensaje': 'Insumo no encontrado'
                }
            
            # Desactivar
            resultado = self.dao.cambiar_estado(id_insumo, False)
            
            if resultado:
                return {
                    'exito': True,
                    'mensaje': 'Insumo desactivado exitosamente'
                }
            else:
                return {
                    'exito': False,
                    'mensaje': 'Error al desactivar insumo'
                }
                
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al desactivar insumo: {str(e)}'
            }
