from pathlib import Path
import numpy as np
from src.models.pulse_models import PulseModel

def load_pulses(file_path: Path) -> list[PulseModel]:
    """Загружает импульсы из текстового файла."""
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Путь не является файлом: {file_path}")
    
    pulses: list[PulseModel] = []
    time, current, voltage = [], [], []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            next(file)  # Пропускаем заголовок
            for line_num, line in enumerate(file, start=2):
                try:
                    if line.startswith("start"):
                        if time:
                            pulses.append(PulseModel(
                                time=np.array(time),
                                current=np.array(current),
                                voltage=np.array(voltage)
                            ))
                            time, current, voltage = [], [], []
                    else:
                        parts = line.strip().split("\t")
                        if len(parts) == 3:
                            t, i, v = map(float, parts)
                            time.append(t)
                            current.append(i)
                            voltage.append(v)
                except ValueError as e:
                    raise ValueError(
                        f"Ошибка парсинга строки {line_num} в файле {file_path}: {e}"
                    ) from e
        if time:
            pulses.append(PulseModel(
                time=np.array(time),
                current=np.array(current),
                voltage=np.array(voltage)
            ))
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла {file_path}: {e}") from e
    
    return pulses

