-- =====================================================================
-- Sistema de Gestión para Restaurantes
-- Esquema de base de datos — PostgreSQL 15+
-- Fuente única de verdad del esquema: administrada vía migraciones
-- de Django (backend-django). FastAPI (backend-fastapi) lee/escribe
-- sobre las tablas operativas (mesas, pedidos, detalle_pedido,
-- movimientos_inventario) usando SQLAlchemy, sin generar migraciones.
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- gen_random_uuid()

-- =====================================================================
-- ENUMS
-- =====================================================================
CREATE TYPE rol_usuario        AS ENUM ('mesero', 'cocina', 'admin', 'inventario');
CREATE TYPE estado_mesa        AS ENUM ('libre', 'ocupada', 'reservada');
CREATE TYPE estado_pedido      AS ENUM ('pendiente', 'preparando', 'listo', 'entregado', 'cancelado');
CREATE TYPE estado_item_pedido AS ENUM ('pendiente', 'preparando', 'listo', 'entregado', 'cancelado');
CREATE TYPE tipo_movimiento    AS ENUM ('entrada', 'salida', 'ajuste');
CREATE TYPE motivo_movimiento  AS ENUM ('venta', 'compra', 'ajuste_manual', 'merma');
CREATE TYPE estado_compra      AS ENUM ('pendiente', 'recibida', 'cancelada');
CREATE TYPE metodo_pago        AS ENUM ('efectivo', 'yape', 'plin', 'tarjeta', 'mercado_pago');
CREATE TYPE estado_pago        AS ENUM ('pendiente', 'confirmado', 'rechazado');

-- =====================================================================
-- Función genérica para updated_at automático
-- =====================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- USUARIOS (autenticación y RBAC simple por rol)
-- =====================================================================
CREATE TABLE usuarios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(120) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    rol             rol_usuario NOT NULL,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_usuarios_rol ON usuarios(rol);

-- =====================================================================
-- MESAS
-- =====================================================================
CREATE TABLE mesas (
    id          SERIAL PRIMARY KEY,
    numero      INTEGER NOT NULL UNIQUE,
    capacidad   SMALLINT NOT NULL DEFAULT 4,
    estado      estado_mesa NOT NULL DEFAULT 'libre',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- CATEGORÍAS Y PRODUCTOS (menú vendible)
-- =====================================================================
CREATE TABLE categorias (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE productos (
    id           SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
    nombre       VARCHAR(120) NOT NULL,
    descripcion  TEXT,
    precio       NUMERIC(10,2) NOT NULL CHECK (precio >= 0),
    activo       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_productos_updated_at BEFORE UPDATE ON productos
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================
-- INSUMOS (materia prima) — el inventario real vive aquí, no en productos
-- =====================================================================
CREATE TABLE insumos (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(120) NOT NULL UNIQUE,
    unidad_medida   VARCHAR(20) NOT NULL,               -- kg, l, unidad...
    stock_actual    NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo    NUMERIC(12,3) NOT NULL DEFAULT 0,
    costo_unitario  NUMERIC(10,2) NOT NULL DEFAULT 0,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_insumos_updated_at BEFORE UPDATE ON insumos
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- índice parcial: acelera la consulta "qué insumos están en alerta"
CREATE INDEX idx_insumos_stock_bajo ON insumos(id) WHERE stock_actual <= stock_minimo;

-- Receta (BOM): cuánto insumo consume cada producto vendido.
-- Esto es lo que permite descontar inventario automáticamente y de forma realista.
CREATE TABLE receta_producto (
    id                  SERIAL PRIMARY KEY,
    producto_id         INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    insumo_id           INTEGER NOT NULL REFERENCES insumos(id) ON DELETE RESTRICT,
    cantidad_requerida  NUMERIC(12,3) NOT NULL CHECK (cantidad_requerida > 0),
    UNIQUE (producto_id, insumo_id)
);

-- =====================================================================
-- PEDIDOS
-- =====================================================================
CREATE TABLE pedidos (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mesa_id          INTEGER NOT NULL REFERENCES mesas(id),
    mesero_id        UUID NOT NULL REFERENCES usuarios(id),
    estado           estado_pedido NOT NULL DEFAULT 'pendiente',
    idempotency_key  UUID NOT NULL UNIQUE,   -- evita pedidos duplicados por doble clic
    total            NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_pedidos_updated_at BEFORE UPDATE ON pedidos
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_mesa ON pedidos(mesa_id);

CREATE TABLE detalle_pedido (
    id              SERIAL PRIMARY KEY,
    pedido_id       UUID NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id     INTEGER NOT NULL REFERENCES productos(id),
    cantidad        SMALLINT NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL,
    subtotal        NUMERIC(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    estado          estado_item_pedido NOT NULL DEFAULT 'pendiente',
    notas           TEXT
);
CREATE INDEX idx_detalle_pedido_pedido ON detalle_pedido(pedido_id);

-- =====================================================================
-- INVENTARIO: MOVIMIENTOS Y ALERTAS
-- =====================================================================
CREATE TABLE movimientos_inventario (
    id           BIGSERIAL PRIMARY KEY,
    insumo_id    INTEGER NOT NULL REFERENCES insumos(id),
    tipo         tipo_movimiento NOT NULL,
    motivo       motivo_movimiento NOT NULL,
    cantidad     NUMERIC(12,3) NOT NULL CHECK (cantidad > 0),
    referencia   VARCHAR(60),        -- ej: 'pedido:<uuid>' o 'compra:<id>'
    usuario_id   UUID REFERENCES usuarios(id),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_movimientos_insumo ON movimientos_inventario(insumo_id);

CREATE TABLE alertas_inventario (
    id          BIGSERIAL PRIMARY KEY,
    insumo_id   INTEGER NOT NULL REFERENCES insumos(id),
    mensaje     TEXT NOT NULL,
    atendida    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- PROVEEDORES Y COMPRAS
-- =====================================================================
CREATE TABLE proveedores (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(150) NOT NULL,
    contacto    VARCHAR(120),
    telefono    VARCHAR(30),
    email       VARCHAR(150),
    direccion   TEXT,
    activo      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE compras (
    id            SERIAL PRIMARY KEY,
    proveedor_id  INTEGER NOT NULL REFERENCES proveedores(id),
    usuario_id    UUID NOT NULL REFERENCES usuarios(id),
    estado        estado_compra NOT NULL DEFAULT 'pendiente',
    total         NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE detalle_compra (
    id              SERIAL PRIMARY KEY,
    compra_id       INTEGER NOT NULL REFERENCES compras(id) ON DELETE CASCADE,
    insumo_id       INTEGER NOT NULL REFERENCES insumos(id),
    cantidad        NUMERIC(12,3) NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL,
    subtotal        NUMERIC(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);

-- =====================================================================
-- PAGOS (opcional — simulación Yape / Mercado Pago sandbox)
-- =====================================================================
CREATE TABLE pagos (
    id                 BIGSERIAL PRIMARY KEY,
    pedido_id          UUID NOT NULL REFERENCES pedidos(id),
    metodo             metodo_pago NOT NULL,
    monto              NUMERIC(10,2) NOT NULL,
    estado             estado_pago NOT NULL DEFAULT 'pendiente',
    referencia_externa VARCHAR(120),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- AUDITORÍA / OBSERVABILIDAD
-- =====================================================================
CREATE TABLE logs_auditoria (
    id          BIGSERIAL PRIMARY KEY,
    usuario_id  UUID REFERENCES usuarios(id),
    accion      VARCHAR(60) NOT NULL,      -- CREATE, UPDATE, DELETE, STATE_CHANGE
    entidad     VARCHAR(60) NOT NULL,      -- pedido, producto, insumo...
    entidad_id  VARCHAR(60) NOT NULL,
    detalle     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_logs_entidad ON logs_auditoria(entidad, entidad_id);

-- =====================================================================
-- VISTAS PARA REPORTES (consumidas por backend-django / reportes)
-- =====================================================================
CREATE VIEW vw_ventas_diarias AS
SELECT date_trunc('day', p.created_at) AS dia,
       COUNT(DISTINCT p.id)            AS num_pedidos,
       SUM(dp.subtotal)                AS total_vendido
FROM pedidos p
JOIN detalle_pedido dp ON dp.pedido_id = p.id
WHERE p.estado = 'entregado'
GROUP BY 1
ORDER BY 1 DESC;

CREATE VIEW vw_productos_mas_vendidos AS
SELECT pr.id, pr.nombre,
       SUM(dp.cantidad)  AS unidades_vendidas,
       SUM(dp.subtotal)  AS ingresos
FROM detalle_pedido dp
JOIN productos pr ON pr.id = dp.producto_id
JOIN pedidos p ON p.id = dp.pedido_id
WHERE p.estado = 'entregado'
GROUP BY pr.id, pr.nombre
ORDER BY unidades_vendidas DESC;

CREATE VIEW vw_insumos_stock_bajo AS
SELECT id, nombre, stock_actual, stock_minimo
FROM insumos
WHERE stock_actual <= stock_minimo AND activo = TRUE;

CREATE VIEW vw_consumo_insumos AS
SELECT i.id, i.nombre,
       SUM(mi.cantidad) FILTER (WHERE mi.tipo = 'salida') AS total_consumido
FROM movimientos_inventario mi
JOIN insumos i ON i.id = mi.insumo_id
GROUP BY i.id, i.nombre
ORDER BY total_consumido DESC NULLS LAST;
