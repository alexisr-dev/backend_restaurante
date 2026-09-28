from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Usuario
from .permissions import GestionUsuarios
from .serializers import (
    CambioPasswordSerializer,
    LoginSerializer,
    PerfilSerializer,
    UsuarioSerializer,
)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = []


class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(PerfilSerializer(request.user).data)


class CambioPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CambioPasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Contrasena actualizada."}, status=status.HTTP_200_OK)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [GestionUsuarios]
    filterset_fields = ["rol", "activo"]
    search_fields = ["nombre", "email"]
    ordering_fields = ["nombre", "created_at"]

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        usuario = self.get_object()
        usuario.activo = True
        usuario.save(update_fields=["activo"])
        return Response(UsuarioSerializer(usuario).data)
