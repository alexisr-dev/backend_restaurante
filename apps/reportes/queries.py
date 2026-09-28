from django.db import connection


def _filas(sql: str, params: list | None = None) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columnas = [col[0] for col in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]


def ventas_diarias(dias: int) -> list[dict]:
    return _filas(
        """
        SELECT dia, num_pedidos, total_vendido
        FROM vw_ventas_diarias
        WHERE dia >= current_date - %s::int
        ORDER BY dia
        """,
        [dias],
    )


def productos_mas_vendidos(limite: int) -> list[dict]:
    return _filas(
        """
        SELECT id, nombre, unidades_vendidas, ingresos
        FROM vw_productos_mas_vendidos
        LIMIT %s
        """,
        [limite],
    )


def insumos_stock_bajo() -> list[dict]:
    return _filas(
        """
        SELECT id, nombre, stock_actual, stock_minimo
        FROM vw_insumos_stock_bajo
        ORDER BY stock_actual - stock_minimo
        """
    )


def consumo_insumos(limite: int) -> list[dict]:
    return _filas(
        """
        SELECT id, nombre, total_consumido
        FROM vw_consumo_insumos
        WHERE total_consumido IS NOT NULL
        LIMIT %s
        """,
        [limite],
    )


def resumen_general() -> dict:
    filas = _filas(
        """
        SELECT
          (SELECT COALESCE(SUM(dp.subtotal), 0)
             FROM pedidos p
             JOIN detalle_pedido dp ON dp.pedido_id = p.id
            WHERE p.estado = 'entregado'
              AND p.created_at >= current_date)                       AS ventas_hoy,
          (SELECT COUNT(*) FROM pedidos
            WHERE created_at >= current_date)                          AS pedidos_hoy,
          (SELECT COUNT(*) FROM pedidos
            WHERE estado IN ('pendiente', 'preparando'))               AS pedidos_activos,
          (SELECT COUNT(*) FROM mesas WHERE estado = 'ocupada')        AS mesas_ocupadas,
          (SELECT COUNT(*) FROM mesas)                                 AS mesas_totales,
          (SELECT COUNT(*) FROM vw_insumos_stock_bajo)                 AS insumos_en_alerta,
          (SELECT COUNT(*) FROM alertas_inventario WHERE atendida = FALSE) AS alertas_pendientes,
          (SELECT COUNT(*) FROM productos WHERE activo = TRUE)         AS productos_activos
        """
    )
    return filas[0]


def ventas_por_categoria(dias: int) -> list[dict]:
    return _filas(
        """
        SELECT c.id, c.nombre,
               SUM(dp.subtotal)  AS ingresos,
               SUM(dp.cantidad)  AS unidades
        FROM detalle_pedido dp
        JOIN pedidos p     ON p.id = dp.pedido_id
        JOIN productos pr  ON pr.id = dp.producto_id
        JOIN categorias c  ON c.id = pr.categoria_id
        WHERE p.estado = 'entregado'
          AND p.created_at >= current_date - %s::int
        GROUP BY c.id, c.nombre
        ORDER BY ingresos DESC
        """,
        [dias],
    )


def historial_pedidos(limite: int, offset: int, estado: str | None) -> list[dict]:
    return _filas(
        """
        SELECT p.id, p.estado, p.total, p.created_at,
               m.numero  AS mesa_numero,
               u.nombre  AS mesero_nombre,
               COUNT(dp.id) AS lineas
        FROM pedidos p
        JOIN mesas m     ON m.id = p.mesa_id
        JOIN usuarios u  ON u.id = p.mesero_id
        LEFT JOIN detalle_pedido dp ON dp.pedido_id = p.id
        WHERE (%s::text IS NULL OR p.estado::text = %s::text)
        GROUP BY p.id, p.estado, p.total, p.created_at, m.numero, u.nombre
        ORDER BY p.created_at DESC
        LIMIT %s OFFSET %s
        """,
        [estado, estado, limite, offset],
    )
