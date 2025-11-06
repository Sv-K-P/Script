
import numpy as np
from src.models.pulse_models import PulseModel


def compute_charge(pulse: PulseModel) -> float:
    """Вычисляет заряд одного импульса (Кулон)."""
    q = np.trapezoid(pulse.current, pulse.time)
    return float(q)

def compute_all_charges(pulses: list[PulseModel]) -> np.ndarray:
    """Возвращает массив зарядов для всех импульсов."""
    if not pulses:
        raise ValueError("Список импульсов не может быть пустым")
    charges = np.array([compute_charge(p) for p in pulses])
    return charges