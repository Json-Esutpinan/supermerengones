#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, date, time
from dao.asistenciaDAO import AsistenciaDAO
from dao.empleadoDAO import EmpleadoDAO
from dao.turnoDAO import TurnoDAO
from entidades.asistencia import Asistencia

logger = logging.getLogger(__name__)


class AsistenciaManager:
    """
    Gestión de asistencia de empleados (HU13)
    """

    def __init__(self):
        self.asistenciaDAO = AsistenciaDAO()
        self.empleadoDAO = EmpleadoDAO()
        self.turnoDAO = TurnoDAO()

    def registrarEntrada(self, id_empleado, id_turno=None):
        """Registra la entrada (clock-in) de un empleado"""
        try:
            # Verificar empleado existe y está activo
            resp_emp = self.empleadoDAO.obtener_por_id(id_empleado)
            if not resp_emp.data:
                return {"success": False, "message": "Empleado no encontrado", "data": None}
            
            empleado = resp_emp.data[0]
            if not empleado.get('usuario', {}).get('activo', False):
                return {"success": False, "message": "El empleado no está activo", "data": None}
            
            # Verificar si ya tiene asistencia registrada hoy
            hoy = date.today().isoformat()
            resp_existente = self.asistenciaDAO.listar_por_empleado_fecha(id_empleado, hoy)
            if resp_existente.data:
                asistencia_existente = resp_existente.data[0]
                if asistencia_existente.get('hora_entrada'):
                    return {"success": False, "message": "Ya existe un registro de entrada para hoy", "data": asistencia_existente}
            
            # Crear nueva asistencia
            ahora = datetime.now()
            nueva_asistencia = Asistencia(
                id_empleado=id_empleado,
                id_turno=id_turno,
                fecha=date.today(),
                hora_entrada=ahora,
                estado='pendiente'
            )
            
            resp = self.asistenciaDAO.crear(nueva_asistencia)
            
            if not resp.data:
                return {"success": False, "message": "Error al registrar entrada", "data": None}
            
            # Obtener asistencia con detalles
            asistencia_creada = resp.data[0]
            resp_detalle = self.asistenciaDAO.obtener_por_id(asistencia_creada['id_asistencia'])
            
            return {"success": True, "message": "Entrada registrada exitosamente", "data": resp_detalle.data[0] if resp_detalle.data else asistencia_creada}
        except Exception as e:
            logger.error(f"Error al registrar entrada: {str(e)}")
            return {"success": False, "message": f"Error al registrar entrada: {str(e)}", "data": None}

    def registrarSalida(self, id_asistencia):
        """Registra la salida (clock-out) de un empleado"""
        try:
            # Verificar asistencia existe
            resp_asis = self.asistenciaDAO.obtener_por_id(id_asistencia)
            if not resp_asis.data:
                return {"success": False, "message": "Asistencia no encontrada", "data": None}
            
            asistencia = resp_asis.data[0]
            
            # Verificar que ya tenga entrada
            if not asistencia.get('hora_entrada'):
                return {"success": False, "message": "No se ha registrado la entrada", "data": None}
            
            # Verificar que no tenga salida ya registrada
            if asistencia.get('hora_salida'):
                return {"success": False, "message": "La salida ya fue registrada", "data": asistencia}
            
            # Registrar salida
            ahora = datetime.now()
            resp = self.asistenciaDAO.registrar_salida(id_asistencia, ahora)
            
            if not resp.data:
                return {"success": False, "message": "Error al registrar salida", "data": None}
            
            # Obtener asistencia actualizada
            resp_actualizada = self.asistenciaDAO.obtener_por_id(id_asistencia)
            
            return {"success": True, "message": "Salida registrada exitosamente", "data": resp_actualizada.data[0] if resp_actualizada.data else resp.data[0]}
        except Exception as e:
            logger.error(f"Error al registrar salida: {str(e)}")
            return {"success": False, "message": f"Error al registrar salida: {str(e)}", "data": None}

    def registrarSalidaPorEmpleado(self, id_empleado):
        """Registra la salida del empleado buscando su asistencia activa de hoy"""
        try:
            # Buscar asistencia de hoy sin salida
            hoy = date.today().isoformat()
            resp_asis = self.asistenciaDAO.listar_por_empleado_fecha(id_empleado, hoy)
            
            if not resp_asis.data:
                return {"success": False, "message": "No hay registro de entrada para hoy", "data": None}
            
            asistencia = resp_asis.data[0]
            
            if asistencia.get('hora_salida'):
                return {"success": False, "message": "La salida ya fue registrada", "data": asistencia}
            
            return self.registrarSalida(asistencia['id_asistencia'])
        except Exception as e:
            logger.error(f"Error al registrar salida por empleado: {str(e)}")
            return {"success": False, "message": f"Error al registrar salida: {str(e)}", "data": None}

    def listarPorEmpleado(self, id_empleado, limite=50):
        """Lista asistencias de un empleado"""
        try:
            resp = self.asistenciaDAO.listar_por_empleado(id_empleado, limite)
            
            if not resp.data:
                return {"success": True, "message": "No hay asistencias registradas", "data": []}
            
            return {"success": True, "message": "Asistencias encontradas", "data": resp.data}
        except Exception as e:
            logger.error(f"Error al listar asistencias: {str(e)}")
            return {"success": False, "message": f"Error al listar asistencias: {str(e)}", "data": None}

    def listarPorFecha(self, fecha, limite=100):
        """Lista asistencias de una fecha específica"""
        try:
            resp = self.asistenciaDAO.listar_por_fecha(fecha, limite)
            
            if not resp.data:
                return {"success": True, "message": f"No hay asistencias para {fecha}", "data": []}
            
            return {"success": True, "message": f"Asistencias del {fecha} encontradas", "data": resp.data}
        except Exception as e:
            logger.error(f"Error al listar asistencias por fecha: {str(e)}")
            return {"success": False, "message": f"Error al listar asistencias: {str(e)}", "data": None}

    def listarPorEstado(self, estado, limite=100):
        """Lista asistencias por estado"""
        try:
            estados_validos = ['pendiente', 'asistio', 'falta', 'tardanza', 'justificado']
            if estado not in estados_validos:
                return {"success": False, "message": f"Estado inválido. Valores permitidos: {', '.join(estados_validos)}", "data": None}
            
            resp = self.asistenciaDAO.listar_por_estado(estado, limite)
            
            if not resp.data:
                return {"success": True, "message": f"No hay asistencias con estado '{estado}'", "data": []}
            
            return {"success": True, "message": f"Asistencias con estado '{estado}' encontradas", "data": resp.data}
        except Exception as e:
            logger.error(f"Error al listar asistencias por estado: {str(e)}")
            return {"success": False, "message": f"Error al listar asistencias: {str(e)}", "data": None}

    def obtenerAsistencia(self, id_asistencia):
        """Obtiene una asistencia específica"""
        try:
            resp = self.asistenciaDAO.obtener_por_id(id_asistencia)
            
            if not resp.data:
                return {"success": False, "message": "Asistencia no encontrada", "data": None}
            
            return {"success": True, "message": "Asistencia encontrada", "data": resp.data[0]}
        except Exception as e:
            logger.error(f"Error al obtener asistencia: {str(e)}")
            return {"success": False, "message": f"Error al obtener asistencia: {str(e)}", "data": None}

    def actualizarEstado(self, id_asistencia, estado, observaciones=None):
        """Actualiza el estado de una asistencia"""
        try:
            estados_validos = ['pendiente', 'asistio', 'falta', 'tardanza', 'justificado']
            if estado not in estados_validos:
                return {"success": False, "message": f"Estado inválido. Valores permitidos: {', '.join(estados_validos)}", "data": None}
            
            # Verificar que existe
            resp_asis = self.asistenciaDAO.obtener_por_id(id_asistencia)
            if not resp_asis.data:
                return {"success": False, "message": "Asistencia no encontrada", "data": None}
            
            resp = self.asistenciaDAO.actualizar_estado(id_asistencia, estado, observaciones)
            
            if not resp.data:
                return {"success": False, "message": "Error al actualizar estado", "data": None}
            
            # Obtener asistencia actualizada
            resp_actualizada = self.asistenciaDAO.obtener_por_id(id_asistencia)
            
            return {"success": True, "message": "Estado actualizado exitosamente", "data": resp_actualizada.data[0] if resp_actualizada.data else resp.data[0]}
        except Exception as e:
            logger.error(f"Error al actualizar estado: {str(e)}")
            return {"success": False, "message": f"Error al actualizar estado: {str(e)}", "data": None}

    def modificarAsistencia(self, id_asistencia, datos):
        """Modifica una asistencia existente"""
        try:
            # Verificar que existe
            resp_asis = self.asistenciaDAO.obtener_por_id(id_asistencia)
            if not resp_asis.data:
                return {"success": False, "message": "Asistencia no encontrada", "data": None}
            
            resp = self.asistenciaDAO.modificar(id_asistencia, datos)
            
            if not resp.data:
                return {"success": False, "message": "Error al modificar asistencia", "data": None}
            
            # Obtener asistencia actualizada
            resp_actualizada = self.asistenciaDAO.obtener_por_id(id_asistencia)
            
            return {"success": True, "message": "Asistencia modificada exitosamente", "data": resp_actualizada.data[0] if resp_actualizada.data else resp.data[0]}
        except Exception as e:
            logger.error(f"Error al modificar asistencia: {str(e)}")
            return {"success": False, "message": f"Error al modificar asistencia: {str(e)}", "data": None}

    def eliminarAsistencia(self, id_asistencia):
        """Elimina un registro de asistencia"""
        try:
            # Verificar que existe
            resp_asis = self.asistenciaDAO.obtener_por_id(id_asistencia)
            if not resp_asis.data:
                return {"success": False, "message": "Asistencia no encontrada", "data": None}
            
            asistencia_eliminada = resp_asis.data[0]
            
            resp = self.asistenciaDAO.eliminar(id_asistencia)
            
            if not resp.data:
                return {"success": False, "message": "Error al eliminar asistencia", "data": None}
            
            return {"success": True, "message": "Asistencia eliminada exitosamente", "data": asistencia_eliminada}
        except Exception as e:
            logger.error(f"Error al eliminar asistencia: {str(e)}")
            return {"success": False, "message": f"Error al eliminar asistencia: {str(e)}", "data": None}

    def listarTodas(self, limite=100):
        """Lista todas las asistencias (solo administradores)"""
        try:
            resp = self.asistenciaDAO.listar_todas(limite)
            
            if not resp.data:
                return {"success": True, "message": "No hay asistencias registradas", "data": []}
            
            return {"success": True, "message": "Asistencias encontradas", "data": resp.data}
        except Exception as e:
            logger.error(f"Error al listar todas las asistencias: {str(e)}")
            return {"success": False, "message": f"Error al listar asistencias: {str(e)}", "data": None}

    def obtenerReporteMensual(self, id_empleado, year, month):
        """Obtiene reporte mensual de asistencias de un empleado"""
        try:
            resp = self.asistenciaDAO.obtener_reporte_mensual(id_empleado, year, month)
            
            if not resp.data:
                return {"success": True, "message": f"No hay asistencias para {year}-{month:02d}", "data": []}
            
            # Calcular estadísticas
            asistencias = resp.data
            total = len(asistencias)
            asistio = len([a for a in asistencias if a.get('estado') == 'asistio'])
            faltas = len([a for a in asistencias if a.get('estado') == 'falta'])
            tardanzas = len([a for a in asistencias if a.get('estado') == 'tardanza'])
            justificados = len([a for a in asistencias if a.get('estado') == 'justificado'])
            
            return {
                "success": True,
                "message": f"Reporte de {year}-{month:02d} generado",
                "data": {
                    "asistencias": asistencias,
                    "estadisticas": {
                        "total": total,
                        "asistio": asistio,
                        "faltas": faltas,
                        "tardanzas": tardanzas,
                        "justificados": justificados
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error al obtener reporte mensual: {str(e)}")
            return {"success": False, "message": f"Error al generar reporte: {str(e)}", "data": None}
