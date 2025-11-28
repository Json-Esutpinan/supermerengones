from datetime import datetime, date

class Empleado:
    def __init__(self, id_empleado=None, id_usuario=None, id_sede=None, cargo=None, fecha_ingreso=None):
        self.id_empleado = id_empleado
        self.id_usuario = id_usuario
        self.id_sede = id_sede
        self.cargo = cargo
        self.fecha_ingreso = fecha_ingreso

    def to_dict(self):
        return {
            "id_empleado": self.id_empleado,
            "id_usuario": self.id_usuario,
            "id_sede": self.id_sede,
            "cargo": self.cargo,
            "fecha_ingreso": self.fecha_ingreso.isoformat() if isinstance(self.fecha_ingreso, (datetime, date)) else self.fecha_ingreso
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Empleado desde un diccionario"""
        fecha_ingreso = data.get('fecha_ingreso')
        if isinstance(fecha_ingreso, str):
            try:
                fecha_ingreso = datetime.fromisoformat(fecha_ingreso.replace('Z', '+00:00')).date()
            except:
                fecha_ingreso = date.today()
        
        return Empleado(
            id_empleado=data.get('id_empleado'),
            id_usuario=data.get('id_usuario'),
            id_sede=data.get('id_sede'),
            cargo=data.get('cargo'),
            fecha_ingreso=fecha_ingreso
        )
    
    def __str__(self):
        return f"Empleado #{self.id_empleado} - {self.cargo} (Sede:{self.id_sede})"
    
    def __repr__(self):
        return f"<Empleado(id={self.id_empleado}, usuario={self.id_usuario}, sede={self.id_sede}, cargo={self.cargo})>"
