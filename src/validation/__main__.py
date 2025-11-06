import argparse
import sys
from pathlib import Path

from src.core.config_loader import load_data_config
from src.validation.folder_validator import FolderStructureValidator
from src.validation.pulse_loader import load_pulses
from src.validation.pulse_plotter import plot_pulses


def validate_structure() -> bool:
    """Проверяет и создает структуру папок."""
    data_config = load_data_config()
    validator = FolderStructureValidator(data_config)

    if not validator.validate_and_create_structure():
        print("❌ Ошибка при создании структуры папок")
        return False

    files = validator.check_for_files()

    print("\n📁 Структура файлов:")
    print(f"  .npz файлов в raw: {len(files['raw_npz'])}")
    print(f"  .txt файлов в processed: {len(files['processed_txt'])}")
    print(f"  .json файлов селекций: {len(files['selections_json'])}")

    return True


def main_cli() -> None:
    """CLI режим - старая функциональность."""
    # Загружаем конфигурацию для правильных путей
    from src.core.config_loader import load_data_config
    data_config = load_data_config()

    parser = argparse.ArgumentParser(
        description="Визуализация импульсов из текстового файла"
    )
    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=data_config.processed_folder / "pulses.txt",
        help="Путь к входному файлу с импульсами",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Директория для сохранения графиков (по умолчанию: outputs/validation)",
    )

    args = parser.parse_args()

    # Если выходная директория не указана, используем стандартную
    if args.output is None:
        args.output = data_config.outputs_folder / "validation"
        args.output.mkdir(parents=True, exist_ok=True)

    # Проверка существования входного файла
    if not args.input.exists():
        parser.error(f"Входной файл не найден: {args.input}")
    if not args.input.is_file():
        parser.error(f"Указанный путь не является файлом: {args.input}")

    pulses = load_pulses(args.input)
    plot_pulses(pulses, save_dir=args.output)


def main_gui() -> None:
    """GUI режим - запуск PyQt приложения."""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.validation.pulse_validator_gui import PulseValidatorMainWindow
    except ImportError:
        print("Ошибка: PyQt6 не установлен. Установите: pip install PyQt6")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = PulseValidatorMainWindow()
    window.show()
    sys.exit(app.exec())


def main() -> None:
    """Главная функция с выбором режима работы."""
    parser = argparse.ArgumentParser(description="Валидация и визуализация импульсов")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Запустить GUI приложение",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Запустить в CLI режиме (старая функциональность)",
    )

    args, unknown_args = parser.parse_known_args()

    # Если указан --cli или есть дополнительные аргументы, запускаем CLI
    if args.cli or unknown_args:
        if unknown_args:
            # Передаем неизвестные аргументы в CLI режим
            sys.argv = [sys.argv[0]] + unknown_args
        main_cli()
    else:
        # По умолчанию запускаем GUI
        main_gui()


if __name__ == "__main__":
    main()