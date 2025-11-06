from pathlib import Path
from src.core.config_loader import load_data_config


def debug_structure():
    data_config = load_data_config()

    print("🔍 Диагностика структуры папок:")
    for folder_name, folder_path in [
        ("raw_data_folder", data_config.raw_data_folder),
        ("processed_folder", data_config.processed_folder),
        ("selections_folder", data_config.selections_folder),
        ("outputs_folder", data_config.outputs_folder),
    ]:
        exists = folder_path.exists()
        print(f"  {folder_name}: {folder_path} - {'✓' if exists else '✗'}")

        if exists:
            files = list(folder_path.glob("*"))
            print(f"    Файлов: {len(files)}")
            for f in files[:5]:  # покажем первые 5 файлов
                print(f"      - {f.name}")


if __name__ == "__main__":
    debug_structure()