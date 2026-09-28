from rest_framework.routers import DefaultRouter

from .views import AlertaInventarioViewSet, MovimientoInventarioViewSet

router = DefaultRouter()
router.register("movimientos", MovimientoInventarioViewSet, basename="movimiento")
router.register("alertas", AlertaInventarioViewSet, basename="alerta")

urlpatterns = router.urls
