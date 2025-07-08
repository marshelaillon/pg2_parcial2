from django.db import models
from django.core.exceptions import ValidationError


class PedidoCono(models.Model):
    VARIANTES_CHOICES = [
        ("Carnívoro", "Carnívoro"),
        ("Vegetariano", "Vegetariano"),
        ("Saludable", "Saludable"),
    ]

    TAMANIO_CHOICES = [
        ("Pequeño", "Pequeño"),
        ("Mediano", "Mediano"),
        ("Grande", "Grande"),
    ]

    # Toppings predefinidos permitidos
    TOPPINGS_PREDEFINIDOS = [
        "queso_extra",
        "papas_al_hilo",
        "salchicha_extra",
        "bacon",
        "cebolla_caramelizada",
        "champiñones",
        "palta",
        "tomate",
        "lechuga",
        "pepino",
        "zanahoria",
        "pollo_grillado",
        "carne_molida",
        "tofu",
        "quinoa",
        "salsa_picante",
        "mayonesa",
        "ketchup",
        "mostaza",
    ]

    # El cliente es un campo de texto simple para almacenar el nombre.
    cliente = models.CharField(max_length=100, verbose_name="Cliente")
    variante = models.CharField(max_length=20, choices=VARIANTES_CHOICES)
    toppings = models.JSONField(default=list, blank=True)
    tamanio_cono = models.CharField(max_length=10, choices=TAMANIO_CHOICES)
    fecha_pedido = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Pedido de Cono"
        verbose_name_plural = "Pedidos de Conos"
        ordering = ["-fecha_pedido"]

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente} - {self.variante}"

    def clean(self):
        """Validación personalizada para los toppings"""
        if self.toppings:
            # Verificar que todos los toppings estén en la lista predefinida
            toppings_invalidos = []
            for topping in self.toppings:
                if topping not in self.TOPPINGS_PREDEFINIDOS:
                    toppings_invalidos.append(topping)

            if toppings_invalidos:
                raise ValidationError(
                    f"Los siguientes toppings no están permitidos: {', '.join(toppings_invalidos)}. "
                    f"Toppings permitidos: {', '.join(self.TOPPINGS_PREDEFINIDOS)}"
                )

    def save(self, *args, **kwargs):
        """Override del método save para ejecutar validaciones"""
        self.clean()
        super().save(*args, **kwargs)
