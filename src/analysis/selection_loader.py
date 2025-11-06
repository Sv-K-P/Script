from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import json

def _approved_from_group_object(obj: dict) -> List[bool]:
    if "pulses" not in obj or not isinstance(obj["pulses"], list):
        raise ValueError("Объект группы должен содержать список 'pulses'")
    approved: List[bool] = []
    for item in obj["pulses"]:
        if not isinstance(item, dict) or "approved" not in item:
            raise ValueError("Элемент pulses должен содержать поле 'approved'")
        approved.append(bool(item["approved"]))
    return approved


def load_selections(path: Path, total: int, input_file_name: Optional[str] = None) -> List[bool]:
    """
    Поддерживаем форматы:
      1) Простой JSON-массив bool: [true,false,...] длиной total
      2) Одиночная группа (PulseGroupModel-подобная):
         {"file_name": "...", "pulses": [{"approved": true}, ...]}
      3) Агрегатор групп:
         {"groups": [ {"file_name": "pulses.txt", "pulses": [...]}, ... ]}

    Возвращаем список approved длиной total.
    Для формата (3) требуется указать input_file_name (обычно имя входного файла импульсов).
    """
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Не найден selections: {path}")

    text = path.read_text(encoding="utf-8")
    data = json.loads(text)

    # Формат 1: массив bool
    if isinstance(data, list) and all(isinstance(x, bool) for x in data):
        if len(data) != total:
            raise ValueError(f"Длина selections {len(data)} != числу импульсов {total}")
        return list(data)

    # Формат 2: одиночная группа
    if isinstance(data, dict) and "pulses" in data:
        approved = _approved_from_group_object(data)
        if len(approved) != total:
            raise ValueError(f"Длина selections {len(approved)} != числу импульсов {total}")
        return approved

    # Формат 3: агрегатор групп
    if isinstance(data, dict) and "groups" in data and isinstance(data["groups"], list):
        if not input_file_name:
            raise ValueError("Для формата 'groups' требуется input_file_name")
        for grp in data["groups"]:
            if isinstance(grp, dict) and grp.get("file_name") == input_file_name:
                approved = _approved_from_group_object(grp)
                if len(approved) != total:
                    raise ValueError(f"Длина selections {len(approved)} != числу импульсов {total}")
                return approved
        raise ValueError(f"В selections не найдена группа для {input_file_name}")

    raise ValueError("Неподдерживаемый формат selections")


