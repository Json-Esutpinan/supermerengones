from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from config import get_supabase_client, TABLA_PRODUCTO
from manager.sedeManager import SedeManager
from django.contrib.auth.decorators import login_required
from manager.authManager import AuthManager
import bcrypt
from dao.usuarioDAO import UsuarioDAO
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from datetime import datetime
from manager.reclamoManager import ReclamoManager
from manager.pedidoManager import PedidoManager
from dao.clienteDAO import ClienteDAO
from manager.proveedorManager import ProveedorManager
from manager.inventarioManager import InventarioManager
from manager.productoManager import ProductoManager
from utils.roles import role_required
from manager.compraManager import CompraManager
from dao.productoInsumoDAO import ProductoInsumoDAO
from dao.productoDAO import ProductoDAO
from dao.notificacionDAO import NotificacionDAO
from manager.insumoManager import InsumoManager
from manager.sedeManager import SedeManager
from dao.detalleCompraDAO import DetalleCompraDAO
from dao.detallePedidoDAO import DetallePedidoDAO
from manager.asistenciaManager import AsistenciaManager
from utils.validation import (
    validate_reclamo,
    validate_pedido,
    validate_perfil,
    validate_proveedor,
    validate_compra,
    validate_producto,
    validate_insumo,
    validate_turno,
    validate_promocion,
)
from utils.structured_logging import log_event
from utils.security import rate_limit
from utils.user_helpers import get_usuario_cliente
from utils.catalog_cache import get_or_cache

reclamo_manager = ReclamoManager()
pedido_manager = PedidoManager()
cliente_dao = ClienteDAO()
proveedor_manager = ProveedorManager()
inventario_manager = InventarioManager()
producto_manager = ProductoManager()
compra_manager = CompraManager()
insumo_manager = InsumoManager()
producto_insumo_dao = ProductoInsumoDAO()
producto_dao = ProductoDAO()
sede_manager = SedeManager()
from manager.turnoManager import TurnoManager
from dao.empleadoDAO import EmpleadoDAO
turno_manager = TurnoManager()
detalle_compra_dao = DetalleCompraDAO()
asistencia_manager = AsistenciaManager()
detalle_pedido_dao = DetallePedidoDAO()

# Datos de ejemplo de productos (temporal, hasta integrar DB)
SAMPLE_PRODUCTS = [
    {'id': 1, 'name': 'Merengón Fresa', 'price': 8000, 'tag': 'fresa'},
    {'id': 2, 'name': 'Merengón Maracuyá', 'price': 9000, 'tag': 'maracuya'},
    {'id': 3, 'name': 'Merengón Mixto', 'price': 10000, 'tag': 'mixto'},
]

# Equipo actualizado con los nombres proporcionados por el usuario
TEAM = [
    {'name': 'Dana Castro', 'role': 'Diseñadora & Administradora', 'bio': 'Diseñadora principal del proyecto y responsable del look & feel.', 'avatar': 'fresa'},
    {'name': 'Juan Beltrán', 'role': 'Desarrollador & Administrador', 'bio': 'Desarrollador backend y administrador del sistema.', 'avatar': 'maracuya'},
    {'name': 'Cristian Gama', 'role': 'Desarrollador & Administrador', 'bio': 'Desarrollador fullstack, responsable de funcionalidades.', 'avatar': 'mixto'},
    {'name': 'Andres Gonzales', 'role': 'Desarrollador & Administrador', 'bio': 'Desarrollador frontend y mantenimiento de UI.', 'avatar': 'fresa'},
    {'name': 'Jeison Estupiñan', 'role': 'Desarrollador & Administrador', 'bio': 'Desarrollador e integraciones con APIs.', 'avatar': 'maracuya'},
]


def index(request):
    """Renderiza la página de inicio con 'Sobre nosotros' y la sección 'Nuestro equipo'."""
    context = {
        'team': TEAM,
    }
    return render(request, 'supermerengones/index.html', context)


def productos(request):
    """Renderiza la página de productos cargando desde la base de datos (Supabase).

    Si hay un error al consultar la base, cae en los SAMPLE_PRODUCTS como respaldo.
    """
    def _load_productos():
        productos_norm = []
        try:
            supabase = get_supabase_client()
            resp = supabase.table(TABLA_PRODUCTO).select('*').eq('activo', True).execute()
            data = resp.data if resp and getattr(resp, 'data', None) is not None else []
            for row in data:
                pid = row.get('id_producto') or row.get('id') or row.get('ID')
                productos_norm.append({
                    'id': pid,
                    'name': row.get('nombre') or row.get('name') or 'Producto',
                    'price': row.get('precio') or row.get('price') or 0,
                    'tag': row.get('tag') or 'mixto',
                })
        except Exception:
            productos_norm = SAMPLE_PRODUCTS
        return productos_norm

    products = get_or_cache('productos_activos', ttl=120, loader=_load_productos)

    context = {'products': products}
    return render(request, 'supermerengones/productos.html', context)


# ------------------------- API BÁSICA -------------------------
def api_productos_activos(request):
    """Devuelve JSON con productos activos (id, nombre, precio, tag)."""
    def _load_productos():
        productos_norm = []
        try:
            supabase = get_supabase_client()
            resp = supabase.table(TABLA_PRODUCTO).select('*').eq('activo', True).execute()
            data = resp.data if resp and getattr(resp, 'data', None) is not None else []
            for row in data:
                pid = row.get('id_producto') or row.get('id') or row.get('ID')
                productos_norm.append({
                    'id': pid,
                    'nombre': row.get('nombre') or row.get('name') or 'Producto',
                    'precio': row.get('precio') or row.get('price') or 0,
                    'tag': row.get('tag') or 'mixto',
                })
        except Exception:
            productos_norm = SAMPLE_PRODUCTS
        return productos_norm
    products = _load_productos()
    return JsonResponse({'success': True, 'data': products})


@login_required
def api_pedidos_cliente(request):
    """Devuelve JSON con pedidos del cliente autenticado (usa sesión)."""
    info = get_usuario_cliente(request)
    id_cliente = info.get('id_cliente')
    if not id_cliente:
        return JsonResponse({'success': False, 'message': 'Cliente no identificado'}, status=400)
    res = pedido_manager.obtenerHistorialCliente(id_cliente)
    pedidos = [p.to_dict() for p in res.get('data', [])] if res.get('success') else []
    return JsonResponse({'success': True, 'data': pedidos})


def api_pedido_crear_token(request):
    """Crea pedido vía token simple en header Authorization: Bearer <token>.

    Para proyecto estudiantil: token simulado = email del usuario registrado.
    Campos esperados (POST JSON): id_sede, items[{id_producto,cantidad}].
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    import json
    # Extraer token
    auth = request.META.get('HTTP_AUTHORIZATION') or ''
    token = None
    if auth.lower().startswith('bearer '):
        token = auth[7:].strip()
    if not token:
        return JsonResponse({'success': False, 'message': 'Token requerido'}, status=401)
    # Simular lookup de usuario por email=token en tabla usuario
    try:
        supabase = get_supabase_client()
        uresp = supabase.table('usuario').select('*').eq('email', token).limit(1).execute()
        if not uresp or not uresp.data:
            return JsonResponse({'success': False, 'message': 'Token inválido'}, status=401)
        usuario_row = uresp.data[0]
        if usuario_row.get('rol') != 'cliente':
            return JsonResponse({'success': False, 'message': 'Solo clientes pueden crear pedidos'}, status=403)
        id_usuario = usuario_row.get('id_usuario')
        c_resp = ClienteDAO().obtener_por_usuario(id_usuario)
        if not c_resp or not c_resp.data:
            return JsonResponse({'success': False, 'message': 'Cliente no encontrado'}, status=400)
        id_cliente = c_resp.data[0].get('id_cliente')
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error auth: {str(e)}'}, status=500)

    # Parsear body
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        payload = {}
    id_sede = payload.get('id_sede')
    items = payload.get('items') or []
    errors = validate_pedido(id_sede, items)
    if errors:
        return JsonResponse({'success': False, 'message': errors}, status=400)
    try:
        if hasattr(pedido_manager, 'crearPedido'):
            resp = pedido_manager.crearPedido(id_cliente=id_cliente, id_sede=int(id_sede), items=items)
        else:
            resp = {'success': False, 'message': 'crearPedido no implementado'}
    except Exception as e:
        resp = {'success': False, 'message': str(e)}
    if resp.get('success'):
        data_obj = resp.get('data')
        try:
            pedido_id = data_obj.to_dict().get('id_pedido') if hasattr(data_obj, 'to_dict') else data_obj.get('id_pedido')
        except Exception:
            pedido_id = None
        log_event('pedido_creado_api', id_pedido=pedido_id, id_cliente=id_cliente, id_sede=id_sede, items=items, success=True)
        return JsonResponse({'success': True, 'data': {'id_pedido': pedido_id}})
    else:
        log_event('pedido_creado_api_failed', id_cliente=id_cliente, id_sede=id_sede, items=items, success=False, message=resp.get('message'))
        return JsonResponse({'success': False, 'message': resp.get('message')}, status=400)


def api_pedido_detalle(request, id_pedido):
    """Devuelve JSON con encabezado del pedido y líneas enriquecidas con nombre de producto."""
    # Encabezado
    res = pedido_manager.obtenerDetallePedido(id_pedido)
    pedido = res.get('data').to_dict() if res.get('success') and res.get('data') else None
    if not pedido:
        return JsonResponse({'success': False, 'message': 'Pedido no encontrado'}, status=404)
    # Líneas usando DAO (ya enriquecidas con producto_nombre)
    try:
        det = detalle_pedido_dao.listar_por_pedido(id_pedido)
        lineas = det.data if getattr(det, 'success', False) else []
    except Exception as e:
        lineas = []
    return JsonResponse({'success': True, 'data': {'pedido': pedido, 'lineas': lineas}})


# ------------------------- API AUTH ENTRY GUARDS -------------------------
def api_auth_login_entry(request):
    """Wrapper: if accessed via browser (GET or non-JSON), redirect to HTML login.

    Otherwise delegate to API auth login handler.
    """
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('login'))
    ct = request.META.get('CONTENT_TYPE', '')
    if 'application/json' not in ct.lower():
        return HttpResponseRedirect(reverse('login'))
    try:
        from views.viewsAuth import login_view as api_login_view
    except Exception:
        return HttpResponseRedirect(reverse('login'))
    return api_login_view(request)


def api_auth_register_entry(request):
    """Wrapper: redirect to HTML register for GET/non-JSON; else delegate to API registrar cliente."""
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('register'))
    ct = request.META.get('CONTENT_TYPE', '')
    if 'application/json' not in ct.lower():
        return HttpResponseRedirect(reverse('register'))
    try:
        from views.viewsAuth import registrar_cliente_view as api_registrar_cliente
    except Exception:
        return HttpResponseRedirect(reverse('register'))
    return api_registrar_cliente(request)


def api_auth_logout_entry(request):
    """Wrapper: for GET redirect to HTML logout; else delegate to API logout handler."""
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('logout'))
    try:
        from views.viewsAuth import cerrar_sesion_view as api_logout_view
    except Exception:
        return HttpResponseRedirect(reverse('logout'))
    return api_logout_view(request)


def promociones(request):
    """Renderiza la página de promociones leyendo desde la tabla 'promocion' en la DB.
    
    Cada promoción puede mostrar productos asociados mediante la tabla 'promocion_producto'.
    """
    promos = []
    try:
        supabase = get_supabase_client()
        resp = supabase.table('promocion').select('*').eq('activo', True).execute()
        data = resp.data if resp and getattr(resp, 'data', None) is not None else []
        
        for row in data:
            pid = row.get('id_promocion') or row.get('id')
            promo_data = {
                'id': pid,
                'titulo': row.get('titulo') or row.get('name') or 'Promoción',
                'descripcion': row.get('descripcion') or row.get('descripcion_corta') or '',
                'tipo': row.get('tipo'),
                'valor': row.get('valor'),
                'imagen_url': row.get('imagen_url') or row.get('imagen') or None,
                'fecha_inicio': row.get('fecha_inicio'),
                'fecha_fin': row.get('fecha_fin'),
                'activo': row.get('activo', True),
                'productos': [],
            }
            
            # Obtener productos asociados (opcional, requiere tabla promocion_producto)
            try:
                rel = supabase.table('promocion_producto').select('id_producto').eq('id_promocion', pid).execute()
                producto_ids = [r['id_producto'] for r in (rel.data or [])]
                if producto_ids:
                    prod_resp = supabase.table(TABLA_PRODUCTO).select('*').in_('id_producto', producto_ids).execute()
                    promo_data['productos'] = prod_resp.data or []
            except Exception:
                promo_data['productos'] = []
            
            promos.append(promo_data)
    
    except Exception:
        # fallback: mostrar empty
        promos = []

    return render(request, 'supermerengones/promociones.html', {'promos': promos})


# ------------------------- PROMOCIONES CRUD (ADMIN) -------------------------
@role_required('administrador')
def promociones_admin_list(request):
    promos = []
    try:
        supabase = get_supabase_client()
        resp = supabase.table('promocion').select('*').order('id_promocion', desc=True).execute()
        promos = resp.data or []
        # contar productos asociados
        for p in promos:
            try:
                rel = supabase.table('promocion_producto').select('id_producto').eq('id_promocion', p.get('id_promocion')).execute()
                p['total_productos'] = len(rel.data or [])
            except Exception:
                p['total_productos'] = 0
    except Exception:
        promos = []
    return render(request, 'supermerengones/promociones_admin_list.html', {'promos': promos})


@role_required('administrador')
def promocion_crear(request):
    productos = []
    try:
        supabase = get_supabase_client()
        pr = supabase.table(TABLA_PRODUCTO).select('id_producto,nombre,activo').eq('activo', True).execute()
        productos = pr.data or []
    except Exception:
        productos = []
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        tipo = request.POST.get('tipo')
        valor = request.POST.get('valor')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        seleccion = request.POST.getlist('productos')  # lista de ids
        # Unicidad títulos
        existing_titulos = set()
        try:
            supabase = get_supabase_client()
            r_all = supabase.table('promocion').select('titulo').execute()
            existing_titulos = {x.get('titulo') for x in (r_all.data or []) if x.get('titulo')}
        except Exception:
            existing_titulos = set()
        errors = validate_promocion(titulo, tipo, valor, fecha_inicio, fecha_fin, descripcion, existing_titulos)
        if errors:
            for f, m in errors.items():
                messages.error(request, f"{f}: {m}")
            return render(request, 'supermerengones/promocion_crear.html', {'productos': productos})
        try:
            supabase = get_supabase_client()
            data = {
                'titulo': titulo,
                'descripcion': descripcion,
                'tipo': tipo,
                'valor': float(valor),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'activo': True,
            }
            ins = supabase.table('promocion').insert(data).execute()
            promo_id = None
            if ins and ins.data:
                promo_id = ins.data[0].get('id_promocion')
            # relaciones
            if promo_id and seleccion:
                rel_rows = [{'id_promocion': promo_id, 'id_producto': int(pid)} for pid in seleccion if pid]
                if rel_rows:
                    supabase.table('promocion_producto').insert(rel_rows).execute()
            messages.success(request, 'Promoción creada')
            return redirect('promociones_admin_list')
        except Exception as e:
            messages.error(request, f'Error al crear promoción: {str(e)}')
    return render(request, 'supermerengones/promocion_crear.html', {'productos': productos})


@role_required('administrador')
def promocion_editar(request, id_promocion):
    promo = None
    productos = []
    productos_sel = set()
    try:
        supabase = get_supabase_client()
        pr = supabase.table(TABLA_PRODUCTO).select('id_producto,nombre,activo').eq('activo', True).execute()
        productos = pr.data or []
        r_promo = supabase.table('promocion').select('*').eq('id_promocion', id_promocion).limit(1).execute()
        if r_promo and r_promo.data:
            promo = r_promo.data[0]
        rel = supabase.table('promocion_producto').select('id_producto').eq('id_promocion', id_promocion).execute()
        productos_sel = {x.get('id_producto') for x in (rel.data or [])}
    except Exception:
        promo = None
    if not promo:
        messages.error(request, 'Promoción no encontrada')
        return redirect('promociones_admin_list')
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        tipo = request.POST.get('tipo')
        valor = request.POST.get('valor')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        seleccion = request.POST.getlist('productos')
        existing_titulos = set()
        try:
            supabase = get_supabase_client()
            r_all = supabase.table('promocion').select('id_promocion,titulo').execute()
            existing_titulos = {x.get('titulo') for x in (r_all.data or []) if x.get('titulo') and x.get('id_promocion') != id_promocion}
        except Exception:
            existing_titulos = set()
        errors = validate_promocion(titulo, tipo, valor, fecha_inicio, fecha_fin, descripcion, existing_titulos)
        if errors:
            for f, m in errors.items():
                messages.error(request, f"{f}: {m}")
            return render(request, 'supermerengones/promocion_editar.html', {'promo': promo, 'productos': productos, 'productos_sel': productos_sel})
        try:
            supabase = get_supabase_client()
            upd = {
                'titulo': titulo,
                'descripcion': descripcion,
                'tipo': tipo,
                'valor': float(valor),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
            }
            supabase.table('promocion').update(upd).eq('id_promocion', id_promocion).execute()
            # Reemplazar relaciones
            supabase.table('promocion_producto').delete().eq('id_promocion', id_promocion).execute()
            rel_rows = [{'id_promocion': id_promocion, 'id_producto': int(pid)} for pid in seleccion if pid]
            if rel_rows:
                supabase.table('promocion_producto').insert(rel_rows).execute()
            messages.success(request, 'Promoción actualizada')
            return redirect('promociones_admin_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    return render(request, 'supermerengones/promocion_editar.html', {'promo': promo, 'productos': productos, 'productos_sel': productos_sel})


@role_required('administrador')
def promocion_toggle_estado(request, id_promocion):
    try:
        supabase = get_supabase_client()
        r = supabase.table('promocion').select('activo').eq('id_promocion', id_promocion).limit(1).execute()
        if not r or not r.data:
            messages.error(request, 'Promoción no encontrada')
            return redirect('promociones_admin_list')
        activo_actual = r.data[0].get('activo', True)
        supabase.table('promocion').update({'activo': not activo_actual}).eq('id_promocion', id_promocion).execute()
        messages.success(request, f"Promoción {'activada' if not activo_actual else 'inactivada'}")
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('promociones_admin_list')


def sedes(request):
    """Renderiza la página de sedes obteniendo datos desde la base (SedeManager)."""
    def _load_sedes():
        _sedes = []
        try:
            sm = SedeManager()
            resultado = sm.listarSedes(solo_activos=True)
            if resultado.get('success'):
                _sedes = [s.to_dict() if hasattr(s, 'to_dict') else s for s in resultado.get('data', [])]
        except Exception:
            _sedes = []
        return _sedes
    sedes = get_or_cache('sedes_activas', ttl=300, loader=_load_sedes)

    return render(request, 'supermerengones/sedes.html', {'sedes': sedes})

# ------------------------- SEDES CRUD (ADMIN) -------------------------
@role_required('administrador')
def sedes_admin_list(request):
    """Listado completo de sedes (admin)."""
    try:
        res = sede_manager.listarSedes(solo_activos=False)
        sedes = [s.to_dict() if hasattr(s, 'to_dict') else s for s in res.get('data', [])] if res.get('success') else []
    except Exception:
        sedes = []
    return render(request, 'supermerengones/sedes_admin_list.html', {'sedes': sedes})

@role_required('administrador')
def sede_crear(request):
    """Crear sede (admin)."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        try:
            res = sede_manager.crearSede(nombre, direccion, telefono)
        except Exception as e:
            res = {'success': False, 'message': str(e)}
        if res.get('success'):
            messages.success(request, 'Sede creada')
            return redirect('sedes_admin_list')
        messages.error(request, res.get('message') or 'Error al crear sede')
    return render(request, 'supermerengones/sede_crear.html')

@role_required('administrador')
def sede_editar(request, id_sede):
    """Editar sede (admin)."""
    # Obtener sede actual
    sede_actual = None
    try:
        r = sede_manager.obtenerSede(id_sede)
        sede_actual = r.get('data') if r.get('success') else None
    except Exception:
        sede_actual = None
    if not sede_actual:
        messages.error(request, 'Sede no encontrada')
        return redirect('sedes_admin_list')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        cambios = {
            'nombre': nombre,
            'direccion': direccion,
            'telefono': telefono,
        }
        try:
            res = sede_manager.modificarSede(id_sede, cambios)
        except Exception as e:
            res = {'success': False, 'message': str(e)}
        if res.get('success'):
            messages.success(request, 'Sede actualizada')
            return redirect('sedes_admin_list')
        messages.error(request, res.get('message') or 'Error al actualizar sede')
    return render(request, 'supermerengones/sede_editar.html', {'sede': sede_actual})

@role_required('administrador')
def sede_toggle_estado(request, id_sede):
    """Activa/Inactiva sede (admin)."""
    try:
        r = sede_manager.obtenerSede(id_sede)
        sede_obj = r.get('data') if r.get('success') else None
        if not sede_obj:
            messages.error(request, 'Sede no encontrada')
            return redirect('sedes_admin_list')
        estado_actual = sede_obj.activo if hasattr(sede_obj, 'activo') else (sede_obj.get('activo') if isinstance(sede_obj, dict) else True)
        cambio = sede_manager.cambiarEstado(id_sede, not estado_actual)
        if cambio.get('success'):
            messages.success(request, f"Sede {'activada' if not estado_actual else 'desactivada'}")
        else:
            messages.error(request, cambio.get('message') or 'No se pudo cambiar estado')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('sedes_admin_list')


def carrito(request):
    """Muestra los productos guardados en la sesión (carrito simple) con descuentos aplicados."""
    cart = request.session.get('cart', {})
    # Convertir a lista legible con aplicación de promociones
    items = []
    supabase = get_supabase_client()
    
    for pid, qty in cart.items():
        # Buscar producto de muestra o en la BD
        prod = next((p for p in SAMPLE_PRODUCTS if str(p['id']) == str(pid)), None)
        if not prod:
            try:
                resp = supabase.table(TABLA_PRODUCTO).select('*').eq('id_producto', int(pid)).execute()
                if resp and resp.data:
                    p = resp.data[0]
                    prod = {
                        'id': int(pid),
                        'name': p.get('nombre') or 'Producto',
                        'price': p.get('precio') or 0,
                    }
            except Exception:
                pass
        
        if prod:
            # Aplicar descuentos si existen promociones activas
            precio_final = prod['price']
            descuento_aplicado = False
            
            try:
                # Buscar promociones que apliquen a este producto
                rel = supabase.table('promocion_producto').select('id_promocion').eq('id_producto', int(pid)).execute()
                promo_ids = [r['id_promocion'] for r in (rel.data or [])]
                if promo_ids:
                    promo_resp = supabase.table('promocion').select('*').eq('activo', True).in_('id_promocion', promo_ids).execute()
                    for promo in (promo_resp.data or []):
                        if promo.get('tipo') == 'descuento_porcentaje':
                            precio_final = prod['price'] * (1 - promo.get('valor', 0) / 100)
                            descuento_aplicado = True
                        elif promo.get('tipo') == 'descuento_monto':
                            precio_final = max(0, prod['price'] - promo.get('valor', 0))
                            descuento_aplicado = True
            except Exception:
                pass
            
            items.append({
                'product': prod,
                'quantity': qty,
                'precio_unitario': prod['price'],
                'precio_final': precio_final,
                'total': precio_final * qty,
                'descuento_aplicado': descuento_aplicado,
            })
    
    # Calcular subtotal, impuestos y total
    subtotal = sum(item['total'] for item in items)
    tax_rate = 0.19  # Impuesto sobre venta (19%)
    tax = subtotal * tax_rate
    total = subtotal + tax
    
    context = {
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
    }
    return render(request, 'supermerengones/carrito.html', context)


@role_required('cliente')
def carrito_crear_pedido(request):
    """Crea un pedido directamente desde el carrito de la sesión."""
    if request.method != 'POST':
        return redirect('carrito')
    # Obtener cliente
    info = get_usuario_cliente(request) or {}
    id_cliente = info.get('id_cliente')
    if not id_cliente:
        messages.error(request, 'No se pudo identificar su cliente')
        return redirect('carrito')
    # Construir items desde carrito
    cart = request.session.get('cart', {})
    items = []
    try:
        for pid, qty in cart.items():
            pid_int = int(pid)
            qty_int = int(qty)
            if qty_int > 0:
                items.append({'id_producto': pid_int, 'cantidad': qty_int})
    except Exception:
        items = []
    if not items:
        messages.error(request, 'El carrito está vacío')
        return redirect('carrito')
    # Crear pedido
    try:
        if hasattr(pedido_manager, 'crearPedido'):
            resp = pedido_manager.crearPedido(id_cliente=id_cliente, detalles=items)
        else:
            resp = {'success': False, 'message': 'crearPedido no implementado'}
    except Exception as e:
        resp = {'success': False, 'message': str(e)}
    if isinstance(resp, dict) and resp.get('success'):
        # Limpiar carrito
        try:
            request.session['cart'] = {}
        except Exception:
            pass
        pedido_id = None
        data_obj = resp.get('data')
        try:
            if hasattr(data_obj, 'to_dict'):
                pedido_id = data_obj.to_dict().get('id_pedido')
            elif isinstance(data_obj, dict):
                pedido_id = data_obj.get('id_pedido')
        except Exception:
            pedido_id = None
        log_event('pedido_creado_desde_carrito', id_pedido=pedido_id, id_cliente=id_cliente, items=items, success=True)
        messages.success(request, 'Pedido creado correctamente desde el carrito')
        return redirect('pedidos_mis')
    else:
        fail_msg = None
        if isinstance(resp, dict):
            fail_msg = resp.get('message')
        if not fail_msg:
            fail_msg = 'Error al crear pedido'
        log_event('pedido_creado_desde_carrito_failed', id_cliente=id_cliente, items=items, success=False, message=fail_msg)
        messages.error(request, fail_msg)
        return redirect('carrito')


def add_to_cart(request, product_id):
    """Añade un producto al carrito. Si el usuario no está autenticado, lo redirige al login.

    Usamos la sesión para almacenar un diccionario 'cart' con {product_id: cantidad}.
    """
    if not request.user.is_authenticated:
        # redirigir al login con next para volver al producto
        login_url = reverse('login') + f'?next={request.path}'
        messages.info(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect(login_url)

    # añadir al carrito en sesión
    cart = request.session.get('cart', {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session['cart'] = cart
    messages.success(request, 'Producto añadido al carrito.')
    # Volver a la página anterior si existe
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('productos')


@rate_limit(limit=15, window=60, key='ip')
def login_view(request):
    """Maneja el inicio de sesión validando directamente contra la tabla `usuario` en Supabase.
    
    Usa bcrypt para validar contraseña.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        next_url = request.GET.get('next') or request.POST.get('next')
        if not next_url:
            next_url = reverse('dashboard')

        if not email or not password:
            messages.error(request, 'Email y contraseña requeridos.')
            return redirect(reverse('login') + f'?next={next_url}')

        # Obtener usuario directamente de Supabase
        try:
            supabase = get_supabase_client()
            resp = supabase.table('usuario').select('*').eq('email', email).execute()
            
            if not resp or not resp.data or len(resp.data) == 0:
                messages.error(request, 'Email o contraseña inválidos.')
                return redirect(reverse('login') + f'?next={next_url}')
            
            usuario_row = resp.data[0]
            nombre = usuario_row.get('nombre', '')
            password_hash = usuario_row.get('password', '')
            rol = usuario_row.get('rol', 'cliente')
            
            # Validar contraseña con bcrypt
            if not password_hash:
                messages.error(request, 'Email o contraseña inválidos.')
                return redirect(reverse('login') + f'?next={next_url}')
            
            try:
                import bcrypt
                if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    messages.error(request, 'Email o contraseña inválidos.')
                    return redirect(reverse('login') + f'?next={next_url}')
            except Exception as e:
                messages.error(request, 'Error validando contraseña.')
                return redirect(reverse('login') + f'?next={next_url}')
            
            # Contraseña válida: crear/sincronizar Django User
            try:
                django_user, created = User.objects.get_or_create(
                    username=email,
                    defaults={'email': email, 'first_name': nombre}
                )
                django_user.set_password(password)
                django_user.save()
            except Exception:
                pass
            
            # Autenticar y establecer sesión de Django
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Guardar rol en sesión
                request.session['user_rol'] = rol
                # Persistir id_cliente si aplica
                if rol == 'cliente':
                    try:
                        # Obtener id_usuario desde tabla usuario (ya tenemos usuario_row)
                        id_usuario = usuario_row.get('id_usuario')
                        if id_usuario:
                            c_resp = ClienteDAO().obtener_por_usuario(id_usuario)
                            if c_resp and c_resp.data:
                                request.session['id_cliente'] = c_resp.data[0].get('id_cliente')
                    except Exception:
                        request.session['id_cliente'] = None
                # Persistir id_empleado si aplica
                if rol == 'empleado':
                    try:
                        id_usuario = usuario_row.get('id_usuario')
                        if id_usuario:
                            from dao.empleadoDAO import EmpleadoDAO
                            e_resp = EmpleadoDAO().obtener_por_usuario(id_usuario)
                            if e_resp and getattr(e_resp, 'data', None):
                                request.session['id_empleado'] = e_resp.data[0].get('id_empleado')
                    except Exception:
                        request.session['id_empleado'] = None
                log_event('login', email=email, rol=rol, id_usuario=usuario_row.get('id_usuario'), success=True)
                messages.success(request, f'¡Bienvenido {nombre or email}!')
                return redirect(next_url)
            else:
                log_event('login_failed', email=email, reason='authenticate_failed')
                messages.error(request, 'Error al establecer sesión.')
                return redirect(reverse('login') + f'?next={next_url}')
        
        except Exception as e:
            log_event('login_failed', email=email, reason=str(e))
            messages.error(request, f'Error: {str(e)}')
            return redirect(reverse('login') + f'?next={next_url}')
    
    # GET -> renderizar form
    return render(request, 'supermerengones/login.html')


def register_view(request):
    """Crea un usuario básico usando email como username.

    Nota: esto es una implementación simple para desarrollo. En producción
    validar y sanitizar correctamente.
    """
    if request.method == 'POST':
        name = request.POST.get('name') or ''
        email = request.POST.get('email')
        password = request.POST.get('password')
        telefono = request.POST.get('telefono') or ''
        direccion = request.POST.get('direccion') or ''
        if not email or not password:
            messages.error(request, 'Email y contraseña son requeridos.')
            return redirect('register')

        # Primero, intentar crear usuario en la tabla personalizada usando AuthManager
        try:
            am = AuthManager()
            resp = am.registrarCliente(name, telefono, email, direccion, password)
            if not resp.get('success'):
                messages.error(request, resp.get('message') or 'Error al registrar usuario')
                return redirect('register')
        except Exception:
            messages.error(request, 'Error al registrar usuario')
            return redirect('register')

        # Luego, crear/sincronizar Django User para poder iniciar sesión normalmente
        try:
            if not User.objects.filter(username=email).exists():
                user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
                user.save()
        except Exception:
            pass

        messages.success(request, 'Cuenta creada. Por favor inicia sesión.')
        return redirect('login')
    return render(request, 'supermerengones/register.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('index')


@login_required
def dashboard(request):
    """Panel de usuario con las funcionalidades disponibles tras iniciar sesión."""
    # Opciones que puede realizar un usuario autenticado
    actions = [
        {'label': 'Ver Productos', 'url': reverse('productos')},
        {'label': 'Promociones', 'url': reverse('promociones')},
        {'label': 'Sedes', 'url': reverse('sedes')},
        {'label': 'Carrito', 'url': reverse('carrito')},
        {'label': 'Mi Perfil', 'url': reverse('perfil_usuario')},
        {'label': 'Historial de Pedidos', 'url': reverse('pedidos_mis')},
    ]
    return render(request, 'supermerengones/dashboard.html', {'actions': actions})


@role_required('administrador')
def admin_panel(request):
    """Panel administrativo (solo administradores)."""
    users = []
    sedes = []
    try:
        udao = UsuarioDAO()
        users = udao.listar(solo_activos=False).data or []
    except Exception:
        pass
    try:
        sm = SedeManager()
        resultado = sm.listarSedes(solo_activos=False)
        if resultado.get('success'):
            sedes = [s.to_dict() if hasattr(s, 'to_dict') else s for s in resultado.get('data', [])]
    except Exception:
        pass
    return render(request, 'supermerengones/admin_panel.html', {'users': users, 'sedes': sedes})


@role_required('administrador')
def export_pedidos_csv(request):
    """Exporta pedidos a CSV (admin) con filtros opcionales: estado, desde, hasta."""
    estado = request.GET.get('estado') or None
    desde = request.GET.get('desde') or None
    hasta = request.GET.get('hasta') or None
    pedidos = []
    try:
        if desde and hasta:
            res = pedido_manager.listarPedidosPorFecha(desde, hasta)
            pedidos = res.get('data', []) if res.get('success') else []
        else:
            res = pedido_manager.listarTodosPedidos(limite=1000)
            pedidos = res.get('data', []) if res.get('success') else []
        if estado:
            pedidos = [p for p in pedidos if (p.estado if hasattr(p, 'estado') else (p.get('estado') if isinstance(p, dict) else None)) == estado]
    except Exception:
        pedidos = []
    # Preparar respuesta CSV
    import csv
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="pedidos.csv"'
    writer = csv.writer(response)
    writer.writerow(['id_pedido', 'id_cliente', 'id_sede', 'fecha', 'estado', 'total', 'metodo_pago', 'estado_pago', 'detalles_count'])
    for p in pedidos:
        try:
            obj = p if isinstance(p, dict) else (p.to_dict() if hasattr(p, 'to_dict') else None)
            if not obj:
                continue
            detalles_count = len(obj.get('detalles', []))
            writer.writerow([
                obj.get('id_pedido'),
                obj.get('id_cliente'),
                obj.get('id_sede'),
                obj.get('fecha'),
                obj.get('estado'),
                obj.get('total'),
                obj.get('metodo_pago'),
                obj.get('estado_pago'),
                detalles_count,
            ])
        except Exception:
            continue
    return response


@role_required('administrador')
def export_productos_csv(request):
    """Exporta productos activos a CSV (admin)."""
    productos = []
    try:
        resp = producto_dao.listar_activos()
        productos = resp
    except Exception:
        productos = []
    import csv
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="productos.csv"'
    writer = csv.writer(response)
    writer.writerow(['id_producto', 'codigo', 'nombre', 'precio', 'stock', 'activo'])
    for prod in productos:
        try:
            obj = prod if isinstance(prod, dict) else (prod.to_dict() if hasattr(prod, 'to_dict') else None)
            if not obj:
                continue
            writer.writerow([
                obj.get('id_producto') or obj.get('id'),
                obj.get('codigo'),
                obj.get('nombre') or obj.get('name'),
                obj.get('precio') or obj.get('price'),
                obj.get('stock'),
                obj.get('activo'),
            ])
        except Exception:
            continue
    return response


@role_required('administrador')
def admin_top_productos(request):
    """Top productos por cantidad vendida y subtotal."""
    rows = []
    try:
        supabase = get_supabase_client()
        # Agregación básica desde detalle_pedido
        resp = supabase.table('detalle_pedido').select('id_producto,cantidad,subtotal').execute()
        data = resp.data or []
        agg = {}
        for d in data:
            pid = d.get('id_producto')
            cant = int(d.get('cantidad') or 0)
            sub = float(d.get('subtotal') or 0.0)
            if pid is None:
                continue
            if pid not in agg:
                agg[pid] = {'cantidad': 0, 'subtotal': 0.0}
            agg[pid]['cantidad'] += cant
            agg[pid]['subtotal'] += sub
        # Obtener nombres
        pids = list(agg.keys())
        nombres = {}
        if pids:
            pr = supabase.table(TABLA_PRODUCTO).select('id_producto,nombre').in_('id_producto', pids).execute()
            for r in (pr.data or []):
                nombres[r.get('id_producto')] = r.get('nombre')
        for pid, st in agg.items():
            rows.append({'id_producto': pid, 'nombre': nombres.get(pid, f'Producto {pid}'), 'cantidad_total': st['cantidad'], 'subtotal_total': st['subtotal']})
        rows.sort(key=lambda r: r['cantidad_total'], reverse=True)
    except Exception:
        rows = []
    return render(request, 'supermerengones/admin_top_productos.html', {'rows': rows})


# ------------------------- REGISTRO MULTI-ROL (ADMIN) -------------------------
@role_required('administrador')
def registrar_empleado_ui(request):
    """Formulario para registrar empleados."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        id_sede = request.POST.get('id_sede')
        cargo = request.POST.get('cargo')
        if all([nombre, email, password, id_sede, cargo]):
            try:
                am = AuthManager()
                resp = am.registrarEmpleado(nombre, email, password, id_sede, cargo)
                if resp.get('success'):
                    messages.success(request, 'Empleado registrado correctamente')
                    return redirect('admin_panel')
                else:
                    messages.error(request, resp.get('message'))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Todos los campos son requeridos')
    return render(request, 'supermerengones/registrar_empleado.html')


@role_required('administrador')
def registrar_administrador_ui(request):
    """Formulario para registrar otro administrador."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        nivel_acceso = request.POST.get('nivel_acceso') or 'basico'
        if all([nombre, email, password]):
            try:
                am = AuthManager()
                resp = am.registrarAdministrador(nombre, email, password, nivel_acceso)
                if resp.get('success'):
                    messages.success(request, 'Administrador registrado correctamente')
                    return redirect('admin_panel')
                else:
                    messages.error(request, resp.get('message'))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Nombre, email y contraseña son requeridos')
    return render(request, 'supermerengones/registrar_administrador.html')


# ------------------------- RECLAMOS FRONT -------------------------
@login_required
def reclamos_mis(request):
    """Lista reclamos del cliente autenticado."""
    info = get_usuario_cliente(request)
    id_cliente = info.get('id_cliente')
    reclamos = []
    if id_cliente:
        r = reclamo_manager.listarReclamosCliente(id_cliente)
        if r.get('success'):
            reclamos = [x.to_dict() for x in r.get('data', [])]
    return render(request, 'supermerengones/reclamos_mis.html', {'reclamos': reclamos})


@login_required
@rate_limit(limit=30, window=300, key='user')
def reclamo_crear(request):
    """Formulario simple para crear reclamo (requiere id_pedido manual)."""
    if request.method == 'POST':
        id_pedido = request.POST.get('id_pedido')
        descripcion = request.POST.get('descripcion')
        errors = validate_reclamo(id_pedido, descripcion)
        if errors:
            for field, msg in errors.items():
                messages.error(request, f"{field}: {msg}")
            return render(request, 'supermerengones/reclamo_crear.html')
        info = get_usuario_cliente(request) or {}
        id_cliente = info.get('id_cliente')
        if id_cliente and id_pedido and descripcion:
            resultado = reclamo_manager.crearReclamo(id_pedido, id_cliente, descripcion)
            if resultado.get('success'):
                reclamo_id = None
                data_obj = resultado.get('data')
                try:
                    # data may be a domain object with to_dict or a dict
                    if hasattr(data_obj, 'to_dict'):
                        reclamo_id = data_obj.to_dict().get('id_reclamo')
                    elif isinstance(data_obj, dict):
                        reclamo_id = data_obj.get('id_reclamo')
                except Exception:
                    reclamo_id = None
                log_event('reclamo_creado', id_reclamo=reclamo_id, id_cliente=id_cliente, id_pedido=id_pedido, success=True)
                messages.success(request, 'Reclamo creado')
                return redirect('reclamos_mis')
            else:
                log_event('reclamo_creado_failed', id_cliente=id_cliente, id_pedido=id_pedido, success=False, message=resultado.get('message'))
            messages.error(request, resultado.get('message'))
        else:
            log_event('reclamo_creado_failed', id_cliente=id_cliente, id_pedido=id_pedido, success=False, message='datos_incompletos')
            messages.error(request, 'Datos incompletos')
    return render(request, 'supermerengones/reclamo_crear.html')


@role_required('administrador')
def reclamos_todos(request):
    """Listado global de reclamos (admin)."""
    r = reclamo_manager.listarTodosReclamos(limite=200)
    reclamos = [x.to_dict() for x in r.get('data', [])] if r.get('success') else []
    return render(request, 'supermerengones/reclamos_todos.html', {'reclamos': reclamos})


@role_required('administrador')
def reclamo_resolver_ui(request, id_reclamo):
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        resultado = reclamo_manager.resolver_reclamo(id_reclamo, respuesta)
        messages.info(request, resultado.get('message'))
    return redirect('reclamos_todos')


@role_required('administrador')
def reclamo_rechazar_ui(request, id_reclamo):
    if request.method == 'POST':
        razon = request.POST.get('razon')
        resultado = reclamo_manager.rechazar_reclamo(id_reclamo, razon)
        messages.info(request, resultado.get('message'))
    return redirect('reclamos_todos')


# ------------------------- PEDIDOS FRONT -------------------------
@login_required
def pedidos_mis(request):
    """Historial pedidos cliente autenticado (solo cliente)."""
    info = get_usuario_cliente(request)
    id_cliente = info.get('id_cliente')
    pedidos = []
    if id_cliente:
        res = pedido_manager.obtenerHistorialCliente(id_cliente)
        if res.get('success'):
            pedidos = [p.to_dict() for p in res.get('data', [])]
    return render(request, 'supermerengones/pedidos_mis.html', {'pedidos': pedidos})


@role_required('administrador', 'empleado')
def pedidos_todos(request):
    """Listado general de pedidos (empleado/admin)."""
    res = pedido_manager.listarTodosPedidos(limite=200)
    pedidos = [p.to_dict() for p in res.get('data', [])] if res.get('success') else []
    return render(request, 'supermerengones/pedidos_todos.html', {'pedidos': pedidos})


@login_required
def pedido_detalle(request, id_pedido):
    res = pedido_manager.obtenerDetallePedido(id_pedido)
    pedido = res.get('data').to_dict() if res.get('success') and res.get('data') else None
    if not pedido:
        messages.error(request, 'Pedido no encontrado')
        return redirect('pedidos_todos')
    # Ownership check: clientes sólo pueden ver sus propios pedidos
    rol = request.session.get('user_rol')
    if rol == 'cliente':
        session_id_cliente = request.session.get('id_cliente')
        pedido_id_cliente = pedido.get('id_cliente')
        # Si no coincide o no hay id_cliente en sesión, denegar
        if not session_id_cliente or pedido_id_cliente != session_id_cliente:
            return render(request, 'supermerengones/403.html', status=403)
    # Cargar líneas del detalle
    try:
        det = detalle_pedido_dao.listar_por_pedido(id_pedido)
        lineas = det.data if getattr(det, 'success', False) else []
    except Exception:
        lineas = []
    return render(request, 'supermerengones/pedido_detalle.html', {'pedido': pedido, 'lineas': lineas})


@role_required('cliente')
def pedido_cancelar_cliente(request, id_pedido):
    """Permite a un cliente cancelar su pedido si está en estado 'pendiente'."""
    # Obtener pedido
    res = pedido_manager.obtenerDetallePedido(id_pedido)
    pedido_obj = res.get('data') if res.get('success') else None
    if not pedido_obj:
        messages.error(request, 'Pedido no encontrado')
        return redirect('pedidos_mis')
    pedido = pedido_obj.to_dict() if hasattr(pedido_obj, 'to_dict') else pedido_obj
    id_cliente_session = request.session.get('id_cliente')
    if not id_cliente_session or pedido.get('id_cliente') != id_cliente_session:
        return render(request, 'supermerengones/403.html', status=403)
    estado_actual = pedido.get('estado')
    if estado_actual != 'pendiente':
        messages.error(request, 'Solo se pueden cancelar pedidos pendientes')
        return redirect('pedido_detalle', id_pedido=id_pedido)
    cambio = pedido_manager.actualizarEstado(id_pedido, 'cancelado')
    if cambio.get('success'):
        from utils.structured_logging import log_event
        log_event('pedido_cancelado_cliente', id_pedido=id_pedido, id_cliente=id_cliente_session, success=True)
        messages.success(request, 'Pedido cancelado correctamente')
    else:
        messages.error(request, cambio.get('message') or 'No se pudo cancelar el pedido')
    return redirect('pedido_detalle', id_pedido=id_pedido)


# ------------------------- CREAR PEDIDO (CLIENTE) -------------------------
@login_required
def pedido_crear(request):
    """Formulario básico para crear pedido (cliente)."""
    # Cargar productos básicos para el selector
    productos = SAMPLE_PRODUCTS
    if request.method == 'POST':
        id_sede = request.POST.get('id_sede')
        items = []
        try:
            for i in range(1, 6):
                pid = request.POST.get(f'p{i}_id')
                qty = request.POST.get(f'p{i}_qty')
                if pid and qty:
                    items.append({'id_producto': int(pid), 'cantidad': int(qty)})
        except Exception:
            items = []
        errors = validate_pedido(id_sede, items)
        if errors:
            for field, msg in errors.items():
                messages.error(request, f"{field}: {msg}")
            return render(request, 'supermerengones/pedido_crear.html', {'productos': productos})
        # Obtener id_cliente usando helper (usa sesión + consulta si necesario)
        info = get_usuario_cliente(request)
        id_cliente = info.get('id_cliente')

        if not id_cliente:
            messages.error(request, 'No se pudo identificar su cliente')
            return render(request, 'supermerengones/pedido_crear.html', {'productos': productos})

        # Crear pedido usando PedidoManager si existe el método
        try:
            if hasattr(pedido_manager, 'crearPedido'):
                # PedidoManager.crearPedido espera (id_cliente, detalles)
                resp = pedido_manager.crearPedido(id_cliente=id_cliente, detalles=items)
            else:
                resp = {'success': False, 'message': 'crearPedido no implementado'}
        except Exception as e:
            resp = {'success': False, 'message': str(e)}

        if resp.get('success'):
            pedido_id = None
            data_obj = resp.get('data')
            try:
                if hasattr(data_obj, 'to_dict'):
                    pedido_id = data_obj.to_dict().get('id_pedido')
                elif isinstance(data_obj, dict):
                    pedido_id = data_obj.get('id_pedido')
            except Exception:
                pedido_id = None
            log_event('pedido_creado', id_pedido=pedido_id, id_cliente=id_cliente, id_sede=id_sede, items=items, success=True)
            messages.success(request, 'Pedido creado correctamente')
            return redirect('pedidos_mis')
        else:
            log_event('pedido_creado_failed', id_cliente=id_cliente, id_sede=id_sede, items=items, success=False, message=resp.get('message'))
            messages.error(request, resp.get('message') or 'Error al crear pedido')
    # Prefill from cart if available (GET): map session cart to items
    prefilled_items = []
    try:
        cart = request.session.get('cart', {})
        # Load basic product options
        supabase = get_supabase_client()
        for i, (pid, qty) in enumerate(cart.items(), start=1):
            if i > 5:
                break
            prefilled_items.append({'slot': i, 'id': int(pid), 'qty': int(qty)})
    except Exception:
        prefilled_items = []
    return render(request, 'supermerengones/pedido_crear.html', {'productos': productos, 'prefilled_items': prefilled_items})


# ------------------------- ACCIONES ESTADO PEDIDO -------------------------
@role_required('administrador', 'empleado')
def pedido_accion_estado(request, id_pedido, accion):
    """Ejecuta acción de estado sobre el pedido: aceptar, preparar, entregar, cancelar."""
    acciones_map = {
        'aceptar': 'aceptarPedido',
        'preparar': 'marcarEnPreparacion',
        'entregar': 'marcarEntregado',
        'cancelar': 'cancelarPedido',
    }
    metodo = acciones_map.get(accion)
    if not metodo:
        messages.error(request, 'Acción no válida')
        return redirect('pedidos_todos')

    try:
        if hasattr(pedido_manager, metodo):
            func = getattr(pedido_manager, metodo)
            resp = func(id_pedido)
        else:
            resp = {'success': False, 'message': f'Método {metodo} no implementado'}
    except Exception as e:
        resp = {'success': False, 'message': str(e)}

    if resp.get('success'):
        messages.success(request, f'Pedido {accion} correctamente')
    else:
        messages.error(request, resp.get('message') or f'Error al {accion} el pedido')

    # Volver al detalle si existe, si no al listado
    return redirect('pedido_detalle', id_pedido=id_pedido)


# ------------------------- VERIFICACIONES -------------------------
@role_required('administrador', 'empleado')
def producto_disponibilidad(request):
    """Consulta disponibilidad de un producto para cierta cantidad."""
    resultado = None
    if request.method == 'POST':
        id_producto = request.POST.get('id_producto')
        cantidad = request.POST.get('cantidad')
        if id_producto and cantidad:
            try:
                cantidad = int(cantidad)
                res = producto_manager.verificar_disponibilidad(int(id_producto), cantidad)
                resultado = res
            except Exception as e:
                resultado = {'success': False, 'message': str(e)}
        else:
            resultado = {'success': False, 'message': 'Datos incompletos'}
    return render(request, 'supermerengones/producto_disponibilidad.html', {'resultado': resultado})


@role_required('administrador', 'empleado')
def inventario_verificar(request):
    """Verifica stock disponible de un insumo en una sede."""
    resultado = None
    if request.method == 'POST':
        id_insumo = request.POST.get('id_insumo')
        id_sede = request.POST.get('id_sede')
        cantidad = request.POST.get('cantidad')
        if id_insumo and id_sede and cantidad:
            try:
                cantidad = int(cantidad)
                res = inventario_manager.verificar_stock_disponible(int(id_insumo), int(id_sede), cantidad)
                resultado = res
            except Exception as e:
                resultado = {'success': False, 'message': str(e)}
        else:
            resultado = {'success': False, 'message': 'Datos incompletos'}
    return render(request, 'supermerengones/inventario_verificar.html', {'resultado': resultado})


# ------------------------- ESTADÍSTICAS PROVEEDOR -------------------------
@role_required('administrador')
def proveedor_estadisticas(request):
    """Consulta estadísticas de compras para un proveedor."""
    resultado = None
    if request.method == 'POST':
        id_proveedor = request.POST.get('id_proveedor')
        if id_proveedor:
            try:
                res = proveedor_manager.obtener_estadisticas(int(id_proveedor))
                resultado = res
            except Exception as e:
                resultado = {'success': False, 'message': str(e)}
        else:
            resultado = {'success': False, 'message': 'id_proveedor requerido'}
    return render(request, 'supermerengones/proveedor_estadisticas.html', {'resultado': resultado})


# ------------------------- PROVEEDORES CRUD (ADMIN) -------------------------
@role_required('administrador')
def proveedores_listar(request):
    proveedores = []
    try:
        if hasattr(proveedor_manager, 'listar'):  # suposición
            res = proveedor_manager.listar()
            proveedores = res.get('data') or [] if res.get('success') else []
    except Exception:
        proveedores = []
    return render(request, 'supermerengones/proveedores_listar.html', {'proveedores': proveedores})


@role_required('administrador')
def proveedor_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        errors = validate_proveedor(nombre, telefono, email, direccion)
        if errors:
            for field, msg in errors.items():
                messages.error(request, f"{field}: {msg}")
            return render(request, 'supermerengones/proveedor_crear.html')
        try:
            if hasattr(proveedor_manager, 'crearProveedor'):
                resp = proveedor_manager.crearProveedor(nombre, telefono, email, direccion)
            else:
                resp = {'success': False, 'message': 'crearProveedor no implementado'}
        except Exception as e:
            resp = {'success': False, 'message': str(e)}
        if resp.get('success'):
            messages.success(request, 'Proveedor creado')
            return redirect('proveedores_listar')
        messages.error(request, resp.get('message') or 'Error al crear proveedor')
    return render(request, 'supermerengones/proveedor_crear.html')


@role_required('administrador')
def proveedor_editar(request, id_proveedor):
    proveedor = None
    try:
        if hasattr(proveedor_manager, 'obtener'):  # suposición
            res = proveedor_manager.obtener(id_proveedor)
            proveedor = res.get('data') if res.get('success') else None
    except Exception:
        proveedor = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        errors = validate_proveedor(nombre, telefono, email, direccion)
        if errors:
            for field, msg in errors.items():
                messages.error(request, f"{field}: {msg}")
            return render(request, 'supermerengones/proveedor_editar.html', {'proveedor': proveedor})
        try:
            if hasattr(proveedor_manager, 'actualizarProveedor'):
                resp = proveedor_manager.actualizarProveedor(id_proveedor, nombre, telefono, email, direccion)
            else:
                resp = {'success': False, 'message': 'actualizarProveedor no implementado'}
        except Exception as e:
            resp = {'success': False, 'message': str(e)}
        if resp.get('success'):
            messages.success(request, 'Proveedor actualizado')
            return redirect('proveedores_listar')
        messages.error(request, resp.get('message') or 'Error al actualizar proveedor')
    return render(request, 'supermerengones/proveedor_editar.html', {'proveedor': proveedor})


# ------------------------- COMPRAS (ADMIN/EMPLEADO) -------------------------
@role_required('administrador', 'empleado')
def compras_listar(request):
    compras = []
    try:
        if hasattr(compra_manager, 'listarCompras'):
            res = compra_manager.listarCompras(limite=200)
            compras = res.get('data') or [] if res.get('success') else []
    except Exception:
        compras = []
    return render(request, 'supermerengones/compras_listar.html', {'compras': compras})


@role_required('administrador', 'empleado')
def compra_registrar(request):
    proveedores = []
    insumos = []
    try:
        if hasattr(proveedor_manager, 'listar'):
            pr = proveedor_manager.listar()
            proveedores = pr.get('data') or [] if pr.get('success') else []
        if hasattr(insumo_manager, 'listar'):
            def _load_insumos():
                try:
                    ir_local = insumo_manager.listar()
                    return ir_local.get('data') or [] if ir_local.get('success') else []
                except Exception:
                    return []
            insumos = get_or_cache('insumos_lista', ttl=300, loader=_load_insumos)
    except Exception:
        pass
    if request.method == 'POST':
        id_proveedor = request.POST.get('id_proveedor')
        items = []
        try:
            for i in range(1, 6):
                iid = request.POST.get(f'i{i}_id')
                qty = request.POST.get(f'i{i}_qty')
                if iid and qty:
                    items.append({'id_insumo': int(iid), 'cantidad': int(qty)})
        except Exception:
            items = []
        errors = validate_compra(id_proveedor, items)
        if errors:
            for field, msg in errors.items():
                messages.error(request, f"{field}: {msg}")
            return render(request, 'supermerengones/compra_registrar.html', {'proveedores': proveedores, 'insumos': insumos})
        try:
            if hasattr(compra_manager, 'registrarCompra'):
                resp = compra_manager.registrarCompra(int(id_proveedor), items)
            else:
                resp = {'success': False, 'message': 'registrarCompra no implementado'}
        except Exception as e:
            resp = {'success': False, 'message': str(e)}
        if resp.get('success'):
            compra_id = None
            data_obj = resp.get('data')
            try:
                if hasattr(data_obj, 'to_dict'):
                    compra_id = data_obj.to_dict().get('id_compra')
                elif isinstance(data_obj, dict):
                    compra_id = data_obj.get('id_compra')
            except Exception:
                compra_id = None
            log_event('compra_registrada', id_compra=compra_id, id_proveedor=id_proveedor, items=items, success=True)
            messages.success(request, 'Compra registrada')
            return redirect('compras_listar')
        messages.error(request, resp.get('message') or 'Error al registrar compra')
        log_event('compra_registrada_failed', id_proveedor=id_proveedor, items=items, success=False, message=resp.get('message'))
    return render(request, 'supermerengones/compra_registrar.html', {'proveedores': proveedores, 'insumos': insumos})


# ------------------------- INVENTARIO MOVIMIENTOS -------------------------
@role_required('administrador', 'empleado')
def inventario_movimientos(request):
    """Registrar entradas, salidas o transferencias de stock."""
    resultado = None
    if request.method == 'POST':
        tipo = request.POST.get('tipo')  # entrada|salida|transferencia
        id_insumo = request.POST.get('id_insumo')
        id_sede_origen = request.POST.get('id_sede_origen')
        id_sede_destino = request.POST.get('id_sede_destino')
        cantidad = request.POST.get('cantidad')
        try:
            cantidad = int(cantidad)
        except Exception:
            cantidad = None
        try:
            if tipo == 'entrada' and hasattr(inventario_manager, 'registrar_entrada'):
                resultado = inventario_manager.registrar_entrada(int(id_insumo), int(id_sede_origen), cantidad)
            elif tipo == 'salida' and hasattr(inventario_manager, 'registrar_salida'):
                resultado = inventario_manager.registrar_salida(int(id_insumo), int(id_sede_origen), cantidad)
            elif tipo == 'transferencia' and hasattr(inventario_manager, 'transferir_stock'):
                resultado = inventario_manager.transferir_stock(int(id_insumo), int(id_sede_origen), int(id_sede_destino), cantidad)
            else:
                resultado = {'success': False, 'message': 'Operación no implementada'}
        except Exception as e:
            resultado = {'success': False, 'message': str(e)}
        log_event('inventario_movimiento', tipo=tipo, id_insumo=id_insumo, id_sede_origen=id_sede_origen, id_sede_destino=id_sede_destino, cantidad=cantidad, success=resultado.get('success'), message=resultado.get('message'))
    return render(request, 'supermerengones/inventario_movimientos.html', {'resultado': resultado})


# ------------------------- PERFIL USUARIO -------------------------
@login_required
def perfil_usuario(request):
    """Muestra resumen de pedidos y reclamos recientes del cliente (si aplica)."""
    rol = request.session.get('user_rol')
    id_cliente = request.session.get('id_cliente')
    pedidos = []
    reclamos = []
    if rol == 'cliente' and id_cliente:
        try:
            p_res = pedido_manager.obtenerHistorialCliente(id_cliente)
            if p_res.get('success'):
                pedidos = [p.to_dict() for p in (p_res.get('data') or [])][:10]
        except Exception:
            pedidos = []
        try:
            r_res = reclamo_manager.listarReclamosCliente(id_cliente)
            if r_res.get('success'):
                reclamos = [r.to_dict() for r in (r_res.get('data') or [])][:10]
        except Exception:
            reclamos = []
    return render(request, 'supermerengones/perfil_usuario.html', {
        'rol': rol,
        'id_cliente': id_cliente,
        'pedidos': pedidos,
        'reclamos': reclamos,
    })


@role_required('cliente')
def perfil_editar(request):
    """Permite editar telefono y direccion del cliente autenticado."""
    id_cliente = request.session.get('id_cliente')
    cliente = None
    if id_cliente:
        try:
            c_resp = ClienteDAO().obtener_por_id(id_cliente)
            if c_resp and c_resp.data:
                cliente = c_resp.data[0]
        except Exception:
            cliente = None
    if request.method == 'POST' and id_cliente:
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        errors = validate_perfil(telefono, direccion)
        if errors:
            for field, msg in errors.items():
                messages.error(request, f"{field}: {msg}")
            return render(request, 'supermerengones/perfil_editar.html', {'cliente': cliente})
        # Validar que haya cambios reales
        if cliente and telefono == cliente.get('telefono') and direccion == cliente.get('direccion'):
            messages.error(request, 'No se detectaron cambios')
            return render(request, 'supermerengones/perfil_editar.html', {'cliente': cliente})
        try:
            upd = ClienteDAO().actualizar(id_cliente, telefono=telefono, direccion=direccion)
            if upd.get('success'):
                messages.success(request, 'Perfil actualizado correctamente')
                return redirect('perfil_usuario')
            else:
                messages.error(request, upd.get('message'))
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    return render(request, 'supermerengones/perfil_editar.html', {'cliente': cliente})


# ------------------------- ADMIN KPIs -------------------------
@role_required('administrador')
def admin_kpis(request):
    """Dashboard de KPIs administrativos.

    Métricas incluidas:
    - pedidos_por_estado: conteo agrupado.
    - top_productos: placeholder (requiere detallePedidoDAO no implementado).
    - insumos_criticos: insumos con nivel critico según inventario.
    - compras_recientes: últimas compras registradas.
    """
    pedidos_por_estado = {}
    total_pedidos = 0
    try:
        res_ped = pedido_manager.listarTodosPedidos(limite=500)
        if res_ped.get('success'):
            for p in res_ped.get('data', []):
                estado = getattr(p, 'estado', None) or (p.to_dict().get('estado') if hasattr(p, 'to_dict') else None) or 'desconocido'
                pedidos_por_estado[estado] = pedidos_por_estado.get(estado, 0) + 1
            total_pedidos = sum(pedidos_por_estado.values())
    except Exception:
        pedidos_por_estado = {}

    # Top productos: no disponible sin DetallePedidoDAO funcional
    top_productos = []
    top_productos_msg = 'No disponible: detallePedidoDAO no implementado'

    insumos_criticos = []
    try:
        alertas = inventario_manager.verificarAlertasReposicion(None)
        if alertas.get('exito'):
            insumos_criticos = [a for a in alertas.get('alertas', []) if a.get('nivel') == 'critico']
    except Exception:
        insumos_criticos = []

    compras_recientes = []
    try:
        res_comp = compra_manager.listarCompras(limite=10)
        if res_comp.get('success'):
            compras_recientes = res_comp.get('data', [])
    except Exception:
        compras_recientes = []

    context = {
        'pedidos_por_estado': pedidos_por_estado,
        'total_pedidos': total_pedidos,
        'top_productos': top_productos,
        'top_productos_msg': top_productos_msg,
        'insumos_criticos': insumos_criticos,
        'compras_recientes': compras_recientes,
    }
    return render(request, 'supermerengones/admin_kpis.html', context)


# ------------------------- AUDITORÍA LOGS (ADMIN) -------------------------
@role_required('administrador')
def auditoria_logs(request):
    """Visor simple de logs estructurados (JSONL) para admins.

    Requiere configurar la variable de entorno APP_LOG_FILE para habilitar lectura desde archivo.
    Filtros opcionales por query string: event (substring), success (true/false), desde/hasta (YYYY-MM-DD), limit.
    """
    import os, json
    from datetime import datetime, date

    log_file = os.getenv('APP_LOG_FILE')
    if not log_file:
        return render(request, 'supermerengones/auditoria_logs.html', {
            'entries': [],
            'configured': False,
            'message': 'No hay archivo de logs configurado. Defina APP_LOG_FILE para habilitar el visor.'
        })

    q_event = request.GET.get('event') or ''
    q_success = request.GET.get('success')  # 'true'|'false'|None
    q_desde = request.GET.get('desde')  # 'YYYY-MM-DD'
    q_hasta = request.GET.get('hasta')  # 'YYYY-MM-DD'
    try:
        limit = int(request.GET.get('limit', '200'))
    except Exception:
        limit = 200

    def parse_date_iso(s):
        try:
            return datetime.fromisoformat(s)
        except Exception:
            try:
                return datetime.strptime(s, '%Y-%m-%d')
            except Exception:
                return None

    # Build date range
    dt_desde = parse_date_iso(q_desde) if q_desde else None
    dt_hasta = parse_date_iso(q_hasta) if q_hasta else None
    if dt_hasta:
        # include full day if only date was provided
        try:
            if len(q_hasta) == 10:
                dt_hasta = dt_hasta.replace(hour=23, minute=59, second=59, microsecond=999999)
        except Exception:
            pass

    entries = []
    # Read file and parse JSON lines
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        lines = []

    # Parse and filter
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        # Quick normalize
        ts = obj.get('ts')
        evt = obj.get('event', '') or ''
        succ = obj.get('success') if 'success' in obj else None
        # Filter by event substring
        if q_event and q_event.lower() not in str(evt).lower():
            continue
        # Filter by success
        if q_success == 'true' and succ is not True:
            continue
        if q_success == 'false' and succ is not False:
            continue
        # Filter by date range
        if ts and (dt_desde or dt_hasta):
            try:
                # support both with Z and without
                ts_clean = ts.replace('Z', '')
                dt_ts = parse_date_iso(ts_clean)
            except Exception:
                dt_ts = None
            if dt_desde and dt_ts and dt_ts < dt_desde:
                continue
            if dt_hasta and dt_ts and dt_ts > dt_hasta:
                continue
        entries.append(obj)

    # Sort by timestamp desc if available
    def sort_key(o):
        t = o.get('ts')
        try:
            return parse_date_iso((t or '').replace('Z', '')) or datetime.min
        except Exception:
            return datetime.min
    entries.sort(key=sort_key, reverse=True)
    entries = entries[:max(1, min(1000, limit))]

    return render(request, 'supermerengones/auditoria_logs.html', {
        'entries': entries,
        'configured': True,
        'filters': {
            'event': q_event,
            'success': q_success,
            'desde': q_desde,
            'hasta': q_hasta,
            'limit': limit,
        }
    })


# ------------------------- RECETA PRODUCTO (ADMIN) -------------------------
@role_required('administrador')
def producto_receta_editar(request, id_producto):
    """Permite editar la 'receta' (insumos y cantidades) de un producto.

    Usa ProductoInsumoDAO.reemplazar_insumos_de_producto para guardar la lista completa.
    El formulario envía arrays 'insumo_id' y 'cantidad'.
    """
    # Obtener producto
    producto = None
    try:
        producto = producto_dao.obtener_por_id(id_producto)
    except Exception:
        producto = None

    # Receta actual
    receta = []
    try:
        receta = producto_insumo_dao.listar_por_producto(id_producto)
    except Exception:
        receta = []

    # Helper para calcular costos unitarios de insumos (promedio ponderado últimas compras)
    def _costos_unitarios(receta_lista, limite=50):
        costos = {}
        for linea in receta_lista:
            iid = getattr(linea, 'id_insumo', None)
            if iid is None:
                continue
            try:
                detalles = detalle_compra_dao.listar_por_insumo(iid, limite=limite)
            except Exception:
                detalles = []
            total_sub = 0.0
            total_cant = 0.0
            for d in detalles:
                try:
                    cant = float(d.get('cantidad') or 0)
                    sub = float(d.get('subtotal') or 0)
                except Exception:
                    cant = 0.0
                    sub = 0.0
                total_cant += cant
                total_sub += sub
            if total_cant > 0:
                costos[iid] = total_sub / total_cant
        return costos

    costos_insumos = _costos_unitarios(receta)
    costo_receta = None
    costo_breakdown = []
    if receta:
        try:
            costo_receta = producto_insumo_dao.calcular_costo_producto(id_producto, costos_insumos)
            for linea in receta:
                iid = linea.id_insumo
                cant = linea.cantidad_necesaria
                unit = costos_insumos.get(iid)
                line_total = unit * cant if (unit is not None and cant is not None) else None
                costo_breakdown.append({
                    'id_insumo': iid,
                    'cantidad': cant,
                    'costo_unitario': unit,
                    'costo_linea': line_total,
                })
        except Exception:
            costo_receta = None

    # Lista de insumos activos para seleccionar
    insumos = []
    try:
        if hasattr(insumo_manager, 'listar'):
            r_ins = insumo_manager.listar()
            if r_ins.get('success'):
                insumos = r_ins.get('data') or []
    except Exception:
        insumos = []

    if request.method == 'POST':
        insumo_ids = request.POST.getlist('insumo_id')
        cantidades = request.POST.getlist('cantidad')
        nueva_lista = []
        for iid, cant in zip(insumo_ids, cantidades):
            iid = iid.strip()
            cant = cant.strip()
            if iid and cant:
                try:
                    nueva_lista.append({'id_insumo': int(iid), 'cantidad_necesaria': float(cant)})
                except Exception:
                    continue
        if not nueva_lista:
            messages.error(request, 'Debe especificar al menos un insumo con cantidad')
            # Recalcular costos con receta original (sin cambios válidos)
            costos_insumos = _costos_unitarios(receta)
            costo_receta = producto_insumo_dao.calcular_costo_producto(id_producto, costos_insumos) if receta else None
            costo_breakdown = []
            for linea in receta:
                iid = linea.id_insumo
                cant = linea.cantidad_necesaria
                unit = costos_insumos.get(iid)
                line_total = unit * cant if (unit is not None and cant is not None) else None
                costo_breakdown.append({
                    'id_insumo': iid,
                    'cantidad': cant,
                    'costo_unitario': unit,
                    'costo_linea': line_total,
                })
            return render(request, 'supermerengones/producto_receta_editar.html', {
                'producto': producto,
                'receta': receta,
                'insumos': insumos,
                'costo_receta': costo_receta,
                'costo_breakdown': costo_breakdown,
            })
        try:
            reemplazo = producto_insumo_dao.reemplazar_insumos_de_producto(id_producto, nueva_lista)
            if reemplazo:
                messages.success(request, 'Receta actualizada correctamente')
                log_event('receta_actualizada', id_producto=id_producto, total_lineas=len(reemplazo), success=True)
                return redirect('producto_receta_editar', id_producto=id_producto)
            else:
                messages.warning(request, 'Receta vacía tras actualización')
                log_event('receta_actualizada', id_producto=id_producto, total_lineas=0, success=True)
                return redirect('producto_receta_editar', id_producto=id_producto)
        except Exception as e:
            messages.error(request, f'Error al actualizar receta: {str(e)}')
            log_event('receta_actualizada_failed', id_producto=id_producto, error=str(e), success=False)

    return render(request, 'supermerengones/producto_receta_editar.html', {
        'producto': producto,
        'receta': receta,
        'insumos': insumos,
        'costo_receta': costo_receta,
        'costo_breakdown': costo_breakdown,
    })


# ------------------------- PANEL FUNCIONALIDADES (ADMIN) -------------------------
@role_required('administrador')
def admin_funcionalidades(request):
    """Panel resumen del estado de implementación de funcionalidades.

    Muestra tarjetas con: nombre, estado (Implementado / Pendiente / En progreso), descripción y enlace si aplica.
    """
    # Definición estática inicial (podría evolucionar a dinámica leyendo managers, DAOs, etc.)
    funcionalidades = [
        {'clave': 'reclamos', 'nombre': 'Reclamos', 'estado': 'Implementado', 'descripcion': 'Gestión de reclamos (listar, crear, resolver, rechazar).', 'url': 'reclamos_todos'},
        {'clave': 'pedidos', 'nombre': 'Pedidos', 'estado': 'Implementado', 'descripcion': 'Creación y administración de pedidos con cambio de estado.', 'url': 'pedidos_todos'},
        {'clave': 'proveedores', 'nombre': 'Proveedores', 'estado': 'Implementado', 'descripcion': 'CRUD básico y estadísticas por proveedor.', 'url': 'proveedores_listar'},
        {'clave': 'compras', 'nombre': 'Compras', 'estado': 'Implementado', 'descripcion': 'Registro de compras con selección de insumos.', 'url': 'compras_listar'},
        {'clave': 'inventario_mov', 'nombre': 'Movimientos Inventario', 'estado': 'Implementado', 'descripcion': 'Entradas, salidas y transferencias de insumos.', 'url': 'inventario_movimientos'},
        {'clave': 'recetas', 'nombre': 'Recetas', 'estado': 'Implementado', 'descripcion': 'Edición de composición producto–insumos y cálculo costo receta.', 'url': 'producto_receta_editar'},
        {'clave': 'notificaciones', 'nombre': 'Notificaciones', 'estado': 'Implementado', 'descripcion': 'Listado cliente/admin, badge unread, marcar leídas (una/todas), envío masivo.'},
        # Actualizado con filtros y segmentación
        {'clave': 'sedes', 'nombre': 'Sedes', 'estado': 'Implementado', 'descripcion': 'CRUD completo de sedes (crear, editar, activar/inactivar).'},
        {'clave': 'turnos', 'nombre': 'Turnos', 'estado': 'Implementado', 'descripcion': 'Programación, edición y eliminación de turnos + vista Mis Turnos empleado.'},
        {'clave': 'asistencia', 'nombre': 'Asistencia', 'estado': 'Implementado', 'descripcion': 'Registro de entrada/salida, estado y reporte diario.'},
        {'clave': 'productos_crud', 'nombre': 'Productos CRUD', 'estado': 'Implementado', 'descripcion': 'Crear, editar, activar/inactivar productos (vista stock bajo pendiente).'},
        {'clave': 'insumos_crud', 'nombre': 'Insumos CRUD', 'estado': 'Implementado', 'descripcion': 'Crear, editar, activar/inactivar insumos (automatización reposición pendiente).'},
        {'clave': 'promociones', 'nombre': 'Promociones', 'estado': 'Implementado', 'descripcion': 'CRUD de promociones, asociación de productos y toggle activo.'},
        {'clave': 'reportes', 'nombre': 'Reportes/KPIs Avanzados', 'estado': 'Pendiente', 'descripcion': 'Top productos, consumo insumos, rotación inventario.'},
        {'clave': 'seguridad', 'nombre': 'Seguridad Cuenta', 'estado': 'Implementado', 'descripcion': 'Cambio/recuperación contraseña (stub) y gestión de sesiones.'},
        {'clave': 'auditoria', 'nombre': 'Auditoría & Mantenimiento', 'estado': 'Implementado', 'descripcion': 'Visor de logs estructurados (JSON) con filtros.', 'url': 'auditoria_logs'},
        {'clave': 'api', 'nombre': 'API & Export', 'estado': 'Pendiente', 'descripcion': 'Endpoints JSON y exportaciones CSV/Excel.'},
    ]
    return render(request, 'supermerengones/admin_funcionalidades.html', {'funcionalidades': funcionalidades})


# ------------------------- NOTIFICACIONES -------------------------
# ------------------------- SEGURIDAD CUENTA -------------------------
@login_required
def password_change(request):
    """Permite al usuario cambiar su contraseña actual."""
    if request.method == 'POST':
        actual = request.POST.get('password_actual')
        nueva = request.POST.get('password_nueva')
        confirmar = request.POST.get('password_confirmar')
        if not actual or not nueva or not confirmar:
            messages.error(request, 'Todos los campos son requeridos')
            return render(request, 'supermerengones/password_change.html')
        if nueva != confirmar:
            messages.error(request, 'La confirmación no coincide')
            return render(request, 'supermerengones/password_change.html')
        user = request.user
        # Verificar contraseña actual
        if not user.check_password(actual):
            messages.error(request, 'La contraseña actual es incorrecta')
            return render(request, 'supermerengones/password_change.html')
        # Establecer nueva contraseña
        user.set_password(nueva)
        user.save()
        messages.success(request, 'Contraseña actualizada. Vuelva a iniciar sesión.')
        return redirect('login')
    return render(request, 'supermerengones/password_change.html')

def password_reset_request(request):
    """Stub de solicitud de recuperación de contraseña (muestra token simulado)."""
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Email requerido')
            return render(request, 'supermerengones/password_reset_request.html')
        # Generar token simulado y mostrar en pantalla (placeholder)
        import secrets
        token = secrets.token_urlsafe(24)
        messages.success(request, f'Se enviaría email con token: {token}')
        return redirect('password_reset_request')
    return render(request, 'supermerengones/password_reset_request.html')

@login_required
def sessions_list(request):
    """Lista simple de sesiones activas del usuario (placeholder)."""
    # Django por defecto no expone sesiones ajenas; mostramos info básica de la actual.
    info = {
        'session_key': request.session.session_key,
        'expira': request.session.get_expiry_date(),
        'rol': request.session.get('user_rol'),
        'id_empleado': request.session.get('id_empleado'),
        'id_cliente': request.session.get('id_cliente'),
    }
    return render(request, 'supermerengones/sessions_list.html', {'session_info': info})

# ------------------------- ASISTENCIA (EMPLEADO) -------------------------
@role_required('empleado')
def asistencia_mi(request):
    """Vista para que el empleado vea su asistencia de hoy y acciones disponibles."""
    from datetime import date
    hoy = date.today().isoformat()
    registro = None
    try:
        emp_id = request.session.get('id_empleado')
        if emp_id:
            resp = asistencia_manager.asistenciaDAO.listar_por_empleado_fecha(emp_id, hoy)
            if resp.data:
                registro = resp.data[0]
    except Exception:
        registro = None
    return render(request, 'supermerengones/asistencia_mi.html', {
        'registro': registro,
    })

@role_required('empleado')
def asistencia_registrar_entrada(request):
    if request.method != 'POST':
        return redirect('asistencia_mi')
    emp_id = request.session.get('id_empleado')
    if not emp_id:
        messages.error(request, 'No se encontró empleado en sesión')
        return redirect('asistencia_mi')
    res = asistencia_manager.registrarEntrada(emp_id)
    messages.add_message(request, messages.SUCCESS if res.get('success') else messages.ERROR, res.get('message'))
    return redirect('asistencia_mi')

@role_required('empleado')
def asistencia_registrar_salida(request):
    if request.method != 'POST':
        return redirect('asistencia_mi')
    emp_id = request.session.get('id_empleado')
    if not emp_id:
        messages.error(request, 'No se encontró empleado en sesión')
        return redirect('asistencia_mi')
    # Buscar registro del día
    from datetime import date
    hoy = date.today().isoformat()
    resp = asistencia_manager.asistenciaDAO.listar_por_empleado_fecha(emp_id, hoy)
    if not resp.data:
        messages.error(request, 'No hay registro de entrada para hoy')
        return redirect('asistencia_mi')
    id_asistencia = resp.data[0].get('id_asistencia')
    res = asistencia_manager.registrarSalida(id_asistencia)
    messages.add_message(request, messages.SUCCESS if res.get('success') else messages.ERROR, res.get('message'))
    return redirect('asistencia_mi')

# ------------------------- ASISTENCIA (ADMIN) -------------------------
@role_required('administrador')
def asistencia_admin_hoy(request):
    from datetime import date
    hoy = date.today().isoformat()
    registros = []
    try:
        resp = asistencia_manager.asistenciaDAO.listar_por_fecha(hoy, limite=500)
        registros = resp.data or []
    except Exception:
        registros = []
    return render(request, 'supermerengones/asistencia_admin_hoy.html', {
        'registros': registros,
        'fecha': hoy,
    })

@role_required('administrador')
def asistencia_actualizar_estado(request, id_asistencia):
    if request.method != 'POST':
        return redirect('asistencia_admin_hoy')
    estado = request.POST.get('estado')
    obs = request.POST.get('observaciones')
    res = asistencia_manager.actualizarEstado(id_asistencia, estado, obs)
    messages.add_message(request, messages.SUCCESS if res.get('success') else messages.ERROR, res.get('message'))
    return redirect('asistencia_admin_hoy')


# ------------------------- STOCK BAJO (ADMIN) -------------------------
@role_required('administrador')
def stock_bajo_admin(request):
    """Listado dedicado de insumos en stock bajo/alerta, opcionalmente filtrado por sede.

    Usa InventarioManager.verificarAlertasReposicion(id_sede) si está disponible.
    Permite acciones rápidas: sugerencia de reposición y enlace a transferencia.
    """
    sede = request.GET.get('sede')
    id_sede = None
    try:
        if sede:
            id_sede = int(sede)
    except Exception:
        id_sede = None
    alertas = []
    try:
        res = inventario_manager.verificarAlertasReposicion(id_sede)
        if res.get('exito'):
            alertas = res.get('alertas', [])
    except Exception:
        alertas = []
    return render(request, 'supermerengones/stock_bajo_admin.html', {
        'alertas': alertas,
        'f_sede': id_sede,
    })
@role_required('cliente')
def notificaciones_cliente(request):
    dao = NotificacionDAO()
    id_cliente = request.session.get('id_cliente')
    resp = None
    notificaciones = []
    if id_cliente:
        try:
            resp = dao.listar_por_cliente(id_cliente, solo_no_leidas=False, limite=100)
            notificaciones = resp.data or []
        except Exception:
            notificaciones = []
    return render(request, 'supermerengones/notificaciones_cliente.html', {'notificaciones': notificaciones})


@role_required('cliente')
def notificacion_marcar_leida(request, id_notificacion):
    dao = NotificacionDAO()
    try:
        dao.marcar_como_leida(id_notificacion)
        messages.success(request, 'Notificación marcada como leída')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('notificaciones_cliente')


@role_required('cliente')
def notificaciones_marcar_todas(request):
    dao = NotificacionDAO()
    id_cliente = request.session.get('id_cliente')
    if id_cliente:
        try:
            dao.marcar_todas_leidas(id_cliente)
            messages.success(request, 'Todas las notificaciones marcadas como leídas')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return redirect('notificaciones_cliente')


@role_required('administrador')
def notificaciones_admin(request):
    dao = NotificacionDAO()
    # Filtros via query params
    rol = request.GET.get('rol') or None
    sede = request.GET.get('sede') or None
    leidas_param = request.GET.get('leidas')  # 'si'|'no'|None
    leidas = None
    if leidas_param == 'si':
        leidas = True
    elif leidas_param == 'no':
        leidas = False
    try:
        page = int(request.GET.get('page', '1'))
    except Exception:
        page = 1
    page_size = 25
    sede_val = None
    try:
        if sede is not None:
            sede_val = int(sede)
    except Exception:
        sede_val = None
    listado = dao.listar_admin_filtrado(sede=sede_val, rol=rol, leidas=leidas, page=page, page_size=page_size)
    notificaciones = listado.get('data', [])
    total = listado.get('total', 0)
    last_page = (total // page_size) + (1 if total % page_size else 0)
    return render(request, 'supermerengones/notificaciones_admin.html', {
        'notificaciones': notificaciones,
        'page': page,
        'last_page': last_page,
        'total': total,
        'page_size': page_size,
        'f_rol': rol,
        'f_sede': sede_val,
        'f_leidas': leidas_param,
    })


@role_required('administrador')
def notificacion_admin_crear(request):
    """Crea notificación masiva segmentada.

    Segmentos soportados:
    - todos: todos los clientes
    - rol: actualmente solo 'cliente' (extensible a otros)
    - sede: clientes por sede
    - rol_sede: rol + sede
    """
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        mensaje = request.POST.get('mensaje')
        segmento = request.POST.get('segmento')  # todos|rol|sede|rol_sede
        rol = request.POST.get('rol')
        sede = request.POST.get('sede')
        if not titulo or not mensaje:
            messages.error(request, 'Título y mensaje requeridos')
            return render(request, 'supermerengones/notificacion_admin_crear.html')
        # Construir lista de clientes destino
        clientes = []
        try:
            cr = cliente_dao.listar_todos() if hasattr(cliente_dao, 'listar_todos') else None
            if cr and getattr(cr, 'data', None):
                clientes = cr.data
        except Exception:
            clientes = []
        # Filtrado simple (suponiendo cliente tiene sede en campo 'id_sede')
        if segmento in ('sede', 'rol_sede') and sede:
            try:
                sid = int(sede)
                clientes = [c for c in clientes if (c.get('id_sede') == sid or getattr(c, 'id_sede', None) == sid)]
            except Exception:
                pass
        if segmento in ('rol', 'rol_sede') and rol:
            # Todos son clientes actualmente; placeholder para otros roles
            if rol != 'cliente':
                clientes = []
        dao = NotificacionDAO()
        creadas = 0
        from entidades.notificacion import Notificacion
        for c in clientes:
            id_cliente = c.get('id_cliente') if isinstance(c, dict) else getattr(c, 'id_cliente', None)
            if not id_cliente:
                continue
            try:
                n = Notificacion(id_notificacion=None, id_cliente=id_cliente, titulo=titulo, mensaje=mensaje, leida=False)
                dao.crear(n)
                creadas += 1
            except Exception:
                continue
        messages.success(request, f'Notificaciones enviadas: {creadas}')
        return redirect('notificaciones_admin')
    return render(request, 'supermerengones/notificacion_admin_crear.html')


# ------------------------- PRODUCTOS CRUD (ADMIN) -------------------------
@role_required('administrador', 'empleado')
def productos_admin_list(request):
    """Listado de productos (admin/empleado)."""
    productos = []
    try:
        productos = producto_dao.listar_todos(limite=500)
    except Exception:
        productos = []
    return render(request, 'supermerengones/productos_admin_list.html', {'productos': productos})


@role_required('administrador')
def producto_crear(request):
    """Crear producto (admin)."""
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        id_unidad = request.POST.get('id_unidad')
        contenido = request.POST.get('contenido')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock') or 0
        # Unicidad códigos
        try:
            existentes = {p.codigo for p in producto_dao.listar_todos(limite=1000) if p.codigo}
        except Exception:
            existentes = set()
        errors = validate_producto(codigo, nombre, precio, descripcion, id_unidad, contenido, existing_codigos=existentes)
        # Validar stock
        try:
            s_val = int(stock)
            if s_val < 0:
                errors['stock'] = 'Stock debe ser >= 0'
        except Exception:
            errors['stock'] = 'Stock inválido'
        if errors:
            for f, m in errors.items():
                messages.error(request, f"{f}: {m}")
            return render(request, 'supermerengones/producto_crear.html')
        from entidades.producto import Producto
        try:
            prod = Producto(codigo=codigo, nombre=nombre, descripcion=descripcion, id_unidad=id_unidad, contenido=contenido, precio=precio, stock=stock, activo=True)
            creado = producto_dao.insertar(prod)
            if creado:
                messages.success(request, 'Producto creado')
                return redirect('productos_admin_list')
            messages.error(request, 'No se pudo crear producto')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'supermerengones/producto_crear.html')


@role_required('administrador')
def producto_editar(request, id_producto):
    """Editar producto (admin)."""
    producto = None
    try:
        producto = producto_dao.obtener_por_id(id_producto)
    except Exception:
        producto = None
    if not producto:
        messages.error(request, 'Producto no encontrado')
        return redirect('productos_admin_list')
    if request.method == 'POST':
        codigo_original = producto.codigo
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        id_unidad = request.POST.get('id_unidad')
        contenido = request.POST.get('contenido')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock') or producto.stock
        try:
            existentes = {p.codigo for p in producto_dao.listar_todos(limite=1000) if p.codigo}
            if codigo_original in existentes:
                existentes.remove(codigo_original)
        except Exception:
            existentes = set()
        errors = validate_producto(codigo, nombre, precio, descripcion, id_unidad, contenido, existing_codigos=existentes)
        # Validar stock
        try:
            s_val = int(stock)
            if s_val < 0:
                errors['stock'] = 'Stock debe ser >= 0'
        except Exception:
            errors['stock'] = 'Stock inválido'
        if errors:
            for f, m in errors.items():
                messages.error(request, f"{f}: {m}")
            return render(request, 'supermerengones/producto_editar.html', {'producto': producto})
        datos_upd = {
            'codigo': codigo,
            'nombre': nombre,
            'descripcion': descripcion,
            'id_unidad': id_unidad,
            'contenido': contenido,
            'precio': float(precio) if precio else 0.0,
            'stock': int(stock) if stock else 0,
        }
        try:
            actualizado = producto_dao.actualizar(id_producto, datos_upd)
            if actualizado:
                messages.success(request, 'Producto actualizado')
                return redirect('productos_admin_list')
            messages.error(request, 'No se pudo actualizar producto')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'supermerengones/producto_editar.html', {'producto': producto})


@role_required('administrador')
def producto_toggle_estado(request, id_producto):
    """Activa/Inactiva producto (admin)."""
    try:
        prod = producto_dao.obtener_por_id(id_producto)
        if not prod:
            messages.error(request, 'Producto no encontrado')
            return redirect('productos_admin_list')
        nuevo_estado = not prod.activo
        actualizado = producto_dao.cambiar_estado(id_producto, nuevo_estado)
        if actualizado:
            messages.success(request, f"Producto {'activado' if nuevo_estado else 'inactivado'}")
        else:
            messages.error(request, 'No se pudo cambiar estado')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('productos_admin_list')


# ------------------------- INSUMOS CRUD (ADMIN) -------------------------
@role_required('administrador', 'empleado')
def insumos_admin_list(request):
    """Listado de insumos (admin/empleado)."""
    insumos = []
    try:
        # Usar manager si disponible, sino DAO directo
        if hasattr(insumo_manager, 'listar'):
            r = insumo_manager.listar()
            insumos = r.get('data') or [] if r.get('success') else []
        else:
            from dao.insumoDAO import InsumoDAO
            insumos = InsumoDAO().listar_todos(solo_activos=False)
    except Exception:
        insumos = []
    return render(request, 'supermerengones/insumos_admin_list.html', {'insumos': insumos})


@role_required('administrador')
def insumo_crear(request):
    """Crear insumo (admin)."""
    # Sedes para selector
    sedes = []
    try:
        from dao.sedeDAO import SedeDAO
        sd = SedeDAO().listar(solo_activos=True)
        sedes = sd.data or []
    except Exception:
        sedes = []
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        id_unidad = request.POST.get('id_unidad')
        id_sede = request.POST.get('id_sede')
        stock_minimo = request.POST.get('stock_minimo')
        try:
            existentes = set()
            if hasattr(insumo_manager, 'listar'):
                r_l = insumo_manager.listar()
                if r_l.get('success'):
                    existentes = {i.get('codigo') for i in r_l.get('data') if i.get('codigo')}
        except Exception:
            existentes = set()
        errors = validate_insumo(codigo, nombre, id_sede, id_unidad, descripcion, stock_minimo, existing_codigos=existentes)
        if errors:
            for f, m in errors.items():
                messages.error(request, f"{f}: {m}")
            return render(request, 'supermerengones/insumo_crear.html', {'sedes': sedes})
        from entidades.insumo import Insumo
        try:
            insumo_obj = Insumo(codigo=codigo, nombre=nombre, descripcion=descripcion, id_unidad=id_unidad, id_sede=int(id_sede), stock_minimo=int(stock_minimo or 0), activo=True)
            from dao.insumoDAO import InsumoDAO
            creado = InsumoDAO().insertar(insumo_obj)
            if creado:
                messages.success(request, 'Insumo creado')
                return redirect('insumos_admin_list')
            messages.error(request, 'No se pudo crear insumo')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'supermerengones/insumo_crear.html', {'sedes': sedes})


@role_required('administrador')
def insumo_editar(request, id_insumo):
    """Editar insumo (admin)."""
    from dao.insumoDAO import InsumoDAO
    insumo = None
    try:
        insumo = InsumoDAO().obtener_por_id(id_insumo)
    except Exception:
        insumo = None
    if not insumo:
        messages.error(request, 'Insumo no encontrado')
        return redirect('insumos_admin_list')
    sedes = []
    try:
        from dao.sedeDAO import SedeDAO
        sd = SedeDAO().listar(solo_activos=True)
        sedes = sd.data or []
    except Exception:
        sedes = []
    if request.method == 'POST':
        codigo_original = insumo.codigo if hasattr(insumo, 'codigo') else (insumo.get('codigo') if isinstance(insumo, dict) else None)
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        id_unidad = request.POST.get('id_unidad')
        id_sede = request.POST.get('id_sede')
        stock_minimo = request.POST.get('stock_minimo')
        try:
            existentes = set()
            if hasattr(insumo_manager, 'listar'):
                r_l = insumo_manager.listar()
                if r_l.get('success'):
                    existentes = {i.get('codigo') for i in r_l.get('data') if i.get('codigo')}
            if codigo_original in existentes:
                existentes.remove(codigo_original)
        except Exception:
            existentes = set()
        errors = validate_insumo(codigo, nombre, id_sede, id_unidad, descripcion, stock_minimo, existing_codigos=existentes)
        if errors:
            for f, m in errors.items():
                messages.error(request, f"{f}: {m}")
            return render(request, 'supermerengones/insumo_editar.html', {'insumo': insumo, 'sedes': sedes})
        cambios = {
            'codigo': codigo,
            'nombre': nombre,
            'descripcion': descripcion,
            'id_unidad': id_unidad,
            'id_sede': int(id_sede) if id_sede else None,
            'stock_minimo': int(stock_minimo) if stock_minimo else 0,
        }
        try:
            actualizado = InsumoDAO().actualizar(id_insumo, cambios)
            if actualizado:
                messages.success(request, 'Insumo actualizado')
                return redirect('insumos_admin_list')
            messages.error(request, 'No se pudo actualizar insumo')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'supermerengones/insumo_editar.html', {'insumo': insumo, 'sedes': sedes})


@role_required('administrador')
def insumo_toggle_estado(request, id_insumo):
    """Activa/Inactiva insumo (admin)."""
    from dao.insumoDAO import InsumoDAO
    try:
        insumo = InsumoDAO().obtener_por_id(id_insumo)
        if not insumo:
            messages.error(request, 'Insumo no encontrado')
            return redirect('insumos_admin_list')
        estado_actual = insumo.activo if hasattr(insumo, 'activo') else (insumo.get('activo') if isinstance(insumo, dict) else True)
        nuevo_estado = not estado_actual
        actualizado = InsumoDAO().cambiar_estado(id_insumo, nuevo_estado)
        if actualizado:
            messages.success(request, f"Insumo {'activado' if nuevo_estado else 'inactivado'}")
        else:
            messages.error(request, 'No se pudo cambiar estado')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('insumos_admin_list')


# ------------------------- TURNOS CRUD (ADMIN) -------------------------
@role_required('administrador')
def turnos_admin_list(request):
    """Listado de turnos."""
    turnos = []
    try:
        res = turno_manager.listarTodos(limite=300)
        if res.get('success'):
            turnos = res.get('data') or []
    except Exception:
        turnos = []
    return render(request, 'supermerengones/turnos_admin_list.html', {'turnos': turnos})


@role_required('administrador')
def turno_crear(request):
    """Crear turno para empleado."""
    empleados = []
    try:
        e_resp = EmpleadoDAO().listar_todos(limite=500) if hasattr(EmpleadoDAO(), 'listar_todos') else None
        if e_resp and getattr(e_resp, 'data', None):
            empleados = [e for e in e_resp.data if (e.get('usuario', {}).get('activo', True) if isinstance(e, dict) else True)]
    except Exception:
        empleados = []
    if request.method == 'POST':
        id_empleado = request.POST.get('id_empleado')
        fecha = request.POST.get('fecha')  # YYYY-MM-DD
        hora_inicio = request.POST.get('hora_inicio')  # HH:MM
        hora_fin = request.POST.get('hora_fin')  # HH:MM
        existing = []
        try:
            if id_empleado:
                r_emp = turno_manager.listarPorEmpleado(int(id_empleado), limite=500)
                if r_emp.get('success'):
                    # Filtrar solo misma fecha para validación de solape
                    existing = [t for t in r_emp.get('data', []) if str(t.get('fecha'))[:10] == fecha]
        except Exception:
            existing = []
        errors = validate_turno(id_empleado, fecha, hora_inicio, hora_fin, existing_turnos=existing)
        if errors:
            for f, m in errors.items():
                messages.error(request, f"{f}: {m}")
            return render(request, 'supermerengones/turno_crear.html', {'empleados': empleados})
        try:
            resp = turno_manager.crearTurno(int(id_empleado), fecha, hora_inicio, hora_fin)
        except Exception as e:
            resp = {'success': False, 'message': str(e)}
        if resp.get('success'):
            messages.success(request, 'Turno creado')
            return redirect('turnos_admin_list')
        messages.error(request, resp.get('message') or 'Error al crear turno')
    return render(request, 'supermerengones/turno_crear.html', {'empleados': empleados})


@role_required('administrador')
def turno_editar(request, id_turno):
    """Editar turno existente."""
    turno = None
    try:
        r = turno_manager.obtenerTurno(id_turno)
        turno = r.get('data') if r.get('success') else None
    except Exception:
        turno = None
    if not turno:
        messages.error(request, 'Turno no encontrado')
        return redirect('turnos_admin_list')
    empleados = []
    try:
        e_resp = EmpleadoDAO().listar_todos(limite=500) if hasattr(EmpleadoDAO(), 'listar_todos') else None
        if e_resp and getattr(e_resp, 'data', None):
            empleados = [e for e in e_resp.data if (e.get('usuario', {}).get('activo', True) if isinstance(e, dict) else True)]
    except Exception:
        empleados = []
    if request.method == 'POST':
        id_empleado = request.POST.get('id_empleado') or turno.get('id_empleado')
        fecha = request.POST.get('fecha') or str(turno.get('fecha'))[:10]
        hora_inicio = request.POST.get('hora_inicio') or (str(turno.get('hora_inicio'))[:5] if turno.get('hora_inicio') else None)
        hora_fin = request.POST.get('hora_fin') or (str(turno.get('hora_fin'))[:5] if turno.get('hora_fin') else None)
        existing = []
        try:
            if id_empleado:
                r_emp = turno_manager.listarPorEmpleado(int(id_empleado), limite=500)
                if r_emp.get('success'):
                    existing = [t for t in r_emp.get('data', []) if str(t.get('fecha'))[:10] == fecha and t.get('id_turno') != id_turno]
        except Exception:
            existing = []
        errors = validate_turno(id_empleado, fecha, hora_inicio, hora_fin, existing_turnos=existing)
        if errors:
            for f, m in errors.items():
                messages.error(request, f"{f}: {m}")
            return render(request, 'supermerengones/turno_editar.html', {'turno': turno, 'empleados': empleados})
        cambios = {
            'id_empleado': int(id_empleado) if id_empleado else None,
            'fecha': fecha,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
        }
        try:
            resp = turno_manager.modificarTurno(id_turno, cambios)
        except Exception as e:
            resp = {'success': False, 'message': str(e)}
        if resp.get('success'):
            messages.success(request, 'Turno actualizado')
            return redirect('turnos_admin_list')
        messages.error(request, resp.get('message') or 'Error al actualizar turno')
    return render(request, 'supermerengones/turno_editar.html', {'turno': turno, 'empleados': empleados})


@role_required('administrador')
def turno_eliminar(request, id_turno):
    """Eliminar turno."""
    try:
        resp = turno_manager.eliminarTurno(id_turno)
        if resp.get('success'):
            messages.success(request, 'Turno eliminado')
        else:
            messages.error(request, resp.get('message') or 'No se pudo eliminar turno')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('turnos_admin_list')


@role_required('empleado')
def turnos_mis(request):
    """Listado de turnos del empleado autenticado."""
    id_empleado = request.session.get('id_empleado')
    if not id_empleado:
        messages.error(request, 'Empleado no identificado en sesión')
        return redirect('dashboard')
    turnos = []
    try:
        res = turno_manager.listarPorEmpleado(int(id_empleado), limite=200)
        if res.get('success'):
            turnos = res.get('data') or []
    except Exception:
        turnos = []
    return render(request, 'supermerengones/turnos_mis.html', {'turnos': turnos})