import re
from .security import sanitize_input

def not_empty(value: str) -> bool:
    return bool(value and str(value).strip())


def max_length(value: str, length: int) -> bool:
    return value is None or len(value) <= length


def numeric(value: str) -> bool:
    if value is None:
        return False
    return str(value).isdigit()


def positive_int(value: str) -> bool:
    if not numeric(value):
        return False
    return int(value) > 0


def validate_reclamo(id_pedido: str, descripcion: str):
    errors = {}
    descripcion = sanitize_input(descripcion)
    if not positive_int(id_pedido):
        errors['id_pedido'] = 'ID pedido inválido'
    if not not_empty(descripcion):
        errors['descripcion'] = 'Descripción requerida'
    elif not max_length(descripcion, 500):
        errors['descripcion'] = 'Descripción demasiado larga (máx 500)'
    return errors


def validate_perfil(telefono: str, direccion: str):
    errors = {}
    telefono = sanitize_input(telefono)
    direccion = sanitize_input(direccion)
    if telefono and not max_length(telefono, 20):
        errors['telefono'] = 'Teléfono supera 20 caracteres'
    if direccion and not max_length(direccion, 255):
        errors['direccion'] = 'Dirección supera 255 caracteres'
    return errors


def validate_proveedor(nombre: str, telefono: str, email: str, direccion: str):
    errors = {}
    nombre = sanitize_input(nombre)
    telefono = sanitize_input(telefono)
    email = sanitize_input(email)
    direccion = sanitize_input(direccion)
    if not not_empty(nombre):
        errors['nombre'] = 'Nombre requerido'
    elif not max_length(nombre, 100):
        errors['nombre'] = 'Nombre demasiado largo (máx 100)'
    if telefono and not max_length(telefono, 20):
        errors['telefono'] = 'Teléfono demasiado largo (máx 20)'
    if email and not max_length(email, 120):
        errors['email'] = 'Email demasiado largo'
    if direccion and not max_length(direccion, 255):
        errors['direccion'] = 'Dirección demasiado larga'
    return errors


def validate_compra(id_proveedor: str, items: list):
    errors = {}
    if not positive_int(id_proveedor):
        errors['id_proveedor'] = 'Proveedor inválido'
    if not items:
        errors['items'] = 'Debe agregar al menos un insumo'
    for i, it in enumerate(items):
        if not positive_int(str(it.get('id_insumo'))):
            errors[f'item_{i}_id'] = 'ID insumo inválido'
        if not isinstance(it.get('cantidad'), int) or it.get('cantidad') <= 0:
            errors[f'item_{i}_cantidad'] = 'Cantidad debe ser > 0'
    return errors


def validate_pedido(id_sede: str, items: list):
    """Valida un pedido.

    id_sede se considera opcional por ahora (algunas implementaciones de manager no lo requieren).
    """
    errors = {}
    # Sede opcional: validar solo si viene informada
    if id_sede is not None and str(id_sede).strip() != '':
        if not positive_int(id_sede):
            errors['id_sede'] = 'Sede inválida'
    if not items:
        errors['items'] = 'Debe seleccionar al menos un producto'
    for i, it in enumerate(items):
        if not positive_int(str(it.get('id_producto'))):
            errors[f'item_{i}_id'] = 'ID producto inválido'
        if not isinstance(it.get('cantidad'), int) or it.get('cantidad') <= 0:
            errors[f'item_{i}_cantidad'] = 'Cantidad debe ser > 0'
    return errors


def validate_producto(codigo: str, nombre: str, precio, descripcion: str = None, id_unidad: str = None,
                      contenido: str = None, existing_codigos: set = None):
    """Valida datos de producto antes de crear/actualizar.

    Args:
        codigo: Código único del producto (requerido, <=50, alfanumérico + - _ )
        nombre: Nombre del producto (requerido, <=100)
        precio: Precio (float >= 0)
        descripcion: Texto opcional (<=500)
        id_unidad: ID unidad (opcional positivo si enviado)
        contenido: Cadena tamaño/contenido (<=50)
        existing_codigos: Conjunto de códigos existentes para validar unicidad (opcional)
    Returns:
        dict de errores campo->mensaje
    """
    errors = {}
    codigo = sanitize_input(codigo) if codigo else codigo
    nombre = sanitize_input(nombre) if nombre else nombre
    descripcion = sanitize_input(descripcion) if descripcion else descripcion
    contenido = sanitize_input(contenido) if contenido else contenido

    # Código
    if not not_empty(codigo):
        errors['codigo'] = 'Código requerido'
    else:
        if not max_length(codigo, 50):
            errors['codigo'] = 'Código demasiado largo (máx 50)'
        elif not re.match(r'^[A-Za-z0-9_-]+$', codigo):
            errors['codigo'] = 'Código inválido (solo letras, números, -, _ )'
        elif existing_codigos and codigo in existing_codigos:
            errors['codigo'] = 'Código ya existe'

    # Nombre
    if not not_empty(nombre):
        errors['nombre'] = 'Nombre requerido'
    elif not max_length(nombre, 100):
        errors['nombre'] = 'Nombre demasiado largo (máx 100)'

    # Precio
    try:
        p = float(precio)
        if p < 0:
            errors['precio'] = 'Precio debe ser >= 0'
    except (TypeError, ValueError):
        errors['precio'] = 'Precio inválido'

    # Descripción
    if descripcion and not max_length(descripcion, 500):
        errors['descripcion'] = 'Descripción supera 500 caracteres'

    # id_unidad
    if id_unidad is not None and str(id_unidad).strip() != '':
        if not positive_int(str(id_unidad)):
            errors['id_unidad'] = 'Unidad inválida'

    # Contenido
    if contenido and not max_length(contenido, 50):
        errors['contenido'] = 'Contenido demasiado largo (máx 50)'

    return errors


def validate_insumo(codigo: str, nombre: str, id_sede: str, id_unidad: str = None, descripcion: str = None,
                    stock_minimo=None, existing_codigos: set = None):
    """Valida datos de insumo.

    Args:
        codigo: Código único (requerido, <=50, alfanumérico + - _ )
        nombre: Nombre (requerido, <=100)
        id_sede: Sede asociada (requerida, int > 0)
        id_unidad: Unidad de medida (opcional positivo)
        descripcion: Texto opcional (<=500)
        stock_minimo: Entero >= 0
        existing_codigos: Conjunto para validar unicidad
    Returns:
        dict errores
    """
    errors = {}
    codigo = sanitize_input(codigo) if codigo else codigo
    nombre = sanitize_input(nombre) if nombre else nombre
    descripcion = sanitize_input(descripcion) if descripcion else descripcion

    # Código
    if not not_empty(codigo):
        errors['codigo'] = 'Código requerido'
    else:
        if not max_length(codigo, 50):
            errors['codigo'] = 'Código demasiado largo (máx 50)'
        elif not re.match(r'^[A-Za-z0-9_-]+$', codigo):
            errors['codigo'] = 'Código inválido (solo letras, números, -, _ )'
        elif existing_codigos and codigo in existing_codigos:
            errors['codigo'] = 'Código ya existe'

    # Nombre
    if not not_empty(nombre):
        errors['nombre'] = 'Nombre requerido'
    elif not max_length(nombre, 100):
        errors['nombre'] = 'Nombre demasiado largo (máx 100)'

    # Sede
    if not positive_int(str(id_sede)):
        errors['id_sede'] = 'Sede inválida'

    # Unidad
    if id_unidad is not None and str(id_unidad).strip() != '':
        if not positive_int(str(id_unidad)):
            errors['id_unidad'] = 'Unidad inválida'

    # Descripción
    if descripcion and not max_length(descripcion, 500):
        errors['descripcion'] = 'Descripción supera 500 caracteres'

    # Stock mínimo
    if stock_minimo is not None and str(stock_minimo).strip() != '':
        try:
            sm = int(stock_minimo)
            if sm < 0:
                errors['stock_minimo'] = 'Stock mínimo debe ser >= 0'
        except (TypeError, ValueError):
            errors['stock_minimo'] = 'Stock mínimo inválido'

    return errors


def validate_turno(id_empleado, fecha, hora_inicio, hora_fin, existing_turnos=None):
    """Valida datos de un turno.
    existing_turnos: lista de dicts con campos 'fecha','hora_inicio','hora_fin' para el mismo empleado.
    Reglas:
      - Campos requeridos
      - Formato fecha YYYY-MM-DD
      - Formato horas HH:MM
      - hora_fin > hora_inicio
      - Duración máxima 12 horas
      - No solapamiento con otro turno del empleado en la misma fecha.
    """
    errors = {}
    if not id_empleado:
        errors['id_empleado'] = 'Empleado requerido'
    if not fecha:
        errors['fecha'] = 'Fecha requerida'
    if not hora_inicio:
        errors['hora_inicio'] = 'Hora inicio requerida'
    if not hora_fin:
        errors['hora_fin'] = 'Hora fin requerida'
    from datetime import datetime, date as _date
    fecha_dt = None
    hi_dt = None
    hf_dt = None
    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
        except Exception:
            errors['fecha'] = 'Formato fecha inválido (YYYY-MM-DD)'
    if hora_inicio:
        try:
            hi_dt = datetime.strptime(hora_inicio, '%H:%M').time()
        except Exception:
            errors['hora_inicio'] = 'Formato hora inválido (HH:MM)'
    if hora_fin:
        try:
            hf_dt = datetime.strptime(hora_fin, '%H:%M').time()
        except Exception:
            errors['hora_fin'] = 'Formato hora inválido (HH:MM)'
    if hi_dt and hf_dt and hf_dt <= hi_dt:
        errors['hora_fin'] = 'Debe ser posterior a hora inicio'
    # Duración máxima 12h
    if hi_dt and hf_dt:
        dur_hours = (datetime.combine(fecha_dt or _date.today(), hf_dt) - datetime.combine(fecha_dt or _date.today(), hi_dt)).total_seconds() / 3600.0
        if dur_hours > 12:
            errors['duracion'] = 'Duración máxima 12 horas'
    # Solapamiento
    if existing_turnos and fecha_dt and hi_dt and hf_dt:
        for t in existing_turnos:
            try:
                tf = t.get('fecha')
                if isinstance(tf, str) and len(tf) >= 10:
                    tf = tf[:10]
                if str(tf) != fecha_dt.isoformat():
                    continue
                t_hi = t.get('hora_inicio')
                t_hf = t.get('hora_fin')
                if isinstance(t_hi, str) and len(t_hi) >= 5:
                    t_hi = t_hi[:5]
                if isinstance(t_hf, str) and len(t_hf) >= 5:
                    t_hf = t_hf[:5]
                t_hi_dt = datetime.strptime(str(t_hi), '%H:%M').time()
                t_hf_dt = datetime.strptime(str(t_hf), '%H:%M').time()
                if hi_dt < t_hf_dt and hf_dt > t_hi_dt:
                    errors['overlap'] = 'Solapa con otro turno existente'
                    break
            except Exception:
                continue
    return errors


def validate_promocion(titulo: str, tipo: str, valor, fecha_inicio: str, fecha_fin: str, descripcion: str = None, existing_titulos: set = None):
    """Valida datos de promoción.
    Reglas:
      - titulo requerido <=100 y único
      - tipo en {'descuento_porcentaje','descuento_monto'}
      - valor numérico >0 (si porcentaje <=100)
      - fechas formato YYYY-MM-DD y fin >= inicio
      - descripcion opcional <=500
    """
    errors = {}
    from datetime import datetime
    titulo = sanitize_input(titulo) if titulo else titulo
    descripcion = sanitize_input(descripcion) if descripcion else descripcion
    if not not_empty(titulo):
        errors['titulo'] = 'Título requerido'
    else:
        if not max_length(titulo, 100):
            errors['titulo'] = 'Título demasiado largo (máx 100)'
        elif existing_titulos and titulo in existing_titulos:
            errors['titulo'] = 'Título ya existe'
    allowed = {'descuento_porcentaje', 'descuento_monto'}
    if tipo not in allowed:
        errors['tipo'] = 'Tipo inválido'
    # valor
    try:
        v = float(valor)
        if v <= 0:
            errors['valor'] = 'Valor debe ser > 0'
        elif tipo == 'descuento_porcentaje' and v > 100:
            errors['valor'] = 'Porcentaje máximo 100'
    except Exception:
        errors['valor'] = 'Valor inválido'
    fi_dt = ff_dt = None
    if fecha_inicio:
        try:
            fi_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        except Exception:
            errors['fecha_inicio'] = 'Formato inválido (YYYY-MM-DD)'
    else:
        errors['fecha_inicio'] = 'Fecha inicio requerida'
    if fecha_fin:
        try:
            ff_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except Exception:
            errors['fecha_fin'] = 'Formato inválido (YYYY-MM-DD)'
    else:
        errors['fecha_fin'] = 'Fecha fin requerida'
    if fi_dt and ff_dt and ff_dt < fi_dt:
        errors['fecha_fin'] = 'Fecha fin debe ser >= inicio'
    if descripcion and not max_length(descripcion, 500):
        errors['descripcion'] = 'Descripción supera 500 caracteres'
    return errors
