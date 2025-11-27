class Cliente:
    def __init__(self, id_cliente=None, id_usuario=None, telefono=None, direccion=None):
        self.id_cliente = id_cliente
        self.id_usuario = id_usuario
        self.telefono = telefono
        self.direccion = direccion

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "telefono": self.telefono,
            "direccion": self.direccion     
        }



