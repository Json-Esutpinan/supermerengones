class Cliente:
    def __init__(self, id_cliente=None, id_usuario=None, telefono=None, direccion=None):
        self.id_cliente = id_cliente
        self.id_usuario = id_usuario
        self.telefono = telefono
        self.direccion = direccion

    def to_dict(self):
        return {
            "id_cliente": self.id_cliente,
            "id_usuario": self.id_usuario,
            "telefono": self.telefono,
            "direccion": self.direccion
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Cliente desde un diccionario"""
        return Cliente(
            id_cliente=data.get('id_cliente'),
            id_usuario=data.get('id_usuario'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion')
        )
    
    def __str__(self):
        return f"Cliente #{self.id_cliente} - Usuario:{self.id_usuario}"
    
    def __repr__(self):
        return f"<Cliente(id={self.id_cliente}, usuario={self.id_usuario})>"



