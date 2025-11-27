from config import get_supabase_client
from entidades.empleado import Empleado

class EmpleadoDAO:
    def __init__(self):
        self.supabase = get_supabase_client()

    def obtener_por_usuario(self, id_usuario):
        resp = self.supabase.table("empleado").select("*").eq("id_usuario", id_usuario).limit(1).execute()
        return resp
