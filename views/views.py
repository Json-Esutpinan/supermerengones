from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from config import get_supabase_client, TABLA_PRODUCTO
from manager.sedeManager import SedeManager
from django.contrib.auth.decorators import login_required


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
    products = []
    try:
        supabase = get_supabase_client()
        resp = supabase.table(TABLA_PRODUCTO).select('*').eq('activo', True).execute()
        data = resp.data if resp and getattr(resp, 'data', None) is not None else []

        for row in data:
            # Normalizar campos: usar id_producto o id como 'id'
            pid = row.get('id_producto') or row.get('id') or row.get('ID')
            products.append({
                'id': pid,
                'name': row.get('nombre') or row.get('name') or 'Producto',
                'price': row.get('precio') or row.get('price') or 0,
                'tag': row.get('tag') or 'mixto',
            })

    except Exception:
        # Fallback local
        products = SAMPLE_PRODUCTS

    context = {'products': products}
    return render(request, 'supermerengones/productos.html', context)


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


def sedes(request):
    """Renderiza la página de sedes obteniendo datos desde la base (SedeManager)."""
    sedes = []
    try:
        sm = SedeManager()
        resultado = sm.listarSedes(solo_activos=True)
        if resultado.get('success'):
            # resultado['data'] es lista de objetos Sede
            sedes = [s.to_dict() if hasattr(s, 'to_dict') else s for s in resultado.get('data', [])]
    except Exception:
        sedes = []

    return render(request, 'supermerengones/sedes.html', {'sedes': sedes})


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
    
    context = {'items': items}
    return render(request, 'supermerengones/carrito.html', context)


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


def login_view(request):
    """Maneja el inicio de sesión con Django auth; respeta el parámetro 'next'."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Usamos el email como username (según registro simple que implementamos)
        user = authenticate(request, username=email, password=password)
        next_url = request.GET.get('next') or request.POST.get('next')
        if not next_url:
            # si no hay next, llevar al usuario al dashboard
            next_url = reverse('dashboard')
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales inválidas. Intenta de nuevo.')
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
        if not email or not password:
            messages.error(request, 'Email y contraseña son requeridos.')
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Ya existe un usuario con ese email.')
            return redirect('register')

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        user.save()
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
        {'label': 'Mi Perfil', 'url': '#'},
        {'label': 'Historial de Pedidos', 'url': reverse('listar_todos_pedidos')},
    ]
    return render(request, 'supermerengones/dashboard.html', {'actions': actions})