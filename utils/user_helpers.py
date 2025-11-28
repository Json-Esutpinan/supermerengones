from dao.usuarioDAO import UsuarioDAO
from dao.clienteDAO import ClienteDAO


def get_usuario_cliente(request):
    """Obtiene usuario_row, id_usuario, cliente_row, id_cliente con manejo de sesión.

    Prioriza valores ya en sesión para reducir consultas. Retorna dict:
    {
        'usuario_row': <dict|None>,
        'id_usuario': <int|None>,
        'cliente_row': <dict|None>,
        'id_cliente': <int|None>
    }
    """
    usuario_row = None
    cliente_row = None
    id_usuario = request.session.get('id_usuario')
    id_cliente = request.session.get('id_cliente')

    email = getattr(getattr(request, 'user', None), 'email', None)
    # Obtener usuario si no está cacheado
    if email and not id_usuario:
        try:
            udao = UsuarioDAO()
            resp = udao.obtener_por_email(email)
            if resp and resp.data:
                usuario_row = resp.data[0]
                id_usuario = usuario_row.get('id_usuario')
                request.session['id_usuario'] = id_usuario
        except Exception:
            usuario_row = None
    elif id_usuario and not usuario_row:
        # Podríamos implementar obtener_por_id si existiera; mantenemos None
        usuario_row = None

    # Obtener cliente si no está en sesión
    if id_usuario and not id_cliente:
        try:
            cdao = ClienteDAO()
            resp_c = cdao.obtener_por_usuario(id_usuario)
            if resp_c and resp_c.data:
                cliente_row = resp_c.data[0]
                id_cliente = cliente_row.get('id_cliente')
                request.session['id_cliente'] = id_cliente
        except Exception:
            cliente_row = None
    elif id_cliente and not cliente_row:
        try:
            cdao = ClienteDAO()
            resp_c = cdao.obtener_por_id(id_cliente)
            if resp_c and resp_c.data:
                cliente_row = resp_c.data[0]
        except Exception:
            cliente_row = None

    return {
        'usuario_row': usuario_row,
        'id_usuario': id_usuario,
        'cliente_row': cliente_row,
        'id_cliente': id_cliente,
    }
