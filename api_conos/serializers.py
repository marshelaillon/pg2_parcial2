from rest_framework import serializers
from .models import PedidoCono
from .patterns import ConoDirector, OperationLogger


class PedidoConoSerializer(serializers.ModelSerializer):
    """
    Serializador para PedidoCono con atributos calculados usando patrones de diseño
    """

    # Atributos calculados (solo lectura)
    precio_final = serializers.SerializerMethodField()
    ingredientes_finales = serializers.SerializerMethodField()

    class Meta:
        model = PedidoCono
        fields = [
            "id",
            "cliente",
            "variante",
            "toppings",
            "tamanio_cono",
            "fecha_pedido",
            "precio_final",  # Atributo calculado
            "ingredientes_finales",  # Atributo calculado
        ]
        read_only_fields = ["fecha_pedido"]

    def _get_calculated_data(self, obj):
        """
        Método unificado para calcular los datos del cono una sola vez y cachearlos
        dentro de la instancia del serializador para evitar cálculos repetidos.
        """
        # Usamos un atributo cacheado en la instancia del serializador
        if not hasattr(self, "_calculated_data_cache"):
            self._calculated_data_cache = {}

        if obj.id not in self._calculated_data_cache:
            director = ConoDirector()
            resultado = director.construir_cono_completo(
                variante=obj.variante,
                tamanio=obj.tamanio_cono,
                toppings=obj.toppings or [],
                pedido_id=obj.id or 0,
            )
            self._calculated_data_cache[obj.id] = resultado

        return self._calculated_data_cache[obj.id]

    def get_precio_final(self, obj):
        """
        Calcular precio final usando patrones de diseño

        Aplica:
        - Factory Method: Para crear el cono base según variante
        - Builder: Para personalizar con toppings
        - Singleton: Para logging de operaciones
        """
        try:
            resultado = self._get_calculated_data(obj)
            return resultado.get("precio_final", 0.0)
        except Exception as e:
            logger = OperationLogger()
            logger.log_operation("ERROR_PRECIO_FINAL", obj.id or 0, {"error": str(e)})
            return 0.0

    def get_ingredientes_finales(self, obj):
        """
        Calcular ingredientes finales usando patrones de diseño

        Aplica:
        - Factory Method: Para obtener ingredientes base según variante
        - Builder: Para agregar toppings seleccionados
        - Singleton: Para logging de operaciones
        """
        try:
            resultado = self._get_calculated_data(obj)
            return resultado.get("ingredientes_finales", [])
        except Exception as e:
            logger = OperationLogger()
            logger.log_operation(
                "ERROR_INGREDIENTES_FINALES", obj.id or 0, {"error": str(e)}
            )
            return []

    def validate_toppings(self, value):
        """Validar que los toppings estén en la lista permitida"""
        if value:
            toppings_invalidos = []
            for topping in value:
                if topping not in PedidoCono.TOPPINGS_PREDEFINIDOS:
                    toppings_invalidos.append(topping)

            if toppings_invalidos:
                raise serializers.ValidationError(
                    f"Los siguientes toppings no están permitidos: {', '.join(toppings_invalidos)}"
                )

        return value

    def to_representation(self, instance):
        """Personalizar la representación del serializador"""
        data = super().to_representation(instance)

        # Agregar información adicional para debugging
        if hasattr(self, "context") and self.context.get("include_debug", False):
            logger = OperationLogger()
            logs_pedido = [
                log for log in logger.get_logs() if log.get("pedido_id") == instance.id
            ]
            data["debug_logs"] = logs_pedido

        return data


class PedidoConoDetailSerializer(PedidoConoSerializer):
    """Serializador detallado con información adicional"""

    total_toppings = serializers.SerializerMethodField()
    tiene_descuento = serializers.SerializerMethodField()
    tipo_cono = serializers.SerializerMethodField()

    class Meta(PedidoConoSerializer.Meta):
        fields = PedidoConoSerializer.Meta.fields + [
            "total_toppings",
            "tiene_descuento",
            "tipo_cono",
        ]

    def get_total_toppings(self, obj):
        """Obtener número total de toppings"""
        return len(obj.toppings) if obj.toppings else 0

    def get_tiene_descuento(self, obj):
        """Verificar si el pedido tiene descuento"""
        return len(obj.toppings or []) >= 3

    def get_tipo_cono(self, obj):
        """Obtener tipo de cono basado en la variante"""
        tipos = {
            "Carnívoro": "ConoCarnivoro",
            "Vegetariano": "ConoVegetariano",
            "Saludable": "ConoSaludable",
        }
        return tipos.get(obj.variante, "ConoGenerico")
