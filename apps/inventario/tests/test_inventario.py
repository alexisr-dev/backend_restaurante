from decimal import Decimal

from django.test import TestCase

from apps.inventario.models import AlertaInventario, MotivoMovimiento, TipoMovimiento
from apps.inventario.services import registrar_movimiento
from apps.usuarios.models import RolUsuario
from apps.usuarios.tests.factories import autenticar, crear_insumo, crear_usuario
from core.exceptions import ReglaNegocioError


class MovimientosTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario(RolUsuario.INVENTARIO, "inv@test.com")
        self.insumo = crear_insumo("Arroz", stock="10.000", minimo="3.000")

    def test_entrada_incrementa_stock(self):
        registrar_movimiento(
            insumo_id=self.insumo.id,
            tipo=TipoMovimiento.ENTRADA,
            motivo=MotivoMovimiento.COMPRA,
            cantidad=Decimal("5.000"),
            usuario=self.usuario,
        )
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("15.000"))

    def test_salida_reduce_stock(self):
        registrar_movimiento(
            insumo_id=self.insumo.id,
            tipo=TipoMovimiento.SALIDA,
            motivo=MotivoMovimiento.MERMA,
            cantidad=Decimal("4.000"),
            usuario=self.usuario,
        )
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("6.000"))

    def test_salida_mayor_que_el_stock_es_rechazada(self):
        with self.assertRaises(ReglaNegocioError) as contexto:
            registrar_movimiento(
                insumo_id=self.insumo.id,
                tipo=TipoMovimiento.SALIDA,
                motivo=MotivoMovimiento.MERMA,
                cantidad=Decimal("50.000"),
                usuario=self.usuario,
            )
        self.assertEqual(contexto.exception.codigo, "stock_insuficiente")
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("10.000"))

    def test_ajuste_fija_el_stock_objetivo(self):
        registrar_movimiento(
            insumo_id=self.insumo.id,
            tipo=TipoMovimiento.AJUSTE,
            motivo=MotivoMovimiento.AJUSTE_MANUAL,
            cantidad=Decimal("0"),
            stock_objetivo=Decimal("7.500"),
            usuario=self.usuario,
        )
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("7.500"))

    def test_se_genera_alerta_al_bajar_del_minimo(self):
        registrar_movimiento(
            insumo_id=self.insumo.id,
            tipo=TipoMovimiento.SALIDA,
            motivo=MotivoMovimiento.MERMA,
            cantidad=Decimal("8.000"),
            usuario=self.usuario,
        )
        alertas = AlertaInventario.objects.filter(insumo=self.insumo, atendida=False)
        self.assertEqual(alertas.count(), 1)
        self.assertIn("Stock bajo", alertas.first().mensaje)

    def test_no_se_duplican_alertas_pendientes(self):
        for _ in range(3):
            registrar_movimiento(
                insumo_id=self.insumo.id,
                tipo=TipoMovimiento.SALIDA,
                motivo=MotivoMovimiento.MERMA,
                cantidad=Decimal("2.500"),
                usuario=self.usuario,
            )
        self.assertEqual(
            AlertaInventario.objects.filter(insumo=self.insumo, atendida=False).count(), 1
        )

    def test_la_alerta_se_cierra_al_reponer_stock(self):
        registrar_movimiento(
            insumo_id=self.insumo.id,
            tipo=TipoMovimiento.SALIDA,
            motivo=MotivoMovimiento.MERMA,
            cantidad=Decimal("8.000"),
            usuario=self.usuario,
        )
        registrar_movimiento(
            insumo_id=self.insumo.id,
            tipo=TipoMovimiento.ENTRADA,
            motivo=MotivoMovimiento.COMPRA,
            cantidad=Decimal("20.000"),
            usuario=self.usuario,
        )
        self.assertFalse(
            AlertaInventario.objects.filter(insumo=self.insumo, atendida=False).exists()
        )


class MovimientosApiTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario(RolUsuario.INVENTARIO, "inv@test.com")
        self.mesero = crear_usuario(RolUsuario.MESERO, "mesero@test.com")
        self.insumo = crear_insumo("Azucar", stock="12.000", minimo="4.000")

    def test_registrar_salida_por_api(self):
        autenticar(self.client, self.usuario)
        respuesta = self.client.post(
            "/api/inventario/movimientos/",
            {"insumo": self.insumo.id, "tipo": "salida", "motivo": "merma", "cantidad": "2.000"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 201)
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("10.000"))

    def test_stock_insuficiente_devuelve_400_con_codigo(self):
        autenticar(self.client, self.usuario)
        respuesta = self.client.post(
            "/api/inventario/movimientos/",
            {"insumo": self.insumo.id, "tipo": "salida", "motivo": "merma", "cantidad": "99.000"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()["code"], "stock_insuficiente")

    def test_mesero_no_puede_mover_inventario(self):
        autenticar(self.client, self.mesero)
        respuesta = self.client.post(
            "/api/inventario/movimientos/",
            {"insumo": self.insumo.id, "tipo": "salida", "motivo": "merma", "cantidad": "1.000"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 403)
