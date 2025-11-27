-- Script SQL para crear tablas de promociones en Supabase
-- Ejecutar este script en la consola SQL de Supabase

-- Tabla de promociones
CREATE TABLE IF NOT EXISTS promocion (
    id_promocion SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    descripcion_corta VARCHAR(500),
    tipo VARCHAR(50) NOT NULL, -- 'descuento_porcentaje', 'descuento_monto', 'combo'
    valor DECIMAL(10, 2) NOT NULL,
    imagen_url VARCHAR(500),
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de relación: promoción - producto (una promoción puede aplicar a varios productos)
CREATE TABLE IF NOT EXISTS promocion_producto (
    id_promocion_producto SERIAL PRIMARY KEY,
    id_promocion INTEGER NOT NULL REFERENCES promocion(id_promocion) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_promocion, id_producto)
);

-- Índices para optimizar queries
CREATE INDEX IF NOT EXISTS idx_promocion_activo ON promocion(activo);
CREATE INDEX IF NOT EXISTS idx_promocion_fecha ON promocion(fecha_inicio, fecha_fin);
CREATE INDEX IF NOT EXISTS idx_promocion_producto_promo ON promocion_producto(id_promocion);
CREATE INDEX IF NOT EXISTS idx_promocion_producto_prod ON promocion_producto(id_producto);

-- Datos de ejemplo
INSERT INTO promocion (titulo, descripcion, descripcion_corta, tipo, valor, imagen_url, fecha_inicio, fecha_fin, activo) VALUES
(
    '20% en Merengones Fresa',
    'Descuento especial del 20% en todos nuestros Merengones de Fresa. Válido solo este mes.',
    '20% de descuento en Merengones Fresa',
    'descuento_porcentaje',
    20,
    NULL,
    NOW(),
    NOW() + INTERVAL '1 month',
    TRUE
),
(
    'Compra 2 lleva 1 gratis',
    'Promoción de combo: compra dos Merengones y lleva uno adicional completamente gratis.',
    '2x1 en productos seleccionados',
    'descuento_monto',
    0,
    NULL,
    NOW(),
    NOW() + INTERVAL '2 weeks',
    TRUE
),
(
    'Descuento de $5.000 en pedidos mayores a $30.000',
    'Si tu pedido supera los $30.000, automáticamente se descuentan $5.000.',
    '-$5.000 en pedidos grandes',
    'descuento_monto',
    5000,
    NULL,
    NOW(),
    NOW() + INTERVAL '1 month',
    TRUE
);


INSERT INTO promocion_producto (id_promocion, id_producto) VALUES
(1, 1),  -- Promo 1 (20% Fresa) aplica a Merengón Grande
(1, 2),  -- Promo 1 (20% Fresa) aplica a Merengón Especial
(2, 3),  -- Promo 2 (2x1) aplica a Merengón Premium
(3, 1), (3, 2), (3, 3), (3, 4);  -- Promo 3 ($5000 desc) aplica a todos

-- Consultas útiles para verificar:
-- SELECT * FROM promocion WHERE activo = TRUE;
-- SELECT p.*, pp.id_producto FROM promocion p LEFT JOIN promocion_producto pp ON p.id_promocion = pp.id_promocion;
