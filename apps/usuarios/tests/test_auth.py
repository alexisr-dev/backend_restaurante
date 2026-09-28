from django.test import TestCase

from apps.usuarios.models import RolUsuario, Usuario

from .factories import PASSWORD, autenticar, crear_usuario


class AutenticacionTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario(RolUsuario.ADMIN, "admin@test.com")
        self.mesero = crear_usuario(RolUsuario.MESERO, "mesero@test.com")

    def test_login_devuelve_tokens_y_perfil(self):
        respuesta = self.client.post(
            "/api/auth/login/",
            {"email": "admin@test.com", "password": PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertIn("access", datos)
        self.assertIn("refresh", datos)
        self.assertEqual(datos["usuario"]["rol"], "admin")

    def test_login_con_password_incorrecta_falla(self):
        respuesta = self.client.post(
            "/api/auth/login/",
            {"email": "admin@test.com", "password": "incorrecta"},
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_el_token_incluye_el_rol_para_compartirlo_con_fastapi(self):
        import jwt
        from django.conf import settings

        token = autenticar(self.client, self.mesero)
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        self.assertEqual(payload["rol"], "mesero")
        self.assertEqual(payload["email"], "mesero@test.com")

    def test_perfil_requiere_autenticacion(self):
        self.assertEqual(self.client.get("/api/auth/perfil/").status_code, 401)

    def test_password_se_guarda_hasheada(self):
        usuario = Usuario.objects.get(email="admin@test.com")
        self.assertNotEqual(usuario.password, PASSWORD)
        self.assertTrue(usuario.check_password(PASSWORD))


class PermisosPorRolTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario(RolUsuario.ADMIN, "admin@test.com")
        self.mesero = crear_usuario(RolUsuario.MESERO, "mesero@test.com")
        self.inventario = crear_usuario(RolUsuario.INVENTARIO, "inv@test.com")

    def test_solo_admin_gestiona_usuarios(self):
        autenticar(self.client, self.mesero)
        self.assertEqual(self.client.get("/api/usuarios/").status_code, 403)

        autenticar(self.client, self.admin)
        self.assertEqual(self.client.get("/api/usuarios/").status_code, 200)

    def test_mesero_lee_catalogo_pero_no_lo_modifica(self):
        autenticar(self.client, self.mesero)
        self.assertEqual(self.client.get("/api/catalogo/productos/").status_code, 200)
        respuesta = self.client.post(
            "/api/catalogo/categorias/", {"nombre": "Nueva"}, content_type="application/json"
        )
        self.assertEqual(respuesta.status_code, 403)

    def test_rol_inventario_puede_crear_categorias(self):
        autenticar(self.client, self.inventario)
        respuesta = self.client.post(
            "/api/catalogo/categorias/", {"nombre": "Nueva"}, content_type="application/json"
        )
        self.assertEqual(respuesta.status_code, 201)

    def test_baja_logica_de_usuario(self):
        autenticar(self.client, self.admin)
        respuesta = self.client.delete(f"/api/usuarios/{self.mesero.id}/")
        self.assertEqual(respuesta.status_code, 204)
        self.mesero.refresh_from_db()
        self.assertFalse(self.mesero.activo)
