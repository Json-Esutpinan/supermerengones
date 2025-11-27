-- =====================================
-- SCRIPT: DATOS DE PRUEBA COMPLETOS
-- =====================================
-- Este script inserta datos de prueba en todas las tablas del sistema
-- Ejecutar DESPUÉS de crear todas las tablas con modelo.sql

-- =====================================
-- 1. SEDES
-- =====================================
INSERT INTO sede (nombre, direccion, telefono, activo) VALUES
('Sede Centro', 'Calle 10 #15-20, Centro', '3001234567', true),
('Sede Norte', 'Carrera 45 #80-15, Chapinero', '3009876543', true),
('Sede Sur', 'Avenida 68 #20-30, Kennedy', '3007654321', true)
ON CONFLICT DO NOTHING;

-- =====================================
-- 2. PROVEEDORES
-- =====================================
INSERT INTO proveedor (nombre, telefono, email, direccion, activo) VALUES
('Distribuidora Frutas Frescas', '3101234567', 'ventas@frutasfrescas.com', 'Calle 25 #10-15', true),
('Lácteos La Vaca Feliz', '3109876543', 'pedidos@lavacafeliz.com', 'Carrera 30 #50-40', true),
('Chocolates Premium SAS', '3107654321', 'info@chocolatespremium.com', 'Avenida 15 #60-20', true)
ON CONFLICT DO NOTHING;

-- =====================================
-- 3. UNIDADES DE MEDIDA
-- =====================================
INSERT INTO unidad_medida (nombre, tipo, abreviatura, activo) VALUES
('Unidad', 'cantidad', 'und', true),
('Gramo', 'peso', 'g', true),
('Kilogramo', 'peso', 'kg', true),
('Litro', 'volumen', 'L', true),
('Mililitro', 'volumen', 'ml', true)
ON CONFLICT (nombre) DO NOTHING;

-- =====================================
-- 4. USUARIOS
-- =====================================
INSERT INTO usuario (nombre, email, password, rol, activo) VALUES
-- Clientes
('Juan Pérez', 'juan.perez@example.com', 'hashed_password_123', 'cliente', true),
('María García', 'maria.garcia@example.com', 'hashed_password_456', 'cliente', true),
('Carlos López', 'carlos.lopez@example.com', 'hashed_password_789', 'cliente', true),
-- Empleados
('Ana Rodríguez', 'ana.rodriguez@supermerengones.com', 'hashed_password_emp1', 'empleado', true),
('Luis Martínez', 'luis.martinez@supermerengones.com', 'hashed_password_emp2', 'empleado', true),
-- Administrador
('Admin Principal', 'admin@supermerengones.com', 'hashed_password_admin', 'administrador', true)
ON CONFLICT (email) DO NOTHING;

-- =====================================
-- 5. CLIENTES
-- =====================================
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

-- =====================================
-- 6. EMPLEADOS
-- =====================================
INSERT INTO empleado (id_usuario, id_sede, cargo, fecha_ingreso)
SELECT 
    u.id_usuario,
    (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1) as id_sede,
    CASE u.nombre
        WHEN 'Ana Rodríguez' THEN 'Cajera'
        WHEN 'Luis Martínez' THEN 'Pastelero'
    END as cargo,
    CASE u.nombre
        WHEN 'Ana Rodríguez' THEN '2024-01-15'
        WHEN 'Luis Martínez' THEN '2024-03-01'
    END::date as fecha_ingreso
FROM usuario u
WHERE u.rol = 'empleado'
ON CONFLICT (id_usuario) DO NOTHING;

-- =====================================
-- 7. ADMINISTRADORES
-- =====================================
INSERT INTO administrador (id_usuario, nivel_acceso)
SELECT 
    u.id_usuario,
    'super' as nivel_acceso
FROM usuario u
WHERE u.rol = 'administrador'
ON CONFLICT (id_usuario) DO NOTHING;

-- =====================================
-- 8. PRODUCTOS
-- =====================================
INSERT INTO producto (codigo, nombre, descripcion, id_unidad, contenido, precio, stock, activo) VALUES
('PROD-001', 'Merengón Grande de Fresa', 'Merengón de 500g con fresas frescas y crema', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 500, 12000, 50, true),
('PROD-002', 'Merengón Especial Frutas', 'Merengón de 750g con frutas mixtas', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 750, 15000, 30, true),
('PROD-003', 'Merengón Premium Chocolate', 'Merengón de 1kg con chocolate belga', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 1000, 20000, 20, true),
('PROD-004', 'Merengón Mini', 'Merengón individual de 250g', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 250, 8000, 100, true),
('PROD-005', 'Torta de Chocolate', 'Torta de chocolate de 1kg', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1), 1000, 35000, 15, true)
ON CONFLICT (codigo) DO NOTHING;

-- =====================================
-- 9. INSUMOS
-- =====================================
INSERT INTO insumo (codigo, nombre, descripcion, id_unidad, id_sede, stock_minimo, activo) VALUES
('INS-001', 'Fresas Frescas', 'Fresas de primera calidad', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Kilogramo' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1), 5, true),
('INS-002', 'Crema de Leche', 'Crema de leche entera', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Litro' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1), 10, true),
('INS-003', 'Chocolate Belga', 'Chocolate para repostería premium', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Kilogramo' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1), 3, true),
('INS-004', 'Azúcar Refinada', 'Azúcar blanca refinada', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Kilogramo' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1), 20, true),
('INS-005', 'Huevos', 'Huevos frescos AA', 
 (SELECT id_unidad FROM unidad_medida WHERE nombre = 'Unidad' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1), 100, true)
ON CONFLICT (codigo) DO NOTHING;

-- =====================================
-- 10. INVENTARIO
-- =====================================
INSERT INTO inventario (id_insumo, cantidad, updated_at)
SELECT i.id_insumo, 
    CASE i.codigo
        WHEN 'INS-001' THEN 25.00  -- Fresas 25kg
        WHEN 'INS-002' THEN 50.00  -- Crema 50L
        WHEN 'INS-003' THEN 15.00  -- Chocolate 15kg
        WHEN 'INS-004' THEN 100.00 -- Azúcar 100kg
        WHEN 'INS-005' THEN 500.00 -- Huevos 500 unidades
    END as cantidad,
    NOW() as updated_at
FROM insumo i
ON CONFLICT (id_insumo) DO NOTHING;

-- =====================================
-- 11. PRODUCTO_INSUMO (Recetas)
-- =====================================
-- Merengón Grande de Fresa necesita:
INSERT INTO producto_insumo (id_producto, id_insumo, cantidad_necesaria)
SELECT 
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-001' LIMIT 1),
    (SELECT id_insumo FROM insumo WHERE codigo = 'INS-001' LIMIT 1),
    0.3  -- 300g de fresas
UNION ALL SELECT
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-001' LIMIT 1),
    (SELECT id_insumo FROM insumo WHERE codigo = 'INS-002' LIMIT 1),
    0.2  -- 200ml de crema
ON CONFLICT DO NOTHING;

-- Merengón Premium Chocolate necesita:
INSERT INTO producto_insumo (id_producto, id_insumo, cantidad_necesaria)
SELECT 
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-003' LIMIT 1),
    (SELECT id_insumo FROM insumo WHERE codigo = 'INS-003' LIMIT 1),
    0.4  -- 400g de chocolate
UNION ALL SELECT
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-003' LIMIT 1),
    (SELECT id_insumo FROM insumo WHERE codigo = 'INS-002' LIMIT 1),
    0.3  -- 300ml de crema
ON CONFLICT DO NOTHING;

-- =====================================
-- 12. PEDIDOS
-- =====================================
INSERT INTO pedido (id_cliente, id_sede, fecha, estado, total) VALUES
-- Pedidos de Juan Pérez
((SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'juan.perez@example.com' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1),
 TIMESTAMP '2025-11-20 14:30:00', 'completado', 24000),
((SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'juan.perez@example.com' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1),
 TIMESTAMP '2025-11-21 10:15:00', 'completado', 35000),
((SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'juan.perez@example.com' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1),
 TIMESTAMP '2025-11-24 16:45:00', 'pendiente', 16000),
((SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'juan.perez@example.com' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Centro' LIMIT 1),
 TIMESTAMP '2025-11-25 09:00:00', 'en_proceso', 40000),
-- Pedido de María García
((SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'maria.garcia@example.com' LIMIT 1),
 (SELECT id_sede FROM sede WHERE nombre = 'Sede Norte' LIMIT 1),
 TIMESTAMP '2025-11-26 11:00:00', 'completado', 15000)
ON CONFLICT DO NOTHING;

-- =====================================
-- 13. DETALLE_PEDIDO
-- =====================================
-- Detalles del primer pedido (2 Merengón Grande)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 0),
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-001' LIMIT 1),
    2, 12000, 24000
ON CONFLICT DO NOTHING;

-- Detalles del segundo pedido (1 Premium + 1 Especial)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 1),
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-003' LIMIT 1),
    1, 20000, 20000
UNION ALL SELECT
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 1),
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-002' LIMIT 1),
    1, 15000, 15000
ON CONFLICT DO NOTHING;

-- Detalles del tercer pedido (2 Mini)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 2),
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-004' LIMIT 1),
    2, 8000, 16000
ON CONFLICT DO NOTHING;

-- Detalles del cuarto pedido (2 Premium)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 3),
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-003' LIMIT 1),
    2, 20000, 40000
ON CONFLICT DO NOTHING;

-- Detalles del quinto pedido (1 Especial)
INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 4),
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-002' LIMIT 1),
    1, 15000, 15000
ON CONFLICT DO NOTHING;

-- =====================================
-- 14. RECLAMOS
-- =====================================
INSERT INTO reclamo (id_pedido, id_cliente, descripcion, estado, fecha, fecha_resolucion) VALUES
((SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 0),
 (SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'juan.perez@example.com' LIMIT 1),
 'El producto llegó con una esquina dañada. La caja estaba en mal estado.',
 'abierto', TIMESTAMP '2025-11-21 10:30:00', NULL),
((SELECT id_pedido FROM pedido ORDER BY id_pedido LIMIT 1 OFFSET 1),
 (SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'juan.perez@example.com' LIMIT 1),
 'Falta una unidad en mi pedido.',
 'resuelto', TIMESTAMP '2025-11-23 14:15:00', TIMESTAMP '2025-11-24 09:00:00')
ON CONFLICT DO NOTHING;

-- =====================================
-- 15. COMPRAS A PROVEEDORES
-- =====================================
INSERT INTO compra (id_proveedor, id_usuario, fecha, total, estado) VALUES
((SELECT id_proveedor FROM proveedor WHERE nombre = 'Distribuidora Frutas Frescas' LIMIT 1),
 (SELECT id_usuario FROM usuario WHERE rol = 'administrador' LIMIT 1),
 DATE '2025-11-15', 250000, 'completado'),
((SELECT id_proveedor FROM proveedor WHERE nombre = 'Lácteos La Vaca Feliz' LIMIT 1),
 (SELECT id_usuario FROM usuario WHERE rol = 'administrador' LIMIT 1),
 DATE '2025-11-18', 180000, 'completado')
ON CONFLICT DO NOTHING;

-- =====================================
-- 16. DETALLE_COMPRA
-- =====================================
INSERT INTO detalle_compra (id_compra, id_insumo, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_compra FROM compra ORDER BY id_compra LIMIT 1 OFFSET 0),
    (SELECT id_insumo FROM insumo WHERE codigo = 'INS-001' LIMIT 1),
    50, 5000, 250000
ON CONFLICT DO NOTHING;

INSERT INTO detalle_compra (id_compra, id_insumo, cantidad, precio_unitario, subtotal)
SELECT 
    (SELECT id_compra FROM compra ORDER BY id_compra LIMIT 1 OFFSET 1),
    (SELECT id_insumo FROM insumo WHERE codigo = 'INS-002' LIMIT 1),
    60, 3000, 180000
ON CONFLICT DO NOTHING;

-- =====================================
-- 17. PROMOCIONES
-- =====================================
INSERT INTO promocion (titulo, descripcion, descripcion_corta, tipo, valor, fecha_inicio, fecha_fin, activo) VALUES
('20% en Merengones Fresa', 
 'Descuento especial del 20% en todos nuestros Merengones de Fresa.',
 '20% de descuento en Merengones Fresa',
 'descuento_porcentaje', 20.00, NOW(), NOW() + INTERVAL '1 month', true),
('Compra 2 lleva 1 gratis',
 'Promoción de combo: compra dos Merengones y lleva uno gratis.',
 '2x1 en productos seleccionados',
 'combo', 0.00, NOW(), NOW() + INTERVAL '2 weeks', true),
('$5.000 OFF en pedidos grandes',
 'Descuento de $5.000 en pedidos mayores a $30.000',
 '-$5.000 en pedidos grandes',
 'descuento_monto', 5000.00, NOW(), NOW() + INTERVAL '1 month', true)
ON CONFLICT DO NOTHING;

-- =====================================
-- 18. PROMOCION_PRODUCTO
-- =====================================
INSERT INTO promocion_producto (id_promocion, id_producto)
SELECT 
    (SELECT id_promocion FROM promocion WHERE titulo = '20% en Merengones Fresa' LIMIT 1),
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-001' LIMIT 1)
UNION ALL SELECT
    (SELECT id_promocion FROM promocion WHERE titulo = 'Compra 2 lleva 1 gratis' LIMIT 1),
    (SELECT id_producto FROM producto WHERE codigo = 'PROD-003' LIMIT 1)
UNION ALL SELECT
    (SELECT id_promocion FROM promocion WHERE titulo = '$5.000 OFF en pedidos grandes' LIMIT 1),
    (SELECT id_producto FROM producto WHERE codigo IN ('PROD-001', 'PROD-002', 'PROD-003') LIMIT 1)
ON CONFLICT DO NOTHING;

-- =====================================
-- 19. NOTIFICACIONES
-- =====================================
INSERT INTO notificacion (id_cliente, mensaje, fecha, leida) VALUES
((SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'juan.perez@example.com' LIMIT 1),
 'Tu pedido #1 ha sido entregado exitosamente', TIMESTAMP '2025-11-20 16:00:00', true),
((SELECT id_cliente FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario WHERE u.email = 'juan.perez@example.com' LIMIT 1),
 'Nuevo descuento del 20% en Merengones de Fresa', TIMESTAMP '2025-11-27 09:00:00', false)
ON CONFLICT DO NOTHING;

-- =====================================
-- 20. TURNOS
-- =====================================
INSERT INTO turno (id_empleado, fecha, hora_inicio, hora_fin)
SELECT 
    (SELECT id_empleado FROM empleado e JOIN usuario u ON e.id_usuario = u.id_usuario WHERE u.nombre = 'Ana Rodríguez' LIMIT 1),
    DATE '2025-11-27', TIME '08:00:00', TIME '16:00:00'
UNION ALL SELECT
    (SELECT id_empleado FROM empleado e JOIN usuario u ON e.id_usuario = u.id_usuario WHERE u.nombre = 'Luis Martínez' LIMIT 1),
    DATE '2025-11-27', TIME '14:00:00', TIME '22:00:00'
ON CONFLICT DO NOTHING;

-- =====================================
-- VERIFICACIÓN FINAL
-- =====================================
SELECT 'RESUMEN DE DATOS INSERTADOS' as titulo;

SELECT 'Sedes' as tabla, COUNT(*) as total FROM sede
UNION ALL SELECT 'Proveedores', COUNT(*) FROM proveedor
UNION ALL SELECT 'Unidades de Medida', COUNT(*) FROM unidad_medida
UNION ALL SELECT 'Usuarios', COUNT(*) FROM usuario
UNION ALL SELECT 'Clientes', COUNT(*) FROM cliente
UNION ALL SELECT 'Empleados', COUNT(*) FROM empleado
UNION ALL SELECT 'Administradores', COUNT(*) FROM administrador
UNION ALL SELECT 'Productos', COUNT(*) FROM producto
UNION ALL SELECT 'Insumos', COUNT(*) FROM insumo
UNION ALL SELECT 'Inventarios', COUNT(*) FROM inventario
UNION ALL SELECT 'Recetas (Producto-Insumo)', COUNT(*) FROM producto_insumo
UNION ALL SELECT 'Pedidos', COUNT(*) FROM pedido
UNION ALL SELECT 'Detalles de Pedidos', COUNT(*) FROM detalle_pedido
UNION ALL SELECT 'Reclamos', COUNT(*) FROM reclamo
UNION ALL SELECT 'Compras', COUNT(*) FROM compra
UNION ALL SELECT 'Detalles de Compras', COUNT(*) FROM detalle_compra
UNION ALL SELECT 'Promociones', COUNT(*) FROM promocion
UNION ALL SELECT 'Promoción-Producto', COUNT(*) FROM promocion_producto
UNION ALL SELECT 'Notificaciones', COUNT(*) FROM notificacion
UNION ALL SELECT 'Turnos', COUNT(*) FROM turno
ORDER BY tabla;

SELECT '✅ Datos de prueba insertados exitosamente' as resultado;
