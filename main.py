
from pathlib import Path
from src.core.config_loader import load_config, load_selections, load_data_config
from src.core.pulse_extractor import extract_all_pulses
from src.core.pulse_writer import write_pulses


def main():
    # Загружаем новую конфигурацию данных
    data_config = load_data_config()

    # Загружаем конфиг извлечения и селекции
    config = load_config(Path("configs/extraction_config.json"))
    selections = load_selections(data_config.selections_folder)

    # Извлекаем импульсы
    pulses = extract_all_pulses(config, selections)

    # Сохраняем в правильную папку
    output_path = data_config.processed_folder / config.output_file
    write_pulses(pulses, output_path)

    print(f"Успешно извлечено {len(pulses)} импульсов в {output_path}")


if __name__ == "__main__":
    main()