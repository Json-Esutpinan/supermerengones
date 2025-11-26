-- 1. Crear usuario de prueba
INSERT INTO usuario (nombre, email, password, rol, activo)
VALUES 
    ('Juan Pérez', 'juan.perez@example.com', 'password123', 'cliente', true),
    ('María García', 'maria.garcia@example.com', 'password123', 'cliente', true),
    ('Carlos López', 'carlos.lopez@example.com', 'password123', 'cliente', true)
ON CONFLICT (email) DO NOTHING;

-- 2. Crear clientes (usa los IDs de usuario creados)
INSERT INTO cliente (id_usuario, telefono, direccion)
SELECT 
    u.id_usuario,
    CASE u.nombre
        WHEN 'Juan Pérez' THEN '3001234567'
        WHEN 'María García' THEN '3009876543'
        WHEN 'Carlos López' THEN '3007654321'
    END as telefono,
    CASE u.nombre
        WHEN 'Juan Pérez' THEN 'Calle 10 #20-30'
        WHEN 'María García' THEN 'Carrera 15 #40-50'
        WHEN 'Carlos López' THEN 'Avenida 5 #60-70'
    END as direccion
FROM usuario u
WHERE u.rol = 'cliente'
ON CONFLICT (id_usuario) DO NOTHING;

-- 3. Crear unidad de medida si no existe
INSERT INTO unidad_medida (nombre, tipo, abreviatura, activo)
VALUES ('Unidad', 'cantidad', 'und', true)
ON CONFLICT (nombre) DO NOTHING;

-- 4. Crear productos de prueba
INSERT INTO producto (codigo, nombre, descripcion, id_unidad, contenido, precio, stock, activo)
VALUES 
    ('PROD-001', 'Merengón Grande', 'Merengón de 500g con fresas', 
     (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 
     500, 12000, 50, true),
    ('PROD-002', 'Merengón Especial', 'Merengón de 750g con frutas mixtas', 
     (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 
     750, 15000, 30, true),
    ('PROD-003', 'Merengón Premium', 'Merengón de 1kg con chocolate', 
     (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 
     1000, 20000, 20, true),
    ('PROD-004', 'Merengón Mini', 'Merengón de 250g', 
     (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 
     250, 8000, 100, true)
ON CONFLICT (codigo) DO NOTHING;

-- 5. Crear pedidos de prueba (para el primer cliente)
INSERT INTO pedido (id_cliente, id_sede, fecha, estado, total)
SELECT 
    c.id_cliente,
    (SELECT MIN(id_sede) FROM sede LIMIT 1) as id_sede,
    TIMESTAMP '2025-11-20 14:30:00' as fecha,
    'completado' as estado,
    24000 as total
FROM cliente c
JOIN usuario u ON c.id_usuario = u.id_usuario
WHERE u.email = 'juan.perez@example.com'
LIMIT 1;

INSERT INTO pedido (id_cliente, id_sede, fecha, estado, total)
SELECT 
    c.id_cliente,
    (SELECT MIN(id_sede) FROM sede LIMIT 1) as id_sede,
    TIMESTAMP '2025-11-21 10:15:00' as fecha,
    'completado' as estado,
    35000 as total
FROM cliente c
JOIN usuario u ON c.id_usuario = u.id_usuario
WHERE u.email = 'juan.perez@example.com'
LIMIT 1;

INSERT INTO pedido (id_cliente, id_sede, fecha, estado, total)
SELECT 
    c.id_cliente,
    (SELECT MIN(id_sede) FROM sede LIMIT 1) as id_sede,
    TIMESTAMP '2025-11-24 16:45:00' as fecha,
    'pendiente' as estado,
    16000 as total
FROM cliente c
JOIN usuario u ON c.id_usuario = u.id_usuario
WHERE u.email = 'juan.perez@example.com'
LIMIT 1;

INSERT INTO pedido (id_cliente, id_sede, fecha, estado, total)
SELECT 
    c.id_cliente,
    (SELECT MIN(id_sede) FROM sede LIMIT 1) as id_sede,
    TIMESTAMP '2025-11-25 09:00:00' as fecha,
    'en_proceso' as estado,
    40000 as total
FROM cliente c
JOIN usuario u ON c.id_usuario = u.id_usuario
WHERE u.email = 'juan.perez@example.com'
LIMIT 1;

-- 6. Crear detalles para el pedido 1 (2 Merengón Grande)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 0) as id_pedido,
    p.id_producto,
    2 as cantidad,
    12000 as precio_unitario,
    24000 as subtotal
FROM producto p
WHERE p.codigo = 'PROD-001'
LIMIT 1;

-- 7. Crear detalles para el pedido 2 (1 Merengón Premium + 1 Merengón Especial)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 1) as id_pedido,
    p.id_producto,
    1 as cantidad,
    20000 as precio_unitario,
    20000 as subtotal
FROM producto p
WHERE p.codigo = 'PROD-003'
LIMIT 1;

INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 1) as id_pedido,
    p.id_producto,
    1 as cantidad,
    15000 as precio_unitario,
    15000 as subtotal
FROM producto p
WHERE p.codigo = 'PROD-002'
LIMIT 1;

-- 8. Crear detalles para el pedido 3 (2 Merengón Mini)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 2) as id_pedido,
    p.id_producto,
    2 as cantidad,
    8000 as precio_unitario,
    16000 as subtotal
FROM producto p
WHERE p.codigo = 'PROD-004'
LIMIT 1;

-- 9. Crear detalles para el pedido 4 (2 Merengón Premium)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 3) as id_pedido,
    p.id_producto,
    2 as cantidad,
    20000 as precio_unitario,
    40000 as subtotal
FROM producto p
WHERE p.codigo = 'PROD-003'
LIMIT 1;

-- 10. Verificar datos insertados
SELECT 'Clientes creados:' as info, COUNT(*) as total FROM cliente
UNION ALL
SELECT 'Productos creados:', COUNT(*) FROM producto
UNION ALL
SELECT 'Pedidos creados:', COUNT(*) FROM pedido
UNION ALL
SELECT 'Detalles creados:', COUNT(*) FROM detalle_pedido;

-- 11. Ver resumen de pedidos
SELECT 
    p.id_pedido,
    u.nombre as cliente,
    p.fecha,
    p.estado,
    p.total,
    COUNT(dp.id_detalle) as cantidad_items
FROM pedido p
JOIN cliente c ON p.id_cliente = c.id_cliente
JOIN usuario u ON c.id_usuario = u.id_usuario
LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
GROUP BY p.id_pedido, u.nombre, p.fecha, p.estado, p.total
ORDER BY p.fecha DESC;
