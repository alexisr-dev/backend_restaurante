from rest_framework.routers import DefaultRouter

from .views import LogAuditoriaViewSet

router = DefaultRouter()
router.register("logs", LogAuditoriaViewSet, basename="log-auditoria")

urlpatterns = router.urls
