from decimal import Decimal

from django.test import TestCase

from apps.proveedores.models import Proveedor
from apps.usuarios.models import RolUsuario
from apps.usuarios.tests.factories import autenticar, crear_insumo, crear_usuario


class ComprasTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario(RolUsuario.ADMIN, "admin@test.com")
        autenticar(self.client, self.admin)
        self.proveedor = Proveedor.objects.create(nombre="Distribuidora Test")
        self.insumo = crear_insumo("Harina", stock="5.000", minimo="2.000")

    def _crear_compra(self, cantidad="10.000", precio="3.50"):
        return self.client.post(
            "/api/proveedores/compras/",
            {
                "proveedor": self.proveedor.id,
                "detalles": [
                    {"insumo": self.insumo.id, "cantidad": cantidad, "precio_unitario": precio}
                ],
            },
            content_type="application/json",
        )

    def test_crear_compra_calcula_el_total(self):
        respuesta = self._crear_compra()
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Decimal(respuesta.json()["total"]), Decimal("35.00"))
        self.assertEqual(respuesta.json()["estado"], "pendiente")

    def test_una_compra_pendiente_no_altera_el_stock(self):
        self._crear_compra()
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("5.000"))

    def test_recibir_una_compra_repone_el_stock(self):
        compra_id = self._crear_compra().json()["id"]
        respuesta = self.client.post(f"/api/proveedores/compras/{compra_id}/recibir/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["estado"], "recibida")

        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("15.000"))
        self.assertEqual(self.insumo.costo_unitario, Decimal("3.50"))

    def test_no_se_puede_recibir_dos_veces(self):
        compra_id = self._crear_compra().json()["id"]
        self.client.post(f"/api/proveedores/compras/{compra_id}/recibir/")
        respuesta = self.client.post(f"/api/proveedores/compras/{compra_id}/recibir/")
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()["code"], "estado_invalido")

        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("15.000"))

    def test_una_compra_sin_lineas_es_rechazada(self):
        respuesta = self.client.post(
            "/api/proveedores/compras/",
            {"proveedor": self.proveedor.id, "detalles": []},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_cancelar_una_compra_pendiente(self):
        compra_id = self._crear_compra().json()["id"]
        respuesta = self.client.post(f"/api/proveedores/compras/{compra_id}/cancelar/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["estado"], "cancelada")
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("5.000"))
