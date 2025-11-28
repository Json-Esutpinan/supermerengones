# Supermerengones - Sistema de Pedidos

## 📋 Requisitos Previos

- Python 3.8 o superior
- Cuenta en Supabase (https://supabase.com)
- Postman (para probar la API)

## 📁 Estructura del Proyecto

```
supermerengones/
│
├── dao/
│   ├── __init__.py
│   └── proveedorDAO.py          # Acceso a datos (Supabase)
│
├── entidades/
│   ├── __init__.py
│   └── proveedor.py             # Modelo de datos
│
├── manager/
│   ├── __init__.py
│   └── proveedorManager.py      # Lógica de negocio
│
├── config.py                     # Configuración de Supabase
├── views.py                      # API endpoints
├── api_urls.py                   # Rutas de la API
├── urls.py                       # URLs principales
├── settings.py                   # Configuración Django
├── manage.py                     # Script de Django
├── requirements.txt              # Dependencias
├── .env                          #variables de entorno
└── README.md                     # Este archivo
```

---

## ✅ Validaciones Implementadas

- **Nombre:** Requerido, máximo 100 caracteres
- **Email:** Formato válido, único en el sistema
- **Teléfono:** Máximo 20 caracteres
- **Dirección:** Máximo 255 caracteres
- **Eliminación lógica:** Los proveedores se desactivan, no se eliminan

---

## 🔧 Troubleshooting

### Error: "Import 'rest_framework' could not be resolved"

Asegúrate de haber instalado las dependencias:
```bash
pip install -r requirements.txt
```

### Error de conexión a Supabase

Verifica que:
1. Las credenciales en `.env` sean correctas
2. La tabla `proveedor` exista en Supabase
3. Las políticas de seguridad (RLS) estén configuradas o deshabilitadas para pruebas

### El servidor no inicia

Ejecuta las migraciones de Django (aunque no uses el ORM):
```bash
python manage.py migrate
```

---

## 👥 Autor

Proyecto estudiantil - HU5 Registro de Proveedores

---

## 📝 Notas

- Este es un proyecto estudiantil
- Usa Supabase como base de datos
- No usa los modelos de Django (ORM), sino entidades personalizadas
- La funcionalidad está lista para probar con Postman
- Implementa eliminación lógica (campo `activo`)

---

## 🌐 Mapa de Páginas y Roles

| Página / Ruta                                    | Nombre Vista / Acción                | Roles Permitidos                          | Notas |
|--------------------------------------------------|--------------------------------------|-------------------------------------------|-------|
| `/`                                              | index                                | Público (no autenticado)                  | Página inicio + equipo |
| `/productos/`                                    | productos                            | Público / Autenticado                     | Fallback a SAMPLE_PRODUCTS si error DB |
| `/promociones/`                                  | promociones                          | Público / Autenticado                     | Lista promociones activas |
| `/sedes/`                                        | sedes                                | Público / Autenticado                     | Lista sedes activas |
| `/carrito/`                                      | carrito                              | Autenticado (cualquier rol)               | Usa sesión para items |
| `/dashboard/`                                    | dashboard                            | Autenticado (cualquier rol)               | Accesos rápidos |
| `/admin-panel/`                                  | admin_panel                          | administrador                             | Panel global |
| `/admin-panel/registrar-empleado/`               | registrar_empleado_ui                | administrador                             | Crear empleado |
| `/admin-panel/registrar-administrador/`          | registrar_administrador_ui           | administrador                             | Crear administrador |
| `/reclamos/mis/`                                 | reclamos_mis                         | cliente                                   | Reclamos propios |
| `/reclamos/crear/`                               | reclamo_crear                        | cliente                                   | Crear reclamo (requiere id_pedido) |
| `/reclamos/todos/`                               | reclamos_todos                       | administrador                             | Lista global |
| `/reclamos/<id>/resolver/` (POST)                | reclamo_resolver_ui                  | administrador                             | Resolver reclamo |
| `/reclamos/<id>/rechazar/` (POST)                | reclamo_rechazar_ui                  | administrador                             | Rechazar reclamo |
| `/pedidos/mis/`                                  | pedidos_mis                          | cliente                                   | Historial cliente |
| `/pedidos/todos/`                                | pedidos_todos                        | administrador, empleado                   | Listado general |
| `/pedidos/<id>/`                                 | pedido_detalle                       | Autenticado (cualquier rol)               | Considerar restringir solo dueño / staff |
| `/pedidos/crear/`                                | pedido_crear                         | cliente                                   | Crear pedido básico |
| `/pedidos/<id>/<accion>/` (POST)                 | pedido_accion_estado                 | administrador, empleado                   | aceptar|preparar|entregar|cancelar |
| `/verificar/producto/`                           | producto_disponibilidad              | administrador, empleado                   | Chequear disponibilidad |
| `/verificar/inventario/`                         | inventario_verificar                 | administrador, empleado                   | Verificar stock insumo |
| `/proveedor/estadisticas/`                       | proveedor_estadisticas               | administrador                             | Estadísticas por proveedor |
| `/proveedores/`                                  | proveedores_listar                   | administrador                             | Listar proveedores |
| `/proveedores/crear/`                            | proveedor_crear                      | administrador                             | Crear proveedor |
| `/proveedores/<id>/editar/`                      | proveedor_editar                     | administrador                             | Editar proveedor |
| `/compras/`                                      | compras_listar                       | administrador, empleado                   | Listar compras |
| `/compras/registrar/`                            | compra_registrar                     | administrador, empleado                   | Registrar compra |
| `/inventario/movimientos/`                       | inventario_movimientos               | administrador, empleado                   | Entradas / salidas / transferencias |
| `/login/`                                        | login_view                           | Público                                   | Establece sesión + rol |
| `/register/`                                     | register_view                        | Público                                   | Registra cliente |
| `/logout/`                                       | logout_view                          | Autenticado                               | Cierra sesión |

---

## 🔐 Control de Acceso & Seguridad

1. Decorador `role_required` aplicado a todas las vistas sensibles (admin / empleado).
2. Vistas solo autenticadas usan `@login_required` o el decorador que lo incluye.
3. Formularios HTML incluyen `{% csrf_token %}` para protección CSRF.
4. Respuestas 403 personalizadas con plantilla (`supermerengones/403.html`).
5. Sesión almacena `user_rol` tras login y se valida contra los roles declarados.
6. Recomendación pendiente: Restringir `pedido_detalle` para evitar visualización de pedidos ajenos (verificación de ownership) o limitar a roles staff.

Checklist rápido verificación (última revisión):
- [x] Reclamos admin sólo con `administrador`
- [x] Acciones estado pedido protegidas (`empleado|administrador`)
- [x] Proveedores CRUD sólo `administrador`
- [x] Compras y movimientos inventario `empleado|administrador`
- [x] Estadísticas proveedor sólo `administrador`

---

## 🧭 Cómo Extender

- Añadir nueva vista restringida: usar `@role_required('administrador')` (o roles necesarios).
- Validar ownership: obtener id_usuario desde email y cruzar con entidad.
- Plantilla 403 reutilizable para denegaciones.

---

## 🛡️ Riesgos Detectados / Mitigaciones

| Riesgo | Impacto | Mitigación Propuesta |
|--------|---------|----------------------|
| Acceso a pedidos ajenos (pedido_detalle) | Privacidad de datos | Implementado: verificación ownership por `id_cliente` en sesión |
| Falta de rate limiting | Posible abuso escritura | Implementar throttling a nivel reverse proxy / middleware |
| Manejo de errores genérico en managers | Mensajes poco específicos | Loguear excepciones con nivel WARNING/ERROR |

---

## 🗂️ Referencia Decorador de Roles

Ubicación: `utils/roles.py`
Uso básico:
```python
@role_required('administrador', 'empleado')
def vista_protegida(request):
	...
```

---

## 📌 Próximos Pasos Sugeridos

- Implementar verificación ownership en `pedido_detalle`.
- Añadir página de perfil del usuario.
- Agregar reportes (ventas, insumos críticos) con rol `administrador`.
- Logging estructurado de acciones críticas (creación compra, movimiento inventario).

