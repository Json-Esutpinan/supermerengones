class Usuario:
    def __init__(self, id_usuario=None, nombre=None, email=None, password=None, rol=None, activo=True, created_at=None):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password
        self.rol = rol
        self.activo = activo
        self.created_at = created_at

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "email": self.email,
            "password": self.password,
            "rol": self.rol
        }

