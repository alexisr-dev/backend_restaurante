from django.test import TestCase

from apps.usuarios.models import RolUsuario
from apps.usuarios.tests.factories import autenticar, crear_insumo, crear_usuario

RUTAS = [
    "resumen",
    "ventas-diarias",
    "productos-mas-vendidos",
    "insumos-stock-bajo",
    "consumo-insumos",
    "ventas-por-categoria",
    "pedidos",
]


class ReportesTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario(RolUsuario.ADMIN, "admin@test.com")
        self.mesero = crear_usuario(RolUsuario.MESERO, "mesero@test.com")

    def test_todas_las_vistas_responden(self):
        autenticar(self.client, self.admin)
        for ruta in RUTAS:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(f"/api/reportes/{ruta}/").status_code, 200)

    def test_el_resumen_trae_todos_los_indicadores(self):
        autenticar(self.client, self.admin)
        datos = self.client.get("/api/reportes/resumen/").json()
        for campo in [
            "ventas_hoy",
            "pedidos_hoy",
            "pedidos_activos",
            "mesas_ocupadas",
            "insumos_en_alerta",
            "productos_activos",
        ]:
            self.assertIn(campo, datos)

    def test_stock_bajo_lista_los_insumos_en_alerta(self):
        crear_insumo("Cafe", stock="1.000", minimo="4.000")
        crear_insumo("Arroz", stock="30.000", minimo="5.000")
        autenticar(self.client, self.admin)
        datos = self.client.get("/api/reportes/insumos-stock-bajo/").json()
        self.assertEqual([fila["nombre"] for fila in datos], ["Cafe"])

    def test_un_mesero_no_accede_a_los_reportes(self):
        autenticar(self.client, self.mesero)
        self.assertEqual(self.client.get("/api/reportes/resumen/").status_code, 403)

    def test_los_reportes_exigen_autenticacion(self):
        self.assertEqual(self.client.get("/api/reportes/resumen/").status_code, 401)
