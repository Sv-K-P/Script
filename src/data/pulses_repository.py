from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json

from src.models.config_models import DataConfigModel
from src.models.pulse_models import PulseModel
from src.models.pulse_group_models import PulseGroupModel, PulseItem
from src.validation.pulse_loader import load_pulses
from src.core.pulse_writer import write_pulses as write_pulses_txt


class PulsesRepository:
    """Единая точка доступа к файлам импульсов и selections."""

    @staticmethod
    def read_pulses(path: Path) -> List[PulseModel]:
        return load_pulses(path)

    @staticmethod
    def write_pulses(pulses: List[PulseModel], path: Path) -> None:
        write_pulses_txt(pulses, path)


    @staticmethod
    def _approved_from_group_object(obj: dict) -> List[bool]:
        if "pulses" not in obj or not isinstance(obj["pulses"], list):
            raise ValueError("Объект группы должен содержать список 'pulses'")
        approved: List[bool] = []
        for item in obj["pulses"]:
            if not isinstance(item, dict) or "approved" not in item:
                raise ValueError("Элемент pulses должен содержать поле 'approved'")
            approved.append(bool(item["approved"]))
        return approved

    @staticmethod
    def read_selections(path: Path, total: int, input_file_name: Optional[str] = None) -> List[bool]:
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Не найден selections: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))

        if isinstance(data, list) and all(isinstance(x, bool) for x in data):
            if len(data) != total:
                raise ValueError(f"Длина selections {len(data)} != числу импульсов {total}")
            return list(data)

        if isinstance(data, dict) and "pulses" in data:
            approved = PulsesRepository._approved_from_group_object(data)
            if len(approved) != total:
                raise ValueError(f"Длина selections {len(approved)} != числу импульсов {total}")
            return approved

        if isinstance(data, dict) and "groups" in data and isinstance(data["groups"], list):
            if not input_file_name:
                raise ValueError("Для формата 'groups' требуется input_file_name")
            for grp in data["groups"]:
                if isinstance(grp, dict) and grp.get("file_name") == input_file_name:
                    approved = PulsesRepository._approved_from_group_object(grp)
                    if len(approved) != total:
                        raise ValueError(f"Длина selections {len(approved)} != числу импульсов {total}")
                    return approved
            raise ValueError(f"В selections не найдена группа для {input_file_name}")

        raise ValueError("Неподдерживаемый формат selections")

    @staticmethod
    def load_group(pulses_path: Path, selections_path: Optional[Path] = None) -> PulseGroupModel:
        pulses = PulsesRepository.read_pulses(pulses_path)
        approved: Optional[List[bool]] = None
        if selections_path is None:
            candidate = PulsesRepository.default_selections_path(pulses_path)
            if candidate.exists() and candidate.is_file():
                selections_path = candidate
        if selections_path is not None:
            approved = PulsesRepository.read_selections(
                selections_path,
                total=len(pulses),
                input_file_name=pulses_path.name,
            )
        items: List[PulseItem] = []
        if approved is None:
            items = [PulseItem(pulse=p, approved=True) for p in pulses]
        else:
            for p, ok in zip(pulses, approved):
                if ok:
                    items.append(PulseItem(pulse=p, approved=True))
        return PulseGroupModel(file_name=pulses_path.name, pulses=items)

    @staticmethod
    def auto_discover_files(data_config: DataConfigModel) -> dict[Path, PulseGroupModel]:
        """Автоматически находит все файлы импульсов и соответствующие селекции."""
        results = {}

        # Ищем .txt файлы в processed folder
        for txt_file in data_config.processed_folder.glob("*.txt"):
            selections_path = data_config.selections_folder / f"{txt_file.stem}_selections.json"
            group = PulsesRepository.load_group(txt_file, selections_path if selections_path.exists() else None)
            results[txt_file] = group

        return results

    @staticmethod
    def get_auto_output_path(data_config: DataConfigModel, base_name: str = "approved") -> Path:
        """Генерирует автоматический путь для сохранения результатов."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return data_config.outputs_folder / "approved" / f"{base_name}_{timestamp}.txt"

    @staticmethod
    def write_selections_for_group(pulses_path: Path, group: PulseGroupModel) -> Path:
        """Сохраняет селекции в папку data/selections"""
        # Используем имя исходного файла для создания имени файла селекций
        selections_filename = f"{pulses_path.stem}_selections.json"

        # Сохраняем в папку selections, а не рядом с исходным файлом
        from src.core.config_loader import load_data_config
        data_config = load_data_config()
        selections_path = data_config.selections_folder / selections_filename

        group_for_save = {
            "file_name": pulses_path.name,
            "pulses": [{"approved": it.approved} for it in group.pulses],
        }

        with open(selections_path, "w", encoding="utf-8") as f:
            json.dump(group_for_save, f, indent=2, ensure_ascii=False)

        return selections_path

    @staticmethod
    def default_selections_path(pulses_path: Path) -> Path:
        """Возвращает путь к файлу селекций по умолчанию."""
        from src.core.config_loader import load_data_config
        data_config = load_data_config()
        selections_filename = f"{pulses_path.stem}_selections.json"
        return data_config.selections_folder / selections_filename


