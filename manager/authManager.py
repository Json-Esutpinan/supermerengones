import bcrypt
import re
import logging
from datetime import date
from entidades.usuario import Usuario
from entidades.cliente import Cliente
from entidades.empleado import Empleado
from entidades.administrador import Administrador
from dao.usuarioDAO import UsuarioDAO
from dao.clienteDAO import ClienteDAO
from dao.empleadoDAO import EmpleadoDAO
from dao.administradorDAO import AdministradorDAO

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Gestión de Autenticación y creación de cuentas multi-rol.
    Soporta: Cliente, Empleado, Administrador
    """

    usuario_actual = None   # Se almacena en memoria. Cambiar a JWT en producción

    def __init__(self):
        self.usuarioDAO = UsuarioDAO()
        self.clienteDAO = ClienteDAO()
        self.empleadoDAO = EmpleadoDAO()
        self.adminDAO = AdministradorDAO()

    # ------------------------------------------------------------------
    # UTILIDADES DE VALIDACIÓN
    # ------------------------------------------------------------------
    def _validar_email(self, email):
        """Valida formato de email"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def _validar_password(self, password):
        """
        Valida que la contraseña cumpla con requisitos mínimos:
        - Al menos 6 caracteres
        """
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        return True, ""
    
    def _hash_password(self, password):
        """Genera hash bcrypt de la contraseña"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def _verificar_password(self, password, hashed):
        """Verifica contraseña contra hash"""
        return bcrypt.checkpw(password.encode(), hashed.encode())

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    def login(self, email, password):
        """
        Inicia sesión de cualquier tipo de usuario
        
        Returns:
            dict con:
            - success: bool
            - message: str
            - data: dict con usuario y perfil según rol
        """
        try:
            resp = self.usuarioDAO.obtener_por_email(email)

            if not resp.data:
                return {"success": False, "message": "Usuario no encontrado", "data": None}

            row = resp.data[0]
            usuario = Usuario(**row)

            # Verificar si está activo
            if not usuario.activo:
                return {"success": False, "message": "Usuario inactivo. Contacte al administrador", "data": None}

            # Validar contraseña
            if not self._verificar_password(password, usuario.password):
                return {"success": False, "message": "Credenciales inválidas", "data": None}

            # Obtener perfil según rol
            perfil = None
            if usuario.rol == 'cliente':
                resp_cliente = self.clienteDAO.obtener_por_usuario(usuario.id_usuario)
                if resp_cliente.data:
                    perfil = Cliente(**resp_cliente.data[0])
            elif usuario.rol == 'empleado':
                resp_empleado = self.empleadoDAO.obtener_por_usuario(usuario.id_usuario)
                if resp_empleado.data:
                    perfil = Empleado(**resp_empleado.data[0])
            elif usuario.rol == 'administrador':
                resp_admin = self.adminDAO.obtener_por_usuario(usuario.id_usuario)
                if resp_admin.data:
                    perfil = Administrador(**resp_admin.data[0])

            AuthManager.usuario_actual = usuario
            
            return {
                "success": True,
                "message": "Inicio de sesión exitoso",
                "data": {
                    "usuario": usuario,
                    "perfil": perfil,
                    "rol": usuario.rol
                }
            }
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            return {"success": False, "message": f"Error en autenticación: {str(e)}", "data": None}

    # ------------------------------------------------------------------
    # REGISTRO DE CLIENTE
    # ------------------------------------------------------------------
    def registrarCliente(self, nombre, telefono, email, direccion, password):
        """
        Registra un nuevo usuario con rol Cliente
        
        Args:
            nombre: Nombre completo
            telefono: Teléfono de contacto (opcional)
            email: Email único
            direccion: Dirección (opcional)
            password: Contraseña
            
        Returns:
            dict con success, message, data
        """
        try:
            # Validaciones
            if not nombre or not email or not password:
                return {"success": False, "message": "Nombre, email y contraseña son requeridos", "data": None}
            
            if not self._validar_email(email):
                return {"success": False, "message": "Formato de email inválido", "data": None}
            
            es_valida, mensaje = self._validar_password(password)
            if not es_valida:
                return {"success": False, "message": mensaje, "data": None}

            # Verificar si el email ya existe
            existe = self.usuarioDAO.obtener_por_email(email)
            if existe.data:
                return {"success": False, "message": "El email ya está registrado", "data": None}

            # Crear usuario
            hashed = self._hash_password(password)
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

            # Crear perfil de cliente
            nuevo_cliente = Cliente(
                id_usuario=id_usuario,
                telefono=telefono,
                direccion=direccion
            )

            resp_cli = self.clienteDAO.crear(nuevo_cliente)
            if not resp_cli.data:
                # TODO: Rollback del usuario creado
                return {"success": False, "message": "Error al crear perfil de cliente", "data": None}

            return {
                "success": True,
                "message": "Cliente registrado exitosamente",
                "data": {
                    "usuario": Usuario(**resp_user.data[0]),
                    "cliente": Cliente(**resp_cli.data[0])
                }
            }
        except Exception as e:
            logger.error(f"Error al registrar cliente: {str(e)}")
            return {"success": False, "message": f"Error al registrar cliente: {str(e)}", "data": None}

    # ------------------------------------------------------------------
    # REGISTRO DE EMPLEADO
    # ------------------------------------------------------------------
    def registrarEmpleado(self, nombre, email, password, id_sede, cargo, fecha_ingreso=None):
        """
        Registra un nuevo usuario con rol Empleado
        
        Args:
            nombre: Nombre completo
            email: Email único
            password: Contraseña
            id_sede: ID de la sede donde trabajará
            cargo: Cargo del empleado
            fecha_ingreso: Fecha de ingreso (opcional, default: hoy)
            
        Returns:
            dict con success, message, data
        """
        try:
            # Validaciones
            if not nombre or not email or not password or not id_sede:
                return {"success": False, "message": "Nombre, email, contraseña y sede son requeridos", "data": None}
            
            if not self._validar_email(email):
                return {"success": False, "message": "Formato de email inválido", "data": None}
            
            es_valida, mensaje = self._validar_password(password)
            if not es_valida:
                return {"success": False, "message": mensaje, "data": None}

            # Verificar si el email ya existe
            existe = self.usuarioDAO.obtener_por_email(email)
            if existe.data:
                return {"success": False, "message": "El email ya está registrado", "data": None}

            # Crear usuario
            hashed = self._hash_password(password)
            nuevo_usuario = Usuario(
                nombre=nombre,
                email=email,
                password=hashed,
                rol="empleado"
            )

            resp_user = self.usuarioDAO.crear(nuevo_usuario)
            if not resp_user.data:
                return {"success": False, "message": "Error al crear usuario", "data": None}

            id_usuario = resp_user.data[0]["id_usuario"]

            # Crear perfil de empleado
            nuevo_empleado = Empleado(
                id_usuario=id_usuario,
                id_sede=id_sede,
                cargo=cargo,
                fecha_ingreso=fecha_ingreso if fecha_ingreso else date.today()
            )

            resp_emp = self.empleadoDAO.crear(nuevo_empleado)
            if not resp_emp.data:
                # TODO: Rollback del usuario creado
                return {"success": False, "message": "Error al crear perfil de empleado", "data": None}

            return {
                "success": True,
                "message": "Empleado registrado exitosamente",
                "data": {
                    "usuario": Usuario(**resp_user.data[0]),
                    "empleado": Empleado(**resp_emp.data[0])
                }
            }
        except Exception as e:
            logger.error(f"Error al registrar empleado: {str(e)}")
            return {"success": False, "message": f"Error al registrar empleado: {str(e)}", "data": None}

    # ------------------------------------------------------------------
    # REGISTRO DE ADMINISTRADOR
    # ------------------------------------------------------------------
    def registrarAdministrador(self, nombre, email, password, nivel_acceso="basico"):
        """
        Registra un nuevo usuario con rol Administrador
        
        Args:
            nombre: Nombre completo
            email: Email único
            password: Contraseña
            nivel_acceso: Nivel de acceso (basico, intermedio, avanzado, total)
            
        Returns:
            dict con success, message, data
        """
        try:
            # Validaciones
            if not nombre or not email or not password:
                return {"success": False, "message": "Nombre, email y contraseña son requeridos", "data": None}
            
            if not self._validar_email(email):
                return {"success": False, "message": "Formato de email inválido", "data": None}
            
            es_valida, mensaje = self._validar_password(password)
            if not es_valida:
                return {"success": False, "message": mensaje, "data": None}
            
            # Validar nivel de acceso
            if nivel_acceso not in Administrador.NIVELES_ACCESO:
                return {"success": False, "message": f"Nivel de acceso inválido. Use: {', '.join(Administrador.NIVELES_ACCESO)}", "data": None}

            # Verificar si el email ya existe
            existe = self.usuarioDAO.obtener_por_email(email)
            if existe.data:
                return {"success": False, "message": "El email ya está registrado", "data": None}

            # Crear usuario
            hashed = self._hash_password(password)
            nuevo_usuario = Usuario(
                nombre=nombre,
                email=email,
                password=hashed,
                rol="administrador"
            )

            resp_user = self.usuarioDAO.crear(nuevo_usuario)
            if not resp_user.data:
                return {"success": False, "message": "Error al crear usuario", "data": None}

            id_usuario = resp_user.data[0]["id_usuario"]

            # Crear perfil de administrador
            nuevo_admin = Administrador(
                id_usuario=id_usuario,
                nivel_acceso=nivel_acceso
            )

            resp_admin = self.adminDAO.crear(nuevo_admin)
            if not resp_admin.data:
                # TODO: Rollback del usuario creado
                return {"success": False, "message": "Error al crear perfil de administrador", "data": None}

            return {
                "success": True,
                "message": "Administrador registrado exitosamente",
                "data": {
                    "usuario": Usuario(**resp_user.data[0]),
                    "administrador": Administrador(**resp_admin.data[0])
                }
            }
        except Exception as e:
            logger.error(f"Error al registrar administrador: {str(e)}")
            return {"success": False, "message": f"Error al registrar administrador: {str(e)}", "data": None}

    # ------------------------------------------------------------------
    # USUARIO ACTUAL
    # ------------------------------------------------------------------
    def usuarioLogueado(self):
        """Retorna el usuario actualmente logueado"""
        return AuthManager.usuario_actual
    
    def cerrarSesion(self):
        """Cierra la sesión del usuario actual"""
        AuthManager.usuario_actual = None
        return {"success": True, "message": "Sesión cerrada exitosamente"}
