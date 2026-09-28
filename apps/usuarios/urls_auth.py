from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import CambioPasswordView, LoginView, PerfilView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("perfil/", PerfilView.as_view(), name="perfil"),
    path("password/", CambioPasswordView.as_view(), name="cambio-password"),
]
