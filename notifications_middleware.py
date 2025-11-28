from dao.notificacionDAO import NotificacionDAO

class NotificacionesCountMiddleware:
    """Inyecta conteo de notificaciones no leídas en request para el template base."""
    def __init__(self, get_response):
        self.get_response = get_response
        self.dao = NotificacionDAO()

    def __call__(self, request):
        request.unread_notif_count = 0
        try:
            if request.user.is_authenticated:
                rol = request.session.get('user_rol')
                if rol == 'cliente':
                    id_cliente = request.session.get('id_cliente')
                    if id_cliente:
                        request.unread_notif_count = self.dao.contar_no_leidas(id_cliente)
        except Exception:
            request.unread_notif_count = 0
        return self.get_response(request)
