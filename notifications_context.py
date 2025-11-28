from dao.notificacionDAO import NotificacionDAO

def notifications_badge(request):
    """Context processor que expone conteo de notificaciones no leídas como 'notif_unread'."""
    count = 0
    try:
        if request.user.is_authenticated:
            rol = request.session.get('user_rol')
            if rol == 'cliente':
                id_cliente = request.session.get('id_cliente')
                if id_cliente:
                    count = NotificacionDAO().contar_no_leidas(id_cliente)
    except Exception:
        count = 0
    return {'notif_unread': count}
