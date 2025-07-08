# api_conos/patterns.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any
import threading


class OperationLogger:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._logs = []  # Inicializar solo una vez
        return cls._instance

    def log_operation(
        self, operation_type: str, pedido_id: int, details: Dict[str, Any]
    ):
        """Registrar una operación de cálculo"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "pedido_id": pedido_id,
            "details": details,
        }
        self._logs.append(log_entry)
        print(f"[LOG] {operation_type} - Pedido {pedido_id}: {details}")

    def get_logs(self) -> List[Dict[str, Any]]:
        """Obtener todos los logs"""
        return self._logs.copy()

    def clear_logs(self):
        """Limpiar todos los logs"""
        self._logs.clear()


class ConoBase(ABC):

    def __init__(self, tamanio: str):
        self.tamanio = tamanio
        self.precio_base = self._get_precio_base()
        self.ingredientes_base = self._get_ingredientes_base()
        self.precio_final = self.precio_base
        self.ingredientes_finales = self.ingredientes_base.copy()

    @abstractmethod
    def _get_precio_base(self) -> float:
        """Obtener precio base según el tamaño"""
        pass

    @abstractmethod
    def _get_ingredientes_base(self) -> List[str]:
        """Obtener ingredientes base del cono"""
        pass

    def agregar_precio(self, precio: float):
        """Agregar precio al cono"""
        self.precio_final += precio

    def agregar_ingrediente(self, ingrediente: str):
        """Agregar ingrediente al cono"""
        if ingrediente not in self.ingredientes_finales:
            self.ingredientes_finales.append(ingrediente)


class ConoCarnivoro(ConoBase):
    """Cono carnívoro con ingredientes base de carne"""

    def _get_precio_base(self) -> float:
        precios = {"Pequeño": 15.0, "Mediano": 20.0, "Grande": 25.0}
        return precios.get(self.tamanio, 20.0)

    def _get_ingredientes_base(self) -> List[str]:
        return ["carne_molida", "cebolla", "salsa_especial", "pan_cono"]


class ConoVegetariano(ConoBase):
    """Cono vegetariano con ingredientes base vegetales"""

    def _get_precio_base(self) -> float:
        precios = {"Pequeño": 12.0, "Mediano": 17.0, "Grande": 22.0}
        return precios.get(self.tamanio, 17.0)

    def _get_ingredientes_base(self) -> List[str]:
        return ["queso", "tomate", "lechuga", "cebolla", "salsa_vegetal", "pan_cono"]


class ConoSaludable(ConoBase):
    """Cono saludable con ingredientes base saludables"""

    def _get_precio_base(self) -> float:
        precios = {"Pequeño": 18.0, "Mediano": 23.0, "Grande": 28.0}
        return precios.get(self.tamanio, 23.0)

    def _get_ingredientes_base(self) -> List[str]:
        return [
            "quinoa",
            "palta",
            "tomate",
            "lechuga",
            "zanahoria",
            "salsa_yogurt",
            "pan_integral",
        ]


class ConoFactory:
    """Factory para crear conos según la variante"""

    @staticmethod
    def crear_cono(variante: str, tamanio: str) -> ConoBase:
        """Crear un cono según la variante especificada"""
        if variante == "Carnívoro":
            return ConoCarnivoro(tamanio)
        elif variante == "Vegetariano":
            return ConoVegetariano(tamanio)
        elif variante == "Saludable":
            return ConoSaludable(tamanio)
        else:
            raise ValueError(f"Variante de cono no soportada: {variante}")


class ConoBuilder:
    """Builder para construir conos personalizados paso a paso"""

    PRECIOS_TOPPINGS = {
        "queso_extra": 2.0,
        "papas_al_hilo": 3.0,
        "salchicha_extra": 4.0,
        "bacon": 5.0,
        "cebolla_caramelizada": 1.5,
        "champiñones": 2.5,
        "palta": 3.5,
        "tomate": 1.0,
        "lechuga": 0.5,
        "pepino": 1.0,
        "zanahoria": 1.0,
        "pollo_grillado": 6.0,
        "carne_molida": 5.0,
        "tofu": 3.0,
        "quinoa": 2.0,
        "salsa_picante": 0.5,
        "mayonesa": 0.5,
        "ketchup": 0.5,
        "mostaza": 0.5,
    }

    def __init__(self, cono_base: ConoBase):
        self.cono = cono_base
        self.logger = OperationLogger()

    def agregar_toppings(self, toppings: List[str]) -> "ConoBuilder":
        """Agregar toppings al cono"""
        for topping in toppings:
            if topping in self.PRECIOS_TOPPINGS:
                precio_topping = self.PRECIOS_TOPPINGS[topping]
                self.cono.agregar_precio(precio_topping)
                self.cono.agregar_ingrediente(topping)

                # Log de la operación
                self.logger.log_operation(
                    "ADD_TOPPING",
                    0,  # Se actualizará en el serializador
                    {"topping": topping, "precio": precio_topping},
                )

        return self

    def aplicar_descuento_combo(self) -> "ConoBuilder":
        """Aplicar descuento si tiene más de 3 toppings"""
        num_toppings_extra = len(
            [
                ing
                for ing in self.cono.ingredientes_finales
                if ing in self.PRECIOS_TOPPINGS
            ]
        )

        if num_toppings_extra >= 3:
            descuento = self.cono.precio_final * 0.1  # 10% de descuento
            self.cono.precio_final -= descuento

            # Log del descuento
            self.logger.log_operation(
                "APPLY_DISCOUNT",
                0,  # Se actualizará en el serializador
                {"descuento": descuento, "motivo": "combo_3_toppings"},
            )

        return self

    def build(self) -> Dict[str, Any]:
        """Construir el resultado final del cono"""
        return {
            "precio_final": round(self.cono.precio_final, 2),
            "ingredientes_finales": self.cono.ingredientes_finales,
            "tamanio": self.cono.tamanio,
            "tipo": self.cono.__class__.__name__,
        }


class ConoDirector:
    """Director que coordina la construcción de conos usando los patrones"""

    def __init__(self):
        self.factory = ConoFactory()
        self.logger = OperationLogger()

    def construir_cono_completo(
        self, variante: str, tamanio: str, toppings: List[str], pedido_id: int
    ) -> Dict[str, Any]:
        """Construir un cono completo aplicando todos los patrones"""

        # 1. Factory Method: Crear cono base
        cono_base = self.factory.crear_cono(variante, tamanio)

        # Log de creación del cono base
        self.logger.log_operation(
            "CREATE_BASE_CONO",
            pedido_id,
            {
                "variante": variante,
                "tamanio": tamanio,
                "precio_base": cono_base.precio_base,
                "ingredientes_base": cono_base.ingredientes_base,
            },
        )

        # 2. Builder: Personalizar el cono
        builder = ConoBuilder(cono_base)
        resultado = builder.agregar_toppings(toppings).aplicar_descuento_combo().build()

        # Log del resultado final
        self.logger.log_operation("CONO_COMPLETED", pedido_id, resultado)

        return resultado
