from src.core.project_root import PROJECT_ROOT
from src.core.config_loader import load_data_config


def debug_paths():
    print(f"📍 Корень проекта: {PROJECT_ROOT}")

    config = load_data_config()

    print("\n📁 Абсолютные пути конфигурации:")
    print(f"  raw_data_folder: {config.raw_data_folder}")
    print(f"  processed_folder: {config.processed_folder}")
    print(f"  selections_folder: {config.selections_folder}")
    print(f"  outputs_folder: {config.outputs_folder}")

    print("\n✅ Проверка существования папок:")
    for folder_name, folder_path in [
        ("raw_data_folder", config.raw_data_folder),
        ("processed_folder", config.processed_folder),
        ("selections_folder", config.selections_folder),
        ("outputs_folder", config.outputs_folder),
    ]:
        exists = folder_path.exists()
        print(f"  {folder_name}: {folder_path} - {'✓' if exists else '✗'}")


if __name__ == "__main__":
    debug_paths()