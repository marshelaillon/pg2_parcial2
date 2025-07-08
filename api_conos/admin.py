from django.contrib import admin
from .models import PedidoCono


@admin.register(PedidoCono)
class PedidoConoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cliente",
        "variante",
        "tamanio_cono",
        "fecha_pedido",
        "get_toppings_display",
    ]
    list_filter = ["variante", "tamanio_cono", "fecha_pedido"]
    search_fields = ["cliente", "variante"]
    readonly_fields = ["fecha_pedido"]

    fieldsets = (
        ("Información del Cliente", {"fields": ("cliente",)}),
        ("Detalles del Pedido", {"fields": ("variante", "tamanio_cono", "toppings")}),
        (
            "Información del Sistema",
            {"fields": ("fecha_pedido",), "classes": ("collapse",)},
        ),
    )

    def get_toppings_display(self, obj):
        """Mostrar toppings de manera legible en el admin"""
        if obj.toppings:
            return ", ".join(obj.toppings)
        return "Sin toppings"

    get_toppings_display.short_description = "Toppings"
