class Empleado:
    def __init__(self, id_empleado=None, id_usuario=None, id_sede=None, cargo=None, fecha_ingreso=None):
        self.id_empleado = id_empleado
        self.id_usuario = id_usuario
        self.id_sede = id_sede
        self.cargo = cargo
        self.fecha_ingreso = fecha_ingreso

    def to_dict(self):
        return self.__dict__
