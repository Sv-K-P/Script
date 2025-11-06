import warnings
import numpy as np
from pathlib import Path
from src.models.config_models import ConfigModel
from src.models.selection_models import SelectionModel
from src.models.pulse_models import PulseModel


def extract_pulses_from_file(file_path: Path, selection: SelectionModel) -> list[PulseModel]:
    print(f"🔧 Извлечение из файла: {file_path.name}")
    print(f"   Селекции: {len(selection.selections)} записей")

    try:
        with np.load(file_path) as npz:
            if "data" not in npz:
                print(f"   ❌ Ключ 'data' не найден в файле {file_path}")
                raise KeyError(f"Ключ 'data' не найден в файле {file_path}")

            t, v, i = npz["data"]
            print(f"   Данные загружены: время={len(t)}, напряжение={len(v)}, ток={len(i)}")

            pulses: list[PulseModel] = []
            valid_selections = 0

            for idx, s in enumerate(selection.selections):
                start, end = s.start_index, s.end_index + 1

                # Полная валидация границ массива
                if start < 0 or start >= len(t) or end > len(t) or start >= end:
                    print(f"   ⚠️  Пропуск селекции {idx}: неверные границы {start}-{end} (данные: 0-{len(t)})")
                    continue

                t_rel = t[start:end]
                pulse = PulseModel(time=t_rel, current=i[start:end], voltage=v[start:end])
                pulses.append(pulse)
                valid_selections += 1
                print(f"   ✅ Селекция {idx}: {start}-{end} -> импульс {len(t_rel)} точек")

            print(f"   📊 Извлечено импульсов: {valid_selections}/{len(selection.selections)}")
            return pulses

    except Exception as e:
        print(f"   ❌ Ошибка при обработке файла {file_path}: {e}")
        raise


def extract_all_pulses(config: ConfigModel, selections: list[SelectionModel]) -> list[PulseModel]:
    print("🚀 Начало извлечения всех импульсов")
    all_pulses: list[PulseModel] = []
    base = config.data_folder

    print(f"📁 Базовая папка: {base}")
    print(f"📋 Всего селекций: {len(selections)}")

    for s_idx, s in enumerate(selections):
        file_path = base / s.file_name  # Используем имя файла из селекции
        print(f"\n📄 Обработка селекции {s_idx}: {s.file_name}")
        print(f"   Полный путь: {file_path}")

        if not file_path.exists():
            warnings.warn(f"Файл не найден и пропущен: {file_path}", UserWarning)
            print(f"   ❌ Файл не существует: {file_path}")
            continue

        try:
            pulses_from_file = extract_pulses_from_file(file_path, s)
            all_pulses.extend(pulses_from_file)
            print(f"   ✅ Добавлено {len(pulses_from_file)} импульсов")
        except Exception as e:
            print(f"   ❌ Ошибка при извлечении из {file_path}: {e}")
            continue

    print(f"\n🎉 ИТОГО: Извлечено {len(all_pulses)} импульсов")
    return all_pulses

