#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, time
from dao.turnoDAO import TurnoDAO
from dao.empleadoDAO import EmpleadoDAO
from dao.sedeDAO import SedeDAO
from entidades.turno import Turno

logger = logging.getLogger(__name__)


class TurnoManager:
    """
    Gestión de turnos de trabajo (HU12)
    """

    def __init__(self):
        self.turnoDAO = TurnoDAO()
        self.empleadoDAO = EmpleadoDAO()
        self.sedeDAO = SedeDAO()

    def crearTurno(self, id_empleado, fecha, hora_inicio, hora_fin):
        """Crea un nuevo turno de trabajo"""
        try:
            if not id_empleado or not fecha or not hora_inicio or not hora_fin:
                return {"success": False, "message": "Todos los campos son requeridos", "data": None}
            
            # Verificar empleado existe y está activo
            resp_emp = self.empleadoDAO.obtener_por_id(id_empleado)
            if not resp_emp.data:
                return {"success": False, "message": "Empleado no encontrado", "data": None}
            
            empleado = resp_emp.data[0]
            if not empleado.get('usuario', {}).get('activo', False):
                return {"success": False, "message": "El empleado no está activo", "data": None}
            
            # Convertir strings a time si es necesario
            if isinstance(hora_inicio, str):
                try:
                    hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
                except:
                    return {"success": False, "message": "Formato de hora_inicio inválido. Use HH:MM", "data": None}
            
            if isinstance(hora_fin, str):
                try:
                    hora_fin = datetime.strptime(hora_fin, "%H:%M").time()
                except:
                    return {"success": False, "message": "Formato de hora_fin inválido. Use HH:MM", "data": None}
            
            # Validar hora_fin > hora_inicio
            if hora_fin <= hora_inicio:
                return {"success": False, "message": "La hora de fin debe ser posterior a la hora de inicio", "data": None}
            
            nuevo_turno = Turno(id_empleado=id_empleado, fecha=fecha, hora_inicio=hora_inicio, hora_fin=hora_fin)
            resp = self.turnoDAO.crear(nuevo_turno)
            
            if not resp.data:
                return {"success": False, "message": "Error al crear turno", "data": None}
            
            turno_creado = resp.data[0]
            resp_detalle = self.turnoDAO.obtener_por_id(turno_creado['id_turno'])
            
            return {"success": True, "message": "Turno creado exitosamente", "data": resp_detalle.data[0] if resp_detalle.data else turno_creado}
        except Exception as e:
            logger.error(f"Error al crear turno: {str(e)}")
            return {"success": False, "message": f"Error al crear turno: {str(e)}", "data": None}

    def asignarTurnoaEmpleado(self, id_empleado, id_turno):
        """Reasigna un turno existente a otro empleado"""
        return self.modificarTurno(id_turno, {"id_empleado": id_empleado})

    def verTurnosPorSede(self, id_sede):
        """Ver turnos de una sede (requiere fecha)"""
        from datetime import date
        return self.listarPorSedeFecha(id_sede, date.today().isoformat())

    def listarTodos(self, limite=100):
        """Lista todos los turnos"""
        try:
            resp = self.turnoDAO.listar_todos(limite)
            if not resp.data:
                return {"success": True, "message": "No hay turnos registrados", "data": []}
            return {"success": True, "message": "Turnos encontrados", "data": resp.data}
        except Exception as e:
            logger.error(f"Error al listar turnos: {str(e)}")
            return {"success": False, "message": f"Error al listar turnos: {str(e)}", "data": None}

    def listarPorEmpleado(self, id_empleado, limite=50):
        """Lista todos los turnos de un empleado"""
        try:
            resp = self.turnoDAO.listar_por_empleado(id_empleado, limite)
            if not resp.data:
                return {"success": True, "message": "No hay turnos para este empleado", "data": []}
            return {"success": True, "message": "Turnos del empleado encontrados", "data": resp.data}
        except Exception as e:
            logger.error(f"Error al listar turnos del empleado: {str(e)}")
            return {"success": False, "message": f"Error al listar turnos: {str(e)}", "data": None}

    def listarPorFecha(self, fecha, limite=100):
        """Lista todos los turnos en una fecha específica"""
        try:
            resp = self.turnoDAO.listar_por_fecha(fecha, limite)
            if not resp.data:
                return {"success": True, "message": f"No hay turnos para la fecha {fecha}", "data": []}
            return {"success": True, "message": f"Turnos del {fecha} encontrados", "data": resp.data}
        except Exception as e:
            logger.error(f"Error al listar turnos por fecha: {str(e)}")
            return {"success": False, "message": f"Error al listar turnos: {str(e)}", "data": None}

    def listarPorSedeFecha(self, id_sede, fecha, limite=100):
        """Lista turnos de una sede en una fecha específica"""
        try:
            # Verificar sede existe
            resp_sede = self.sedeDAO.obtener_por_id(id_sede)
            if not resp_sede.data:
                return {"success": False, "message": "Sede no encontrada", "data": None}
            
            resp = self.turnoDAO.listar_por_sede_fecha(id_sede, fecha, limite)
            if not resp.data:
                return {"success": True, "message": f"No hay turnos para esta sede el {fecha}", "data": []}
            return {"success": True, "message": f"Turnos de la sede encontrados", "data": resp.data}
        except Exception as e:
            logger.error(f"Error al listar turnos por sede y fecha: {str(e)}")
            return {"success": False, "message": f"Error al listar turnos: {str(e)}", "data": None}

    def obtenerTurno(self, id_turno):
        """Obtiene los detalles de un turno específico"""
        try:
            resp = self.turnoDAO.obtener_por_id(id_turno)
            if not resp.data:
                return {"success": False, "message": "Turno no encontrado", "data": None}
            return {"success": True, "message": "Turno encontrado", "data": resp.data[0]}
        except Exception as e:
            logger.error(f"Error al obtener turno: {str(e)}")
            return {"success": False, "message": f"Error al obtener turno: {str(e)}", "data": None}

    def modificarTurno(self, id_turno, datos):
        """Modifica un turno existente"""
        try:
            # Verificar turno existe
            resp_turno = self.turnoDAO.obtener_por_id(id_turno)
            if not resp_turno.data:
                return {"success": False, "message": "Turno no encontrado", "data": None}
            
            # Si se va a reasignar empleado, validar
            if 'id_empleado' in datos:
                resp_emp = self.empleadoDAO.obtener_por_id(datos['id_empleado'])
                if not resp_emp.data:
                    return {"success": False, "message": "Empleado no encontrado", "data": None}
                
                empleado = resp_emp.data[0]
                if not empleado.get('usuario', {}).get('activo', False):
                    return {"success": False, "message": "El empleado no está activo", "data": None}
            
            # Convertir horas si vienen como string
            if 'hora_inicio' in datos and isinstance(datos['hora_inicio'], str):
                try:
                    datos['hora_inicio'] = datetime.strptime(datos['hora_inicio'], "%H:%M").time()
                except:
                    return {"success": False, "message": "Formato de hora_inicio inválido. Use HH:MM", "data": None}
            
            if 'hora_fin' in datos and isinstance(datos['hora_fin'], str):
                try:
                    datos['hora_fin'] = datetime.strptime(datos['hora_fin'], "%H:%M").time()
                except:
                    return {"success": False, "message": "Formato de hora_fin inválido. Use HH:MM", "data": None}
            
            # Validar rango de horas si se modifican ambas o alguna
            turno_actual = resp_turno.data[0]
            hora_inicio_nueva = datos.get('hora_inicio', turno_actual.get('hora_inicio'))
            hora_fin_nueva = datos.get('hora_fin', turno_actual.get('hora_fin'))
            
            # Convertir strings a time si es necesario para comparación
            if isinstance(hora_inicio_nueva, str):
                hora_inicio_nueva = datetime.strptime(hora_inicio_nueva, "%H:%M:%S").time()
            if isinstance(hora_fin_nueva, str):
                hora_fin_nueva = datetime.strptime(hora_fin_nueva, "%H:%M:%S").time()
            
            if hora_fin_nueva <= hora_inicio_nueva:
                return {"success": False, "message": "La hora de fin debe ser posterior a la hora de inicio", "data": None}
            
            # Convertir objetos time de vuelta a string para serialización JSON
            if 'hora_inicio' in datos and isinstance(datos['hora_inicio'], time):
                datos['hora_inicio'] = datos['hora_inicio'].strftime("%H:%M:%S")
            if 'hora_fin' in datos and isinstance(datos['hora_fin'], time):
                datos['hora_fin'] = datos['hora_fin'].strftime("%H:%M:%S")
            
            resp = self.turnoDAO.modificar(id_turno, datos)
            if not resp.data:
                return {"success": False, "message": "Error al modificar turno", "data": None}
            
            # Obtener turno actualizado con todos los detalles
            resp_actualizado = self.turnoDAO.obtener_por_id(id_turno)
            
            return {"success": True, "message": "Turno modificado exitosamente", "data": resp_actualizado.data[0] if resp_actualizado.data else resp.data[0]}
        except Exception as e:
            logger.error(f"Error al modificar turno: {str(e)}")
            return {"success": False, "message": f"Error al modificar turno: {str(e)}", "data": None}

    def eliminarTurno(self, id_turno):
        """Elimina un turno"""
        try:
            # Verificar turno existe
            resp_turno = self.turnoDAO.obtener_por_id(id_turno)
            if not resp_turno.data:
                return {"success": False, "message": "Turno no encontrado", "data": None}
            
            turno_eliminado = resp_turno.data[0]
            
            resp = self.turnoDAO.eliminar(id_turno)
            if not resp.data:
                return {"success": False, "message": "Error al eliminar turno", "data": None}
            
            return {"success": True, "message": "Turno eliminado exitosamente", "data": turno_eliminado}
        except Exception as e:
            logger.error(f"Error al eliminar turno: {str(e)}")
            return {"success": False, "message": f"Error al eliminar turno: {str(e)}", "data": None}

