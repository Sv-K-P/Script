from src.core.config_loader import load_data_config


def check_structure():
    data_config = load_data_config()

    print("📁 Проверка структуры папок:")

    folders = [
        ("Исходные данные", data_config.raw_data_folder),
        ("Обработанные импульсы", data_config.processed_folder),
        ("Файлы селекций", data_config.selections_folder),
        ("Одобренные импульсы", data_config.outputs_folder / data_config.approved_subfolder),
        ("Графики валидации", data_config.outputs_folder / data_config.validation_subfolder),
    ]

    for name, path in folders:
        exists = path.exists()
        print(f"  {name}: {path} - {'✓' if exists else '✗'}")

        if exists:
            files = list(path.glob("*"))
            print(f"    Файлов: {len(files)}")
            for f in files[:3]:  # покажем первые 3 файла
                print(f"      - {f.name}")
            if len(files) > 3:
                print(f"      ... и еще {len(files) - 3} файлов")


if __name__ == "__main__":
    check_structure()