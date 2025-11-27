# HU20 - Actualización de Estado de Pedidos

## 📋 Descripción
Sistema para actualizar el estado de los pedidos con validación de transiciones permitidas.

## 🎯 Funcionalidad Implementada

### Estados Disponibles
- `pendiente`: Pedido creado, esperando procesamiento
- `en_proceso`: Pedido siendo preparado por empleado
- `completado`: Pedido entregado al cliente
- `cancelado`: Pedido cancelado

### Matriz de Transiciones Permitidas

```
┌─────────────┬──────────────────────────────────────────────────┐
│ Estado      │ Transiciones Permitidas                          │
├─────────────┼──────────────────────────────────────────────────┤
│ pendiente   │ → en_proceso, cancelado                          │
│ en_proceso  │ → completado, cancelado                          │
│ completado  │ (ninguna - estado final)                         │
│ cancelado   │ (ninguna - estado final)                         │
└─────────────┴──────────────────────────────────────────────────┘
```

## 🛠️ Arquitectura Implementada

### 1. DAO (pedidoDAO.py)
**Método:** `actualizar_estado(id_pedido, nuevo_estado)`
- Actualiza el estado en la base de datos
- Retorna el pedido actualizado

### 2. Manager (pedidoManager.py)
**Método:** `actualizarEstado(id_pedido, nuevo_estado, id_empleado=None)`

**Validaciones:**
- ✅ Estado válido (solo: pendiente, en_proceso, completado, cancelado)
- ✅ Pedido existe en la base de datos
- ✅ Transición de estado permitida según matriz
- ✅ Estados finales no permiten cambios (completado, cancelado)

**Retorna:**
```json
{
  "success": true,
  "message": "Estado del pedido actualizado de \"pendiente\" a \"en_proceso\"",
  "data": {objeto Pedido}
}
```

### 3. Views (viewsPedidos.py)
**Endpoint:** `PATCH /api/pedidos/{id_pedido}/estado/`

**Request Body:**
```json
{
  "estado": "en_proceso",
  "id_empleado": 1  // opcional
}
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "Estado del pedido actualizado de \"pendiente\" a \"en_proceso\"",
  "data": {
    "id_pedido": 3,
    "id_cliente": 1,
    "id_sede": 1,
    "fecha": "2025-11-24T16:45:00",
    "estado": "en_proceso",
    "total": 16000.0,
    "detalles": [...]
  }
}
```

**Response Error (400):**
```json
{
  "success": false,
  "message": "Transición de estado no permitida: completado → en_proceso",
  "data": null
}
```

### 4. URLs (api_urls.py)
**Ruta registrada:**
```python
path('pedidos/<int:id_pedido>/estado/', actualizar_estado_pedido, name='actualizar_estado_pedido')
```

## 🧪 Casos de Prueba

### Escenario 1: Transiciones Válidas ✅

**1.1 Pedido pendiente → en_proceso**
```bash
PATCH http://localhost:8000/api/pedidos/3/estado/
Content-Type: application/json

{
  "estado": "en_proceso",
  "id_empleado": 1
}
```
**Resultado esperado:** ✅ 200 OK - Estado actualizado

**1.2 Pedido en_proceso → completado**
```bash
PATCH http://localhost:8000/api/pedidos/4/estado/
Content-Type: application/json

{
  "estado": "completado",
  "id_empleado": 1
}
```
**Resultado esperado:** ✅ 200 OK - Estado actualizado

**1.3 Pedido pendiente → cancelado**
```bash
PATCH http://localhost:8000/api/pedidos/3/estado/
Content-Type: application/json

{
  "estado": "cancelado",
  "id_empleado": 2
}
```
**Resultado esperado:** ✅ 200 OK - Estado actualizado

### Escenario 2: Transiciones Inválidas ❌

**2.1 Pedido completado → en_proceso**
```bash
PATCH http://localhost:8000/api/pedidos/1/estado/
Content-Type: application/json

{
  "estado": "en_proceso"
}
```
**Resultado esperado:** ❌ 400 Bad Request
```json
{
  "success": false,
  "message": "Transición de estado no permitida: completado → en_proceso"
}
```

**2.2 Pedido completado → cancelado**
```bash
PATCH http://localhost:8000/api/pedidos/2/estado/
Content-Type: application/json

{
  "estado": "cancelado"
}
```
**Resultado esperado:** ❌ 400 Bad Request

### Escenario 3: Estado Inválido ❌

```bash
PATCH http://localhost:8000/api/pedidos/3/estado/
Content-Type: application/json

{
  "estado": "entregado"
}
```
**Resultado esperado:** ❌ 400 Bad Request
```json
{
  "success": false,
  "message": "Estado inválido. Estados permitidos: pendiente, en_proceso, completado, cancelado"
}
```

### Escenario 4: Pedido No Existente ❌

```bash
PATCH http://localhost:8000/api/pedidos/9999/estado/
Content-Type: application/json

{
  "estado": "completado"
}
```
**Resultado esperado:** ❌ 400 Bad Request
```json
{
  "success": false,
  "message": "Pedido no encontrado"
}
```

### Escenario 5: Campo Faltante ❌

```bash
PATCH http://localhost:8000/api/pedidos/3/estado/
Content-Type: application/json

{
  "id_empleado": 1
}
```
**Resultado esperado:** ❌ 400 Bad Request
```json
{
  "success": false,
  "message": "El campo \"estado\" es requerido"
}
```

## 📊 Consultas SQL Útiles

### Ver resumen de pedidos por estado
```sql
SELECT 
    estado,
    COUNT(*) as cantidad,
    SUM(total) as total_ventas
FROM pedido
GROUP BY estado
ORDER BY estado;
```

### Ver cola de pedidos pendientes
```sql
SELECT 
    p.id_pedido,
    u.nombre as cliente,
    s.nombre as sede,
    p.fecha,
    p.total
FROM pedido p
JOIN cliente c ON p.id_cliente = c.id_cliente
JOIN usuario u ON c.id_usuario = u.id_usuario
JOIN sede s ON p.id_sede = s.id_sede
WHERE p.estado = 'pendiente'
ORDER BY p.fecha;
```

### Ver pedidos en proceso
```sql
SELECT 
    p.id_pedido,
    u.nombre as cliente,
    s.nombre as sede,
    p.fecha,
    p.total
FROM pedido p
JOIN cliente c ON p.id_cliente = c.id_cliente
JOIN usuario u ON c.id_usuario = u.id_usuario
JOIN sede s ON p.id_sede = s.id_sede
WHERE p.estado = 'en_proceso'
ORDER BY p.fecha;
```

## 🔗 Endpoints Relacionados

- `GET /api/pedidos/estado/{estado}/` - Listar pedidos por estado
- `GET /api/pedidos/{id_pedido}/` - Ver detalle de pedido
- `GET /api/pedidos/cliente/{id_cliente}/historial/` - Historial del cliente
- `PATCH /api/pedidos/{id_pedido}/estado/` - **Actualizar estado (HU20)**

## ✅ Checklist de Validación

- [x] DAO implementado con método `actualizar_estado()`
- [x] Manager con validaciones de transiciones de estado
- [x] Endpoint REST PATCH funcional
- [x] Validación de estados válidos
- [x] Validación de pedido existente
- [x] Validación de transiciones permitidas
- [x] Estados finales bloqueados (completado, cancelado)
- [x] Mensajes de error descriptivos
- [x] Ruta registrada en urls.py
- [x] Script de pruebas SQL creado

## 📁 Archivos Modificados/Creados

```
✅ dao/pedidoDAO.py                              (modificado - método actualizar_estado)
✅ manager/pedidoManager.py                      (modificado - método actualizarEstado)
✅ views/viewsPedidos.py                         (modificado - endpoint actualizar_estado_pedido)
✅ api_urls.py                                   (modificado - nueva ruta)
✅ datos_prueba_actualizacion_estado.sql         (nuevo)
✅ HU20_ACTUALIZACION_ESTADO.md                  (nuevo - este archivo)
```

## 🚀 Siguiente Paso
Ejecutar el servidor y probar el endpoint con los casos de prueba documentados.
