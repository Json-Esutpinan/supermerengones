-- =====================================
-- SCRIPT: DATOS DE PRUEBA - HU20
-- Actualización de Estado de Pedidos
-- =====================================
-- Este script crea escenarios de prueba para validar las transiciones de estado
-- Ejecutar DESPUÉS de tener datos de prueba completos

-- =====================================
-- VERIFICAR PEDIDOS ACTUALES
-- =====================================
SELECT 
    p.id_pedido,
    p.estado,
    p.fecha,
    u.nombre as cliente,
    s.nombre as sede,
    p.total
FROM pedido p
JOIN cliente c ON p.id_cliente = c.id_cliente
JOIN usuario u ON c.id_usuario = u.id_usuario
JOIN sede s ON p.id_sede = s.id_sede
ORDER BY p.fecha DESC;

-- =====================================
-- ESCENARIO 1: Transiciones Válidas
-- =====================================

-- Pedido 3: pendiente → en_proceso (VÁLIDO)
-- Este pedido está pendiente y puede pasar a en_proceso
SELECT 
    'ANTES - Pedido #3:' as descripcion,
    estado 
FROM pedido 
WHERE id_pedido = 3;

-- Para actualizar, usar el endpoint:
-- PATCH /api/pedidos/3/estado/
-- Body: {"estado": "en_proceso", "id_empleado": 1}

-- Verificar después de la actualización:
-- SELECT estado FROM pedido WHERE id_pedido = 3;
-- Resultado esperado: 'en_proceso'


-- Pedido 4: en_proceso → completado (VÁLIDO)
-- Este pedido está en proceso y puede pasar a completado
SELECT 
    'ANTES - Pedido #4:' as descripcion,
    estado 
FROM pedido 
WHERE id_pedido = 4;

-- Para actualizar, usar el endpoint:
-- PATCH /api/pedidos/4/estado/
-- Body: {"estado": "completado", "id_empleado": 1}


-- =====================================
-- ESCENARIO 2: Transiciones Inválidas (deben fallar)
-- =====================================

-- Pedido 1: completado → en_proceso (INVÁLIDO)
-- No se puede regresar de completado a en_proceso
SELECT 
    'Pedido #1 (completado):' as descripcion,
    estado 
FROM pedido 
WHERE id_pedido = 1;

-- Intentar actualizar (debe fallar):
-- PATCH /api/pedidos/1/estado/
-- Body: {"estado": "en_proceso"}
-- Respuesta esperada: Error - "Transición de estado no permitida: completado → en_proceso"


-- Pedido 2: completado → cancelado (INVÁLIDO)
-- No se puede cancelar un pedido ya completado
-- PATCH /api/pedidos/2/estado/
-- Body: {"estado": "cancelado"}
-- Respuesta esperada: Error - "Transición de estado no permitida: completado → cancelado"


-- =====================================
-- ESCENARIO 3: Cancelación de pedidos
-- =====================================

-- Pedido 3: pendiente → cancelado (VÁLIDO)
-- Se puede cancelar un pedido pendiente
-- PATCH /api/pedidos/3/estado/
-- Body: {"estado": "cancelado", "id_empleado": 2}


-- =====================================
-- ESCENARIO 4: Estado inválido
-- =====================================

-- Intentar establecer un estado no existente (debe fallar):
-- PATCH /api/pedidos/3/estado/
-- Body: {"estado": "entregado"}
-- Respuesta esperada: Error - "Estado inválido. Estados permitidos: pendiente, en_proceso, completado, cancelado"


-- =====================================
-- ESCENARIO 5: Pedido no existente
-- =====================================

-- Intentar actualizar un pedido que no existe (debe fallar):
-- PATCH /api/pedidos/9999/estado/
-- Body: {"estado": "completado"}
-- Respuesta esperada: Error - "Pedido no encontrado"


-- =====================================
-- MATRIZ DE TRANSICIONES PERMITIDAS
-- =====================================
/*
┌─────────────┬──────────────────────────────────────────────────────────────┐
│ Estado      │ Transiciones Permitidas                                      │
├─────────────┼──────────────────────────────────────────────────────────────┤
│ pendiente   │ → en_proceso (empleado comienza a preparar)                 │
│             │ → cancelado (cliente cancela antes de preparación)           │
├─────────────┼──────────────────────────────────────────────────────────────┤
│ en_proceso  │ → completado (pedido entregado)                              │
│             │ → cancelado (problema durante preparación)                   │
├─────────────┼──────────────────────────────────────────────────────────────┤
│ completado  │ (NINGUNA - Estado final exitoso)                            │
├─────────────┼──────────────────────────────────────────────────────────────┤
│ cancelado   │ (NINGUNA - Estado final de cancelación)                     │
└─────────────┴──────────────────────────────────────────────────────────────┘
*/


-- =====================================
-- CONSULTAS ÚTILES PARA TESTING
-- =====================================

-- Ver todos los pedidos por estado
SELECT 
    estado,
    COUNT(*) as cantidad,
    SUM(total) as total_ventas
FROM pedido
GROUP BY estado
ORDER BY estado;

-- Ver historial de un cliente con estados
SELECT 
    p.id_pedido,
    p.fecha,
    p.estado,
    p.total,
    COUNT(dp.id_detalle_pedido) as cantidad_items
FROM pedido p
LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
WHERE p.id_cliente = 1  -- Cambiar por ID de cliente a consultar
GROUP BY p.id_pedido, p.fecha, p.estado, p.total
ORDER BY p.fecha DESC;

-- Ver pedidos pendientes (cola de trabajo)
SELECT 
    p.id_pedido,
    u.nombre as cliente,
    s.nombre as sede,
    p.fecha,
    p.total,
    COUNT(dp.id_detalle_pedido) as items
FROM pedido p
JOIN cliente c ON p.id_cliente = c.id_cliente
JOIN usuario u ON c.id_usuario = u.id_usuario
JOIN sede s ON p.id_sede = s.id_sede
LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
WHERE p.estado = 'pendiente'
GROUP BY p.id_pedido, u.nombre, s.nombre, p.fecha, p.total
ORDER BY p.fecha;

-- Ver pedidos en proceso
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


-- =====================================
-- EJEMPLOS DE LLAMADAS AL API
-- =====================================

/*
# 1. Listar todos los pedidos pendientes
GET http://localhost:8000/api/pedidos/estado/pendiente/

# 2. Actualizar pedido pendiente a en_proceso
PATCH http://localhost:8000/api/pedidos/3/estado/
Content-Type: application/json
{
    "estado": "en_proceso",
    "id_empleado": 1
}

# 3. Completar un pedido en proceso
PATCH http://localhost:8000/api/pedidos/4/estado/
Content-Type: application/json
{
    "estado": "completado",
    "id_empleado": 1
}

# 4. Cancelar un pedido pendiente
PATCH http://localhost:8000/api/pedidos/3/estado/
Content-Type: application/json
{
    "estado": "cancelado",
    "id_empleado": 2
}

# 5. Intentar transición inválida (debe fallar)
PATCH http://localhost:8000/api/pedidos/1/estado/
Content-Type: application/json
{
    "estado": "en_proceso"
}
# Respuesta esperada: 400 Bad Request
# "Transición de estado no permitida: completado → en_proceso"

# 6. Ver detalle de un pedido
GET http://localhost:8000/api/pedidos/3/

# 7. Ver historial de cliente con filtro de estado
GET http://localhost:8000/api/pedidos/cliente/1/historial/?estado=completado
*/


-- =====================================
-- ✅ CHECKLIST DE PRUEBAS HU20
-- =====================================
/*
□ Transición pendiente → en_proceso (exitosa)
□ Transición en_proceso → completado (exitosa)
□ Transición pendiente → cancelado (exitosa)
□ Transición en_proceso → cancelado (exitosa)
□ Transición completado → cualquier estado (rechazada)
□ Transición cancelado → cualquier estado (rechazada)
□ Estado inválido "entregado" (rechazado)
□ Pedido no existente (rechazado)
□ Campo estado faltante en body (rechazado)
□ Listar pedidos por estado funciona correctamente
*/
