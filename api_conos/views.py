from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PedidoCono
from .serializers import PedidoConoSerializer, PedidoConoDetailSerializer
from .patterns import OperationLogger


class PedidoConoViewSet(viewsets.ModelViewSet):
    queryset = PedidoCono.objects.all()
    serializer_class = PedidoConoSerializer

    def get_serializer_class(self):
        """Usar serializador detallado para retrieve"""
        if self.action == "retrieve":
            return PedidoConoDetailSerializer
        return PedidoConoSerializer

    @action(detail=False, methods=["get"])
    def toppings_disponibles(self, request):
        """Endpoint para obtener la lista de toppings disponibles"""
        return Response(
            {
                "toppings_disponibles": PedidoCono.TOPPINGS_PREDEFINIDOS,
                "total_toppings": len(PedidoCono.TOPPINGS_PREDEFINIDOS),
            }
        )

    @action(detail=False, methods=["get"])
    def logs_operaciones(self, request):
        """Endpoint para obtener logs de operaciones (usando Singleton)"""
        logger = OperationLogger()
        logs = logger.get_logs()

        pedido_id = request.query_params.get("pedido_id")
        if pedido_id:
            try:
                pedido_id = int(pedido_id)
                logs = [log for log in logs if log.get("pedido_id") == pedido_id]
            except ValueError:
                pass

        # Filtrar por tipo de operación
        operation_type = request.query_params.get("operation_type")
        if operation_type:
            logs = [log for log in logs if log.get("operation_type") == operation_type]

        # Limitar resultados
        limit = request.query_params.get("limit", 100)
        try:
            limit = int(limit)
            logs = logs[-limit:]  # Obtener los últimos N logs
        except ValueError:
            logs = logs[-100:]  # Por defecto, últimos 100

        return Response(
            {
                "logs": logs,
                "total_logs": len(logger.get_logs()),
                "filtered_logs": len(logs),
            }
        )

    @action(detail=False, methods=["post"])
    def limpiar_logs(self, request):
        """Endpoint para limpiar logs (usando Singleton)"""
        logger = OperationLogger()
        logs_count = len(logger.get_logs())
        logger.clear_logs()

        return Response(
            {
                "message": f"Se limpiaron {logs_count} logs",
                "logs_eliminados": logs_count,
            }
        )

    @action(detail=True, methods=["get"])
    def detalle_calculo(self, request, pk=None):
        """Endpoint para obtener detalles del cálculo de un pedido específico"""
        pedido = self.get_object()

        # Obtener el serializador con contexto de debug
        serializer = self.get_serializer(
            pedido, context={"include_debug": True, "request": request}
        )

        return Response(serializer.data)
