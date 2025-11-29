from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def role_required(*roles):
    """Decorator que exige autenticación y que el rol de sesión esté dentro de roles.
    Uso:
        @role_required('administrador')
        def vista(request): ...
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            rol = request.session.get('user_rol')
            if rol not in roles:
                # Renderiza plantilla 403 personalizada
                return render(request, 'supermerengones/403.html', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
