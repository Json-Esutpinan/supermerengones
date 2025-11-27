import bcrypt
from entidades.usuario import Usuario
from entidades.cliente import Cliente
from dao.usuarioDAO import UsuarioDAO
from dao.clienteDAO import ClienteDAO
from dao.empleadoDAO import EmpleadoDAO
from dao.administradorDAO import AdministradorDAO


class AuthManager:
    """
    Gestión de Autenticación y creación de cuentas de cliente.
    """

    usuario_actual = None   # Se almacena en memoria. Cambia luego si usas JWT.

    def __init__(self):
        self.usuarioDAO = UsuarioDAO()
        self.clienteDAO = ClienteDAO()
        self.empleadoDAO = EmpleadoDAO()
        self.adminDAO = AdministradorDAO()

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    def login(self, email, password):
        resp = self.usuarioDAO.obtener_por_email(email)

        if not resp.data:
            return {"success": False, "message": "Usuario no encontrado", "data": None}

        row = resp.data[0]
        usuario = Usuario(**row)

        # validar contraseña
        if not bcrypt.checkpw(password.encode(), usuario.password.encode()):
            return {"success": False, "message": "Credenciales inválidas", "data": None}

        AuthManager.usuario_actual = usuario
        return {"success": True, "message": "Inicio de sesión exitoso", "data": usuario}

    # ------------------------------------------------------------------
    # REGISTRO DEL CLIENTE
    # ------------------------------------------------------------------
    def registrarCliente(self, nombre, telefono, email, direccion, password):
        # verificar existencia
        existe = self.usuarioDAO.obtener_por_email(email)
        if existe.data:
            return {"success": False, "message": "El email ya está registrado", "data": None}

        # hash
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            password=hashed,
            rol="cliente"
        )

        resp_user = self.usuarioDAO.crear(nuevo_usuario)
        if not resp_user.data:
            return {"success": False, "message": "Error al crear usuario", "data": None}

        id_usuario = resp_user.data[0]["id_usuario"]

        nuevo_cliente = Cliente(
            id_usuario=id_usuario,
            telefono=telefono,
            direccion=direccion,
        )

        resp_cli = self.clienteDAO.crear(nuevo_cliente)

        if not resp_cli.data:
            return {"success": False, "message": "Error al crear cliente", "data": None}

        return {
            "success": True,
            "message": "Cliente registrado exitosamente",
            "data": {
                "usuario": Usuario(**resp_user.data[0]),
                "cliente": Cliente(**resp_cli.data[0])
            }
        }

    # ------------------------------------------------------------------
    # USUARIO ACTUAL
    # ------------------------------------------------------------------
    def usuarioLogueado(self):
        return AuthManager.usuario_actual
