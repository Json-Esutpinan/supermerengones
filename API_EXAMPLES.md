# API de Proveedores y Pedidos - Ejemplos de Uso

## PROVEEDORES

### 1. Crear Proveedor
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

### 2. Listar Proveedores
```bash
GET http://127.0.0.1:8000/api/proveedores/
```

### 3. Obtener Proveedor por ID
```bash
GET http://127.0.0.1:8000/api/proveedores/1/
```

### 4. Modificar Proveedor
```bash
PUT http://127.0.0.1:8000/api/proveedores/1/modificar/
Content-Type: application/json

{
    "nombre": "Proveedor Modificado",
    "telefono": "3009876543"
}
```

### 5. Cambiar Estado (Activar/Desactivar)
```bash
PATCH http://127.0.0.1:8000/api/proveedores/1/estado/
Content-Type: application/json

{
    "activo": false
}
```

---

## PEDIDOS (HU17 - Historial)

### 1. Historial de Pedidos de un Cliente
```bash
GET http://127.0.0.1:8000/api/pedidos/cliente/1/historial/
```

**Con filtros:**
```bash
# Filtrar por estado
GET http://127.0.0.1:8000/api/pedidos/cliente/1/historial/?estado=completado

# Filtrar por rango de fechas
GET http://127.0.0.1:8000/api/pedidos/cliente/1/historial/?fecha_inicio=2025-01-01&fecha_fin=2025-12-31

# Combinar filtros
GET http://127.0.0.1:8000/api/pedidos/cliente/1/historial/?estado=pendiente&fecha_inicio=2025-01-01
```

**Respuesta:**
```json
{
    "success": true,
    "message": "Se encontraron 3 pedidos",
    "data": [
        {
            "id_pedido": 1,
            "id_cliente": 1,
            "fecha": "2025-11-20T14:30:00",
            "estado": "completado",
            "total": 25000.00,
            "created_at": "2025-11-20T14:30:00",
            "detalles": [
                {
                    "id_detalle": 1,
                    "id_pedido": 1,
                    "id_producto": 101,
                    "cantidad": 2,
                    "precio_unitario": 10000.00,
                    "subtotal": 20000.00,
                    "nombre_producto": "Merengón Grande"
                }
            ]
        }
    ]
}
```

### 2. Obtener Detalle de un Pedido
```bash
GET http://127.0.0.1:8000/api/pedidos/5/
```

**Respuesta:**
```json
{
    "success": true,
    "message": "Pedido encontrado",
    "data": {
        "id_pedido": 5,
        "id_cliente": 1,
        "fecha": "2025-11-20T15:00:00",
        "estado": "pendiente",
        "total": 35000.00,
        "created_at": "2025-11-20T15:00:00",
        "detalles": [
            {
                "id_detalle": 10,
                "id_pedido": 5,
                "id_producto": 102,
                "cantidad": 3,
                "precio_unitario": 12000.00,
                "subtotal": 36000.00,
                "nombre_producto": "Merengón Especial"
            }
        ]
    }
}
```

### 3. Listar Pedidos por Estado
```bash
# Pedidos pendientes
GET http://127.0.0.1:8000/api/pedidos/estado/pendiente/

# Pedidos completados
GET http://127.0.0.1:8000/api/pedidos/estado/completado/

# Pedidos en proceso
GET http://127.0.0.1:8000/api/pedidos/estado/en_proceso/

# Pedidos cancelados
GET http://127.0.0.1:8000/api/pedidos/estado/cancelado/
```

### 4. Listar Pedidos por Rango de Fechas
```bash
GET http://127.0.0.1:8000/api/pedidos/fecha/?fecha_inicio=2025-11-01&fecha_fin=2025-11-30
```

### 5. Listar Todos los Pedidos
```bash
# Lista los primeros 100 pedidos
GET http://127.0.0.1:8000/api/pedidos/

# Con límite personalizado
GET http://127.0.0.1:8000/api/pedidos/?limite=50
```

---

## Estados de Pedido Disponibles
- `pendiente` - Pedido creado, esperando procesamiento
- `en_proceso` - Pedido en preparación
- `completado` - Pedido entregado
- `cancelado` - Pedido cancelado

---

## Endpoints Disponibles

### Proveedores
| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/proveedores/crear/` | Crear proveedor |
| GET | `/api/proveedores/` | Listar proveedores |
| GET | `/api/proveedores/{id}/` | Obtener proveedor |
| PUT/PATCH | `/api/proveedores/{id}/modificar/` | Modificar proveedor |
| PATCH | `/api/proveedores/{id}/estado/` | Cambiar estado (activar/desactivar) |
| DELETE | `/api/proveedores/{id}/desactivar/` | Desactivar proveedor |

### Pedidos (Historial - HU17)
| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/pedidos/` | Listar todos los pedidos |
| GET | `/api/pedidos/{id}/` | Obtener detalle de pedido |
| GET | `/api/pedidos/cliente/{id}/historial/` | Historial de cliente |
| GET | `/api/pedidos/estado/{estado}/` | Listar por estado |
| GET | `/api/pedidos/fecha/` | Listar por rango de fechas |
