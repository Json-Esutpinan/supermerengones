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
    
    def actualizar(self, id_cliente, telefono=None, direccion=None):
        """Actualiza campos básicos de un cliente."""
        update_fields = {}
        if telefono is not None:
            update_fields['telefono'] = telefono
        if direccion is not None:
            update_fields['direccion'] = direccion
        if not update_fields:
            return {'success': False, 'message': 'Nada para actualizar'}
        resp = self.supabase.table("cliente").update(update_fields).eq("id_cliente", id_cliente).execute()
        # Normalizar respuesta
        if resp and getattr(resp, 'data', None):
            return {'success': True, 'data': resp.data, 'message': 'Cliente actualizado'}
        return {'success': False, 'message': 'No se pudo actualizar'}
# Fin del archivo dao/clienteDAO.py con direccion