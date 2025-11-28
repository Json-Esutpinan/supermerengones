#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from dao.empleadoDAO import EmpleadoDAO
from dao.usuarioDAO import UsuarioDAO
from dao.sedeDAO import SedeDAO
from entidades.empleado import Empleado

logger = logging.getLogger(__name__)


class PersonalManager:
    """
    Gestión de empleados (HU11)
    Nota: La creación de empleados se hace desde AuthManager.registrarEmpleado()
    Este manager se enfoca en: listar, consultar, modificar, transferir sede
    """

    def __init__(self):
        self.empleadoDAO = EmpleadoDAO()
        self.usuarioDAO = UsuarioDAO()
        self.sedeDAO = SedeDAO()

    # ------------------------------------------------------------------
    # CONSULTA DE EMPLEADOS
    # ------------------------------------------------------------------
    def listarTodos(self, limite=None):
        """
        Lista todos los empleados con información de usuario y sede
        
        Args:
            limite: Número máximo de resultados (opcional)
            
        Returns:
            dict con success, message, data
        """
        try:
            resp = self.empleadoDAO.listar_todos(limite=limite)
            
            if not resp.data:
                return {
                    "success": True,
                    "message": "No hay empleados registrados",
                    "data": []
                }
            
            return {
                "success": True,
                "message": f"Se encontraron {len(resp.data)} empleados",
                "data": resp.data
            }
        except Exception as e:
            logger.error(f"Error al listar empleados: {str(e)}")
            return {
                "success": False,
                "message": f"Error al listar empleados: {str(e)}",
                "data": None
            }

    def listarPorSede(self, id_sede, limite=None):
        """
        Lista empleados de una sede específica
        
        Args:
            id_sede: ID de la sede
            limite: Número máximo de resultados (opcional)
            
        Returns:
            dict con success, message, data
        """
        try:
            # Verificar que la sede existe
            resp_sede = self.sedeDAO.obtener(id_sede)
            if not resp_sede.data:
                return {
                    "success": False,
                    "message": "Sede no encontrada",
                    "data": None
                }
            
            resp = self.empleadoDAO.listar_por_sede(id_sede, limite=limite)
            
            if not resp.data:
                return {
                    "success": True,
                    "message": f"No hay empleados en la sede {resp_sede.data[0]['nombre']}",
                    "data": []
                }
            
            return {
                "success": True,
                "message": f"Se encontraron {len(resp.data)} empleados en la sede",
                "data": resp.data
            }
        except Exception as e:
            logger.error(f"Error al listar empleados por sede: {str(e)}")
            return {
                "success": False,
                "message": f"Error al listar empleados por sede: {str(e)}",
                "data": None
            }

    def listarActivos(self, limite=None):
        """
        Lista empleados con usuarios activos
        
        Args:
            limite: Número máximo de resultados (opcional)
            
        Returns:
            dict con success, message, data
        """
        try:
            resp = self.empleadoDAO.listar_activos(limite=limite)
            
            if not resp.data:
                return {
                    "success": True,
                    "message": "No hay empleados activos",
                    "data": []
                }
            
            return {
                "success": True,
                "message": f"Se encontraron {len(resp.data)} empleados activos",
                "data": resp.data
            }
        except Exception as e:
            logger.error(f"Error al listar empleados activos: {str(e)}")
            return {
                "success": False,
                "message": f"Error al listar empleados activos: {str(e)}",
                "data": None
            }

    def obtenerEmpleado(self, id_empleado):
        """
        Obtiene detalle de un empleado con información de usuario y sede
        
        Args:
            id_empleado: ID del empleado
            
        Returns:
            dict con success, message, data
        """
        try:
            resp = self.empleadoDAO.obtener_por_id(id_empleado)
            
            if not resp.data:
                return {
                    "success": False,
                    "message": "Empleado no encontrado",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Empleado encontrado",
                "data": resp.data[0]
            }
        except Exception as e:
            logger.error(f"Error al obtener empleado: {str(e)}")
            return {
                "success": False,
                "message": f"Error al obtener empleado: {str(e)}",
                "data": None
            }

    # ------------------------------------------------------------------
    # MODIFICACIÓN DE EMPLEADOS
    # ------------------------------------------------------------------
    def modificarEmpleado(self, id_empleado, datos):
        """
        Modifica datos de un empleado (cargo, id_sede)
        
        Args:
            id_empleado: ID del empleado
            datos: Dict con campos a actualizar {"cargo": str, "id_sede": int}
            
        Returns:
            dict con success, message, data
        """
        try:
            # Verificar que el empleado existe
            resp_emp = self.empleadoDAO.obtener_por_id(id_empleado)
            if not resp_emp.data:
                return {
                    "success": False,
                    "message": "Empleado no encontrado",
                    "data": None
                }
            
            # Si se está cambiando la sede, verificar que existe
            if 'id_sede' in datos:
                resp_sede = self.sedeDAO.obtener(datos['id_sede'])
                if not resp_sede.data:
                    return {
                        "success": False,
                        "message": "Sede no encontrada",
                        "data": None
                    }
            
            # Modificar empleado
            resp = self.empleadoDAO.modificar(id_empleado, datos)
            
            if not resp.data:
                return {
                    "success": False,
                    "message": "Error al modificar empleado",
                    "data": None
                }
            
            # Obtener datos actualizados
            resp_actualizado = self.empleadoDAO.obtener_por_id(id_empleado)
            
            return {
                "success": True,
                "message": "Empleado modificado exitosamente",
                "data": resp_actualizado.data[0] if resp_actualizado.data else resp.data[0]
            }
        except Exception as e:
            logger.error(f"Error al modificar empleado: {str(e)}")
            return {
                "success": False,
                "message": f"Error al modificar empleado: {str(e)}",
                "data": None
            }

    def cambiarSede(self, id_empleado, nueva_sede):
        """
        Transfiere un empleado a otra sede
        
        Args:
            id_empleado: ID del empleado
            nueva_sede: ID de la nueva sede
            
        Returns:
            dict con success, message, data
        """
        try:
            # Verificar que el empleado existe
            resp_emp = self.empleadoDAO.obtener_por_id(id_empleado)
            if not resp_emp.data:
                return {
                    "success": False,
                    "message": "Empleado no encontrado",
                    "data": None
                }
            
            sede_actual = resp_emp.data[0].get('id_sede')
            
            # Verificar que la nueva sede existe
            resp_sede = self.sedeDAO.obtener(nueva_sede)
            if not resp_sede.data:
                return {
                    "success": False,
                    "message": "Sede destino no encontrada",
                    "data": None
                }
            
            if sede_actual == nueva_sede:
                return {
                    "success": False,
                    "message": "El empleado ya está asignado a esa sede",
                    "data": None
                }
            
            # Cambiar sede
            resp = self.empleadoDAO.cambiar_sede(id_empleado, nueva_sede)
            
            if not resp.data:
                return {
                    "success": False,
                    "message": "Error al cambiar sede",
                    "data": None
                }
            
            # Obtener datos actualizados
            resp_actualizado = self.empleadoDAO.obtener_por_id(id_empleado)
            
            return {
                "success": True,
                "message": f"Empleado transferido a {resp_sede.data[0]['nombre']} exitosamente",
                "data": resp_actualizado.data[0] if resp_actualizado.data else resp.data[0]
            }
        except Exception as e:
            logger.error(f"Error al cambiar sede: {str(e)}")
            return {
                "success": False,
                "message": f"Error al cambiar sede: {str(e)}",
                "data": None
            }

    # ------------------------------------------------------------------
    # DESACTIVACIÓN DE EMPLEADOS
    # ------------------------------------------------------------------
    def desactivarEmpleado(self, id_empleado):
        """
        Desactiva un empleado (desactiva su usuario)
        
        Args:
            id_empleado: ID del empleado
            
        Returns:
            dict con success, message, data
        """
        try:
            # Obtener empleado
            resp_emp = self.empleadoDAO.obtener_por_id(id_empleado)
            if not resp_emp.data:
                return {
                    "success": False,
                    "message": "Empleado no encontrado",
                    "data": None
                }
            
            id_usuario = resp_emp.data[0].get('id_usuario')
            
            # Desactivar usuario
            resp = self.usuarioDAO.modificar({
                "id_usuario": id_usuario,
                "activo": False
            })
            
            if not resp.data:
                return {
                    "success": False,
                    "message": "Error al desactivar empleado",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Empleado desactivado exitosamente",
                "data": resp.data[0]
            }
        except Exception as e:
            logger.error(f"Error al desactivar empleado: {str(e)}")
            return {
                "success": False,
                "message": f"Error al desactivar empleado: {str(e)}",
                "data": None
            }
    
    def activarEmpleado(self, id_empleado):
        """
        Activa un empleado (activa su usuario)
        
        Args:
            id_empleado: ID del empleado
            
        Returns:
            dict con success, message, data
        """
        try:
            # Obtener empleado
            resp_emp = self.empleadoDAO.obtener_por_id(id_empleado)
            if not resp_emp.data:
                return {
                    "success": False,
                    "message": "Empleado no encontrado",
                    "data": None
                }
            
            id_usuario = resp_emp.data[0].get('id_usuario')
            
            # Activar usuario
            resp = self.usuarioDAO.modificar({
                "id_usuario": id_usuario,
                "activo": True
            })
            
            if not resp.data:
                return {
                    "success": False,
                    "message": "Error al activar empleado",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Empleado activado exitosamente",
                "data": resp.data[0]
            }
        except Exception as e:
            logger.error(f"Error al activar empleado: {str(e)}")
            return {
                "success": False,
                "message": f"Error al activar empleado: {str(e)}",
                "data": None
            }
