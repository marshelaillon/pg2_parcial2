from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoConoViewSet

router = DefaultRouter()
router.register(r"pedidos", PedidoConoViewSet, basename="pedido")

urlpatterns = [
    path("", include(router.urls)),
]
