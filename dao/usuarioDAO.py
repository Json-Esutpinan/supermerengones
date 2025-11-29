from config import get_supabase_client
from entidades.usuario import Usuario

class UsuarioDAO:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.tabla = "usuario"

    def obtener_por_email(self, email):
        resp = self.supabase.table("usuario").select("*").eq("email", email).limit(1).execute()
        return resp

    def crear(self, usuario: Usuario):
        data = usuario.to_dict(incluir_password=True)  # Incluir password al crear
        # Eliminar id_usuario si es None para permitir autogeneración en BD
        if data.get('id_usuario') is None:
            data.pop('id_usuario', None)
        resp = self.supabase.table("usuario").insert(data).execute()
        return resp


    def obtener(self, id_usuario):
        resp = self.supabase.table("usuario").select("*").eq("id_usuario", id_usuario).limit(1).execute()
        return resp

    def modificar(self, id_usuario, cambios: dict):
        resp = self.supabase.table("usuario").update(cambios).eq("id_usuario", id_usuario).execute()
        return resp
