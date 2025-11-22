# API de Proveedores - Ejemplos de Uso

## 1. Crear Proveedor
```bash
POST http://127.0.0.1:8000/api/proveedores/crear/
Content-Type: application/json

{
    "nombre": "Proveedor Test",
    "email": "test@proveedor.com",
    "telefono": "3001234567",
    "direccion": "Calle 123 #45-67"
}
```

**Respuesta exitosa:**
```json
{
    "success": true,
    "message": "Proveedor creado exitosamente",
    "data": {
        "id_proveedor": 1,
        "nombre": "Proveedor Test",
        "email": "test@proveedor.com",
        "telefono": "3001234567",
        "direccion": "Calle 123 #45-67",
        "activo": true
    }
}
```

## 2. Listar Proveedores
```bash
GET http://127.0.0.1:8000/api/proveedores/
```

**Parámetros opcionales:**
- `?todos=true` - Incluir proveedores inactivos
- `?buscar=nombre` - Buscar por nombre

**Respuesta:**
```json
{
    "success": true,
    "message": "Proveedores obtenidos exitosamente",
    "data": [
        {
            "id_proveedor": 1,
            "nombre": "Proveedor Test",
            "email": "test@proveedor.com",
            "telefono": "3001234567",
            "direccion": "Calle 123 #45-67",
            "activo": true
        }
    ]
}
```

## 3. Obtener Proveedor por ID
```bash
GET http://127.0.0.1:8000/api/proveedores/1/
```

## 4. Modificar Proveedor
```bash
PUT http://127.0.0.1:8000/api/proveedores/1/modificar/
Content-Type: application/json

{
    "nombre": "Proveedor Modificado",
    "email": "modificado@proveedor.com",
    "telefono": "3009876543",
    "direccion": "Nueva dirección"
}
```

## 5. Cambiar Estado (Activar/Desactivar)
**Desactivar:**
```bash
PATCH http://127.0.0.1:8000/api/proveedores/1/estado/
Content-Type: application/json

{
    "activo": false
}
```

**Activar:**
```bash
PATCH http://127.0.0.1:8000/api/proveedores/1/estado/
Content-Type: application/json

{
    "activo": true
}
```

**Respuesta:**
```json
{
    "success": true,
    "message": "Proveedor activado exitosamente",
    "data": {
        "id_proveedor": 1,
        "nombre": "Proveedor Test",
        "email": "test@proveedor.com",
        "telefono": "3001234567",
        "direccion": "Calle 123 #45-67",
        "activo": true
    }
}
```

## 6. Desactivar Proveedor (Alternativa)
```bash
DELETE http://127.0.0.1:8000/api/proveedores/1/desactivar/
```

---

## Endpoints Disponibles

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/proveedores/crear/` | Crear proveedor |
| GET | `/api/proveedores/` | Listar proveedores |
| GET | `/api/proveedores/{id}/` | Obtener proveedor |
| PUT/PATCH | `/api/proveedores/{id}/modificar/` | Modificar proveedor |
| PATCH | `/api/proveedores/{id}/estado/` | Cambiar estado (activar/desactivar) |
| DELETE | `/api/proveedores/{id}/desactivar/` | Desactivar proveedor |
