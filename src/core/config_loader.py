from pathlib import Path
import json
from src.models.config_models import ConfigModel, DataConfigModel
from src.models.selection_models import SelectionModel
from src.core.project_root import PROJECT_ROOT


def load_config(config_path: Path) -> ConfigModel:
    # Делаем путь абсолютным относительно корня проекта
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    config = ConfigModel(**data)
    return config


def load_selections(selections_folder: Path) -> list[SelectionModel]:
    """Загружает селекции из общего файла selections.json"""
    # Делаем путь абсолютным относительно корня проекта
    if not selections_folder.is_absolute():
        selections_folder = PROJECT_ROOT / selections_folder

    selections_path = selections_folder / "selections.json"

    if not selections_path.exists():
        raise FileNotFoundError(f"Файл селекций не найден: {selections_path}")

    with open(selections_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Если data - это список, значит это массив селекций
    if isinstance(data, list):
        return [SelectionModel(**entry) for entry in data]
    # Если data - это один объект, оборачиваем в список
    elif isinstance(data, dict):
        return [SelectionModel(**data)]
    else:
        raise ValueError(f"Неверный формат файла селекций: {selections_path}")


def load_data_config(config_path: Path | None = None) -> DataConfigModel:
    """Загружает конфигурацию путей к данным."""
    if config_path is None:
        config_path = PROJECT_ROOT / "configs/data_config.json"
    elif not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                # Заменяем обратные слеши на прямые для надежности
                content = content.replace('\\', '/')
                data = json.loads(content)
            return DataConfigModel(**data)
        else:
            # Создаем конфиг по умолчанию
            return _create_default_data_config(config_path)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"⚠️ Ошибка загрузки конфига {config_path}: {e}")
        print("🔄 Создаю новый конфиг по умолчанию...")
        return _create_default_data_config(config_path)


def _create_default_data_config(config_path: Path) -> DataConfigModel:
    """Создает конфигурацию по умолчанию и сохраняет в файл."""
    default_config = DataConfigModel()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(default_config.model_dump_jsonable(), f, indent=2, ensure_ascii=False)

    print(f"✅ Создан новый конфиг: {config_path}")
    return default_config