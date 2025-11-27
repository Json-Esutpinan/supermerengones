-- =====================================
-- DATOS DE PRUEBA PARA HU19 - RECLAMOS
-- =====================================
-- Este script crea datos de prueba para probar la funcionalidad de reclamos
-- Asume que ya existe la tabla reclamo y los pedidos de datos_prueba_pedidos.sql

-- IMPORTANTE: Primero debes ejecutar datos_prueba_pedidos.sql para tener:
-- - Cliente Juan Pérez (id: 1)
-- - Pedidos 2, 3, 4, 5

-- =====================================
-- RECLAMOS DE PRUEBA 
-- =====================================

-- Reclamo 1: Reclamo sobre pedido completado (ID 2)
INSERT INTO reclamo (id_pedido, id_cliente, descripcion, estado, fecha, fecha_resolucion)
VALUES (
    2, 
    1, 
    'El producto Torta de Chocolate llegó con una esquina dañada. La caja estaba en mal estado y la decoración se corrió.',
    'abierto',
    '2025-11-21T10:30:00',
    NULL
)
ON CONFLICT (id_reclamo) DO NOTHING;

-- Reclamo 2: Reclamo resuelto sobre pedido completado (ID 3)
INSERT INTO reclamo (id_pedido, id_cliente, descripcion, estado, fecha, fecha_resolucion)
VALUES (
    3,
    1,
    'Ordené 2 Cupcakes de Vainilla pero solo me llegó 1. Falta una unidad en mi pedido.',
    'resuelto',
    '2025-11-23T14:15:00',
    '2025-11-24T09:00:00'
)
ON CONFLICT (id_reclamo) DO NOTHING;

-- Reclamo 3: Reclamo en revisión sobre pedido en proceso (ID 4)
INSERT INTO reclamo (id_pedido, id_cliente, descripcion, estado, fecha, fecha_resolucion)
VALUES (
    4,
    1,
    'El Pie de Limón tiene un sabor diferente al que probé en la tienda. No cumple con mis expectativas de calidad.',
    'en_revision',
    '2025-11-24T16:45:00',
    NULL
)
ON CONFLICT (id_reclamo) DO NOTHING;

-- Reclamo 4: Reclamo cerrado sobre pedido completado (ID 5)
INSERT INTO reclamo (id_pedido, id_cliente, descripcion, estado, fecha, fecha_resolucion)
VALUES (
    5,
    1,
    'Las Galletas de Chocolate llegaron rotas. La mitad de las galletas estaban en pedazos dentro de la bolsa.',
    'cerrado',
    '2025-11-25T11:20:00',
    '2025-11-26T15:30:00'
)
ON CONFLICT (id_reclamo) DO NOTHING;

-- Reclamo 5: Otro reclamo abierto para tener variedad
INSERT INTO reclamo (id_pedido, id_cliente, descripcion, estado, fecha, fecha_resolucion)
VALUES (
    2,
    1,
    'Tardaron más de lo prometido en entregar mi pedido. Me dijeron 2 horas pero llegó después de 4 horas.',
    'abierto',
    '2025-11-21T18:00:00',
    NULL
)
ON CONFLICT (id_reclamo) DO NOTHING;

-- =====================================
-- VERIFICACIÓN
-- =====================================
-- Descomentar para verificar que se crearon correctamente:

-- SELECT r.id_reclamo, r.id_pedido, p.estado as estado_pedido, r.estado as estado_reclamo, 
--        r.descripcion, r.fecha, r.fecha_resolucion
-- FROM reclamo r
-- JOIN pedido p ON r.id_pedido = p.id_pedido
-- WHERE r.id_cliente = 1
-- ORDER BY r.fecha DESC;

-- =====================================
-- RESUMEN DE DATOS CREADOS
-- =====================================
-- 5 reclamos para el cliente Juan Pérez (id: 1)
-- 
-- Distribución por estado:
-- - 2 reclamos abiertos (ids: 1, 5)
-- - 1 reclamo en_revision (id: 3)
-- - 1 reclamo resuelto (id: 2)
-- - 1 reclamo cerrado (id: 4)
--
-- Distribución por pedido:
-- - Pedido 2: 2 reclamos (1 abierto, 1 abierto de demora)
-- - Pedido 3: 1 reclamo (resuelto)
-- - Pedido 4: 1 reclamo (en_revision)
-- - Pedido 5: 1 reclamo (cerrado)
--
-- Esto permite probar:
-- - Listar reclamos por cliente
-- - Listar reclamos por pedido
-- - Filtrar por estado
-- - Ver detalles de reclamo individual
-- - Cambiar estados
-- - Agregar respuestas
