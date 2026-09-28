from rest_framework.routers import DefaultRouter

from .views import CompraViewSet, ProveedorViewSet

router = DefaultRouter()
router.register("proveedores", ProveedorViewSet, basename="proveedor")
router.register("compras", CompraViewSet, basename="compra")

urlpatterns = router.urls
