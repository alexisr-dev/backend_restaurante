from rest_framework.routers import DefaultRouter

from .views import CategoriaViewSet, InsumoViewSet, ProductoViewSet, RecetaProductoViewSet

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("productos", ProductoViewSet, basename="producto")
router.register("insumos", InsumoViewSet, basename="insumo")
router.register("recetas", RecetaProductoViewSet, basename="receta")

urlpatterns = router.urls
