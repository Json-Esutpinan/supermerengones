from config import get_supabase_client
from entidades.cliente import Cliente

class ClienteDAO:
    def __init__(self):
        self.supabase = get_supabase_client()

    def crear(self, cliente: Cliente):
        data = cliente.to_dict()
        resp = self.supabase.table("cliente").insert(data).execute()
        return resp


    def obtener_por_usuario(self, id_usuario):
        resp = self.supabase.table("cliente").select("*").eq("id_usuario", id_usuario).limit(1).execute()
        return resp
# Fin del archivo dao/clienteDAO.py con direccion