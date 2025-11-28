class Administrador:
    # Niveles de acceso válidos
    NIVELES_ACCESO = ['basico', 'intermedio', 'avanzado', 'total']
    
    def __init__(self, id_admin=None, id_usuario=None, nivel_acceso="basico"):
        self.id_admin = id_admin
        self.id_usuario = id_usuario
        self.nivel_acceso = nivel_acceso if nivel_acceso in self.NIVELES_ACCESO else 'basico'

    def to_dict(self):
        return {
            "id_admin": self.id_admin,
            "id_usuario": self.id_usuario,
            "nivel_acceso": self.nivel_acceso
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Administrador desde un diccionario"""
        return Administrador(
            id_admin=data.get('id_admin'),
            id_usuario=data.get('id_usuario'),
            nivel_acceso=data.get('nivel_acceso', 'basico')
        )
    
    def __str__(self):
        return f"Administrador #{self.id_admin} - Usuario:{self.id_usuario} [{self.nivel_acceso}]"
    
    def __repr__(self):
        return f"<Administrador(id={self.id_admin}, usuario={self.id_usuario}, nivel={self.nivel_acceso})>"
