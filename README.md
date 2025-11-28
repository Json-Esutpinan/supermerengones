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
├── views/
│   └── viewsProveedor.py        # API endpoints
|
├── config.py                     # Configuración de Supabase
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
