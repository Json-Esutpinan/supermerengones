class Administrador:
    def __init__(self, id_admin=None, id_usuario=None, nivel_acceso="basico"):
        self.id_admin = id_admin
        self.id_usuario = id_usuario
        self.nivel_acceso = nivel_acceso

    def to_dict(self):
        return self.__dict__
