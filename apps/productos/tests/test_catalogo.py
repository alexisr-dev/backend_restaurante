from decimal import Decimal

from django.test import TestCase

from apps.productos.models import Producto
from apps.usuarios.models import RolUsuario
from apps.usuarios.tests.factories import (
    autenticar,
    crear_insumo,
    crear_producto_con_receta,
    crear_usuario,
)


class CatalogoTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario(RolUsuario.ADMIN, "admin@test.com")
        autenticar(self.client, self.admin)
        self.insumo = crear_insumo("Lomo", stock="20.000", minimo="5.000")

    def test_crear_producto(self):
        respuesta = self.client.post(
            "/api/catalogo/productos/",
            {"nombre": "Lomo Saltado", "precio": "34.00"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Decimal(respuesta.json()["precio"]), Decimal("34.00"))

    def test_precio_negativo_rechazado(self):
        respuesta = self.client.post(
            "/api/catalogo/productos/",
            {"nombre": "Invalido", "precio": "-5.00"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_el_producto_expone_su_receta(self):
        producto = crear_producto_con_receta("Lomo Saltado", "34.00", {self.insumo: "0.250"})
        respuesta = self.client.get(f"/api/catalogo/productos/{producto.id}/")
        self.assertEqual(respuesta.status_code, 200)
        receta = respuesta.json()["receta"]
        self.assertEqual(len(receta), 1)
        self.assertEqual(receta[0]["insumo_nombre"], "Lomo")
        self.assertEqual(Decimal(receta[0]["cantidad_requerida"]), Decimal("0.250"))

    def test_agregar_linea_de_receta(self):
        producto = crear_producto_con_receta("Arroz con pollo", "28.00")
        respuesta = self.client.post(
            f"/api/catalogo/productos/{producto.id}/receta/",
            {"insumo": self.insumo.id, "cantidad_requerida": "0.300"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(producto.receta.count(), 1)

    def test_cantidad_de_receta_debe_ser_positiva(self):
        producto = crear_producto_con_receta("Ceviche", "32.00")
        respuesta = self.client.post(
            f"/api/catalogo/productos/{producto.id}/receta/",
            {"insumo": self.insumo.id, "cantidad_requerida": "0"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_eliminar_producto_es_baja_logica(self):
        producto = crear_producto_con_receta("Postre", "12.00")
        respuesta = self.client.delete(f"/api/catalogo/productos/{producto.id}/")
        self.assertEqual(respuesta.status_code, 204)
        producto.refresh_from_db()
        self.assertFalse(producto.activo)
        self.assertTrue(Producto.objects.filter(pk=producto.pk).exists())

    def test_el_stock_no_se_edita_desde_el_catalogo(self):
        respuesta = self.client.patch(
            f"/api/catalogo/insumos/{self.insumo.id}/",
            {"stock_actual": "999.000"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("20.000"))

    def test_marca_de_alerta_en_el_serializador(self):
        bajo = crear_insumo("Sal", stock="1.000", minimo="5.000")
        respuesta = self.client.get(f"/api/catalogo/insumos/{bajo.id}/")
        self.assertTrue(respuesta.json()["en_alerta"])
