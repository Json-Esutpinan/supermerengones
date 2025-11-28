from datetime import datetime

class Usuario:
    # Roles válidos del sistema
    ROLES_VALIDOS = ['cliente', 'empleado', 'administrador']
    
    def __init__(self, id_usuario=None, nombre=None, email=None, password=None, rol=None, activo=True, created_at=None):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password
        self.rol = rol if rol in self.ROLES_VALIDOS else 'cliente'
        self.activo = activo if isinstance(activo, bool) else True
        self.created_at = created_at if isinstance(created_at, datetime) else datetime.now()

    def to_dict(self, incluir_password=False):
        """Convierte el usuario a diccionario (sin password por defecto)"""
        data = {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
        if incluir_password:
            data["password"] = self.password
        return data
    
    @staticmethod
    def from_dict(data):
        """Crea un objeto Usuario desde un diccionario"""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                created_at = datetime.now()
        
        return Usuario(
            id_usuario=data.get('id_usuario'),
            nombre=data.get('nombre'),
            email=data.get('email'),
            password=data.get('password'),
            rol=data.get('rol'),
            activo=data.get('activo', True),
            created_at=created_at
        )
    
    def __str__(self):
        return f"Usuario #{self.id_usuario} - {self.nombre} ({self.rol})"
    
    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, email={self.email}, rol={self.rol}, activo={self.activo})>"

