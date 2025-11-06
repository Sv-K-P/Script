from __future__ import annotations

from typing import List
from src.models.pulse_group_models import PulseItem


def apply_pulse_mask(items: List[PulseItem], mask: List[bool]) -> List[PulseItem]:
    """Возвращает новый список PulseItem, отфильтрованный по bool-маске.

    Длина маски должна совпадать с количеством элементов.
    Помимо фильтрации, в результирующих элементах поле approved
    синхронизируется с соответствующим значением маски.
    """
    if len(items) != len(mask):
        raise ValueError(f"Длина маски {len(mask)} != числу импульсов {len(items)}")

    filtered: List[PulseItem] = []
    for it, keep in zip(items, mask):
        if keep:
            # Создаём новый PulseItem с синхронизированным approved
            filtered.append(PulseItem(pulse=it.pulse, approved=True))
    return filtered


