from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from entidades.usuario import Usuario
from dao.usuarioDAO import UsuarioDAO
import bcrypt


class Command(BaseCommand):
    help = 'Crea un usuario en Supabase tabla usuario con rol específico (administrador, empleado, cliente)'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email del usuario')
        parser.add_argument('--password', type=str, required=True, help='Contraseña del usuario')
        parser.add_argument('--nombre', type=str, default='', help='Nombre del usuario')
        parser.add_argument('--rol', type=str, default='cliente', 
                           help='Rol: administrador, empleado, cliente (default: cliente)')
        parser.add_argument('--telefono', type=str, default='', help='Teléfono del usuario')
        parser.add_argument('--direccion', type=str, default='', help='Dirección del usuario')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        nombre = options['nombre'] or email
        rol = options['rol'].lower()
        telefono = options['telefono']
        direccion = options['direccion']

        # Validar rol
        if rol not in ['administrador', 'empleado', 'cliente']:
            self.stdout.write(self.style.ERROR(f'Rol inválido: {rol}. Debe ser: administrador, empleado, cliente'))
            return

        # Verificar si usuario ya existe en Supabase
        udao = UsuarioDAO()
        resp = udao.obtener_por_email(email)
        if resp and resp.data:
            self.stdout.write(self.style.ERROR(f'Usuario con email {email} ya existe en Supabase'))
            return

        try:
            # Hash de contraseña con bcrypt
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Crear usuario en Supabase
            nuevo_usuario = Usuario(
                nombre=nombre,
                email=email,
                password=hashed,
                rol=rol,
                activo=True
            )

            resp_user = udao.crear(nuevo_usuario)
            if not resp_user or not resp_user.data:
                self.stdout.write(self.style.ERROR('Error al crear usuario en Supabase'))
                return

            # Crear/sincronizar Django User
            try:
                django_user, created = User.objects.get_or_create(
                    username=email,
                    defaults={'email': email, 'first_name': nombre}
                )
                django_user.set_password(password)
                django_user.save()
                status = 'creado' if created else 'actualizado'
                self.stdout.write(self.style.SUCCESS(f'Django User {status}: {email}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Django User no sincronizado: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Usuario creado exitosamente:'))
            self.stdout.write(f'  Email: {email}')
            self.stdout.write(f'  Nombre: {nombre}')
            self.stdout.write(f'  Rol: {rol}')
            self.stdout.write(f'  Teléfono: {telefono or "(vacío)"}')
            self.stdout.write(f'  Dirección: {direccion or "(vacío)"}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
