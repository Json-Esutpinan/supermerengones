from config import get_supabase_client
from entidades.empleado import Empleado

class EmpleadoDAO:
    def __init__(self):
        self.supabase = get_supabase_client()

    def crear(self, empleado: Empleado):
        """Crea un nuevo empleado"""
        data = empleado.to_dict()
        # Remover id_empleado si es None (se genera automáticamente)
        if data.get('id_empleado') is None:
            data.pop('id_empleado', None)
        resp = self.supabase.table("empleado").insert(data).execute()
        return resp

    def obtener_por_usuario(self, id_usuario):
        """Obtiene el empleado asociado a un usuario"""
        resp = self.supabase.table("empleado").select("*").eq("id_usuario", id_usuario).limit(1).execute()
        return resp
    
    def obtener_por_id(self, id_empleado):
        """
        Obtiene un empleado por su ID con información de usuario y sede
        
        Returns:
            {
                "id_empleado": int,
                "id_usuario": int,
                "id_sede": int,
                "cargo": str,
                "fecha_ingreso": date,
                "usuario": {"nombre": str, "email": str, "activo": bool},
                "sede": {"nombre": str, "direccion": str}
            }
        """
        resp = self.supabase.table("empleado").select(
            "*, usuario(nombre, email, activo), sede(nombre, direccion)"
        ).eq("id_empleado", id_empleado).limit(1).execute()
        return resp
    
    def listar_todos(self, limite=None):
        """
        Lista todos los empleados con información de usuario y sede
        
        Args:
            limite: Número máximo de resultados (opcional)
        """
        query = self.supabase.table("empleado").select(
            "*, usuario(nombre, email, activo), sede(nombre, direccion)"
        ).order("id_empleado", desc=True)
        
        if limite:
            query = query.limit(limite)
        
        resp = query.execute()
        return resp
    
    def listar_por_sede(self, id_sede, limite=None):
        """
        Lista empleados de una sede específica
        
        Args:
            id_sede: ID de la sede
            limite: Número máximo de resultados (opcional)
        """
        query = self.supabase.table("empleado").select(
            "*, usuario(nombre, email, activo), sede(nombre)"
        ).eq("id_sede", id_sede).order("id_empleado", desc=True)
        
        if limite:
            query = query.limit(limite)
        
        resp = query.execute()
        return resp
    
    def listar_activos(self, limite=None):
        """
        Lista empleados con usuarios activos
        
        Args:
            limite: Número máximo de resultados (opcional)
        """
        query = self.supabase.table("empleado").select(
            "*, usuario!inner(nombre, email, activo), sede(nombre)"
        ).eq("usuario.activo", True).order("id_empleado", desc=True)
        
        if limite:
            query = query.limit(limite)
        
        resp = query.execute()
        return resp
    
    def modificar(self, id_empleado, datos):
        """
        Modifica datos de un empleado
        
        Args:
            id_empleado: ID del empleado
            datos: Diccionario con campos a actualizar (id_sede, cargo)
        """
        # Solo permitir actualizar id_sede y cargo
        datos_permitidos = {}
        if 'id_sede' in datos:
            datos_permitidos['id_sede'] = datos['id_sede']
        if 'cargo' in datos:
            datos_permitidos['cargo'] = datos['cargo']
        
        resp = self.supabase.table("empleado").update(datos_permitidos).eq("id_empleado", id_empleado).execute()
        return resp
    
    def cambiar_sede(self, id_empleado, nueva_sede):
        """
        Cambia la sede de un empleado
        
        Args:
            id_empleado: ID del empleado
            nueva_sede: ID de la nueva sede
        """
        resp = self.supabase.table("empleado").update({"id_sede": nueva_sede}).eq("id_empleado", id_empleado).execute()
        return resp
