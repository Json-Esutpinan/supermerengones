from config import get_supabase_client
from entidades.cliente import Cliente

class ClienteDAO:
    def __init__(self):
        self.supabase = get_supabase_client()

    def crear(self, cliente: Cliente):
        data = cliente.to_dict()
        # Eliminar id_cliente si es None para permitir autogeneración
        if data.get('id_cliente') is None:
            data.pop('id_cliente', None)
        resp = self.supabase.table("cliente").insert(data).execute()
        return resp


    def obtener_por_usuario(self, id_usuario):
        resp = self.supabase.table("cliente").select("*").eq("id_usuario", id_usuario).limit(1).execute()
        return resp
    
    def obtener_por_id(self, id_cliente):
        """
        Obtiene un cliente por su ID
        
        Args:
            id_cliente: ID del cliente
            
        Returns:
            Response de Supabase con los datos del cliente
        """
        resp = self.supabase.table("cliente").select("*").eq("id_cliente", id_cliente).limit(1).execute()
        return resp
# Fin del archivo dao/clienteDAO.py con direccion