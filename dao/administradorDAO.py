from config import get_supabase_client
from entidades.administrador import Administrador

class AdministradorDAO:
    def __init__(self):
        self.supabase = get_supabase_client()

    def crear(self, administrador: Administrador):
        """Crea un nuevo administrador"""
        data = administrador.to_dict()
        # Remover id_admin si es None (se genera automáticamente)
        if data.get('id_admin') is None:
            data.pop('id_admin', None)
        resp = self.supabase.table("administrador").insert(data).execute()
        return resp

    def obtener_por_usuario(self, id_usuario):
        """Obtiene el administrador asociado a un usuario"""
        resp = self.supabase.table("administrador").select("*").eq("id_usuario", id_usuario).limit(1).execute()
        return resp
    
    def obtener_por_id(self, id_admin):
        """Obtiene un administrador por su ID"""
        resp = self.supabase.table("administrador").select("*, usuario(nombre, email)").eq("id_admin", id_admin).limit(1).execute()
        return resp
