from dao.sedeDAO import SedeDAO
from entidades.sede import Sede

class SedeManager:
    def __init__(self):
        self.dao = SedeDAO()

    def crearSede(self, nombre, direccion, telefono):
        """
        Crea una nueva sede con validación de nombre único.
        Retorna: success, message y data = objeto Sede
        """
        
        # Validar nombre requerido
        if not nombre or not nombre.strip():
            return {
                "success": False,
                "message": "El nombre es obligatorio",
                "data": None
            }
        
        # Validar longitud mínima del nombre
        if len(nombre.strip()) < 3:
            return {
                "success": False,
                "message": "El nombre debe tener al menos 3 caracteres",
                "data": None
            }
        
        # Validar teléfono si se proporciona
        if telefono and telefono.strip():
            # Eliminar espacios y caracteres no numéricos para validación
            telefono_limpio = ''.join(filter(str.isdigit, telefono.strip()))
            if len(telefono_limpio) < 7:
                return {
                    "success": False,
                    "message": "El teléfono debe tener al menos 7 dígitos",
                    "data": None
                }

        # Validar nombre único (consulta directa por nombre)
        existentes = self.dao.obtener_por_nombre(nombre.strip())
        if existentes.data:
            return {
                "success": False,
                "message": "Ya existe una sede con ese nombre",
                "data": None
            }

        # Crear la entidad
        sede = Sede(
            nombre=nombre.strip(),
            direccion=direccion.strip() if direccion else None,
            telefono=telefono.strip() if telefono else None,
            activo=True
        )

        # Guardar en BD
        resp = self.dao.crear(sede)

        if resp.data:
            sede_creada = Sede(**resp.data[0])
            return {
                "success": True,
                "message": "Sede registrada exitosamente",
                "data": sede_creada
            }

        return {
            "success": False,
            "message": "Error al registrar sede",
            "data": None
        }

    def listarSedes(self, solo_activos=True):
        """
        Lista todas las sedes.
        Retorna lista de Sede.
        """

        resp = self.dao.listar(solo_activos)
        sedes = [Sede(**row) for row in resp.data]

        return {
            "success": True,
            "message": f"Se encontraron {len(sedes)} sede(s)",
            "data": sedes
        }

    def obtenerSede(self, id_sede):
        """
        Obtiene una sede por ID.
        Retorna un objeto Sede o None.
        """

        resp = self.dao.obtener(id_sede)

        if resp.data:
            sede = Sede(**resp.data[0])
            return {
                "success": True,
                "message": "Sede encontrada",
                "data": sede
            }

        return {
            "success": False,
            "message": "Sede no encontrada",
            "data": None
        }

    def modificarSede(self, id_sede, cambios):
        """
        Modifica una sede existente.
        Retorna objeto Sede modificado.
        """
        
        # Verificar que la sede existe
        sede_existente = self.dao.obtener(id_sede)
        if not sede_existente.data:
            return {
                "success": False,
                "message": "Sede no encontrada",
                "data": None
            }
        
        # Validar nombre si se está modificando
        if 'nombre' in cambios:
            if not cambios['nombre'] or not cambios['nombre'].strip():
                return {
                    "success": False,
                    "message": "El nombre no puede estar vacío",
                    "data": None
                }
            
            if len(cambios['nombre'].strip()) < 3:
                return {
                    "success": False,
                    "message": "El nombre debe tener al menos 3 caracteres",
                    "data": None
                }
            
            # Validar nombre único (excepto la misma sede)
            existentes = self.dao.obtener_por_nombre(cambios['nombre'].strip())
            if any(s["id_sede"] != id_sede for s in existentes.data):
                return {
                    "success": False,
                    "message": "Ya existe otra sede con ese nombre",
                    "data": None
                }
            
            cambios['nombre'] = cambios['nombre'].strip()
        
        # Validar teléfono si se está modificando
        if 'telefono' in cambios and cambios['telefono'] and cambios['telefono'].strip():
            telefono_limpio = ''.join(filter(str.isdigit, cambios['telefono'].strip()))
            if len(telefono_limpio) < 7:
                return {
                    "success": False,
                    "message": "El teléfono debe tener al menos 7 dígitos",
                    "data": None
                }
        
        # Limpiar valores
        if 'direccion' in cambios and cambios['direccion']:
            cambios['direccion'] = cambios['direccion'].strip()

        resp = self.dao.modificar(id_sede, cambios)

        if resp.data:
            sede = Sede(**resp.data[0])
            return {
                "success": True,
                "message": "Sede modificada exitosamente",
                "data": sede
            }

        return {
            "success": False,
            "message": "Error al modificar la sede",
            "data": None
        }

    def desactivarSede(self, id_sede):
        """
        Desactiva una sede.
        Retorna objeto Sede actualizado.
        """
        # Verificar que la sede existe
        sede_existente = self.dao.obtener(id_sede)
        if not sede_existente.data:
            return {
                "success": False,
                "message": "Sede no encontrada",
                "data": None
            }

        resp = self.dao.desactivar(id_sede)

        if resp.data:
            sede = Sede(**resp.data[0])
            return {
                "success": True,
                "message": "Sede desactivada exitosamente",
                "data": sede
            }

        return {
            "success": False,
            "message": "Error al desactivar la sede",
            "data": None
        }
    
    def cambiarEstado(self, id_sede, activo):
        """
        Cambia el estado activo/inactivo de una sede.
        Retorna objeto Sede actualizado.
        """
        # Verificar que la sede existe
        sede_existente = self.dao.obtener(id_sede)
        if not sede_existente.data:
            return {
                "success": False,
                "message": "Sede no encontrada",
                "data": None
            }
        
        resp = self.dao.cambiar_estado(id_sede, activo)
        
        if resp.data:
            sede = Sede(**resp.data[0])
            estado_texto = "activada" if activo else "desactivada"
            return {
                "success": True,
                "message": f"Sede {estado_texto} exitosamente",
                "data": sede
            }
        
        return {
            "success": False,
            "message": "Error al cambiar el estado de la sede",
            "data": None
        }

    def vistaConsolidada(self, id_sede, filtro=None):
        """
        Vista consolidada con personal, inventario y pedidos.
        Retorna dict.
        """

        data = {}

        if filtro in (None, "personal"):
            empleados = self.dao.supabase.table("empleado").select("*").eq("id_sede", id_sede).execute()
            data["personal"] = empleados.data

        if filtro in (None, "inventario"):
            inventario = self.dao.supabase.table("inventario").select("*").execute()
            data["inventario"] = inventario.data

        if filtro in (None, "pedidos"):
            pedidos = self.dao.supabase.table("pedido").select("*").eq("id_sede", id_sede).execute()
            data["pedidos"] = pedidos.data

        return {
            "success": True,
            "message": "Vista consolidada generada",
            "data": data
        }
