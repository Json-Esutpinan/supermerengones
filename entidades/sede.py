class Sede:
    def __init__(self, id_sede=None, nombre=None, direccion=None, telefono=None , activo=True):
        self.id_sede = id_sede
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.activo = activo

    def to_dict(self):
        return {
            "id_sede": self.id_sede,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "activo": self.activo
        }
