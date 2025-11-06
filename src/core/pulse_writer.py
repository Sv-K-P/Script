from pathlib import Path
from src.models.pulse_models import PulseModel

def write_pulses(pulses: list[PulseModel], output_path: Path) -> None:
    """Записывает импульсы в текстовый файл."""
    with output_path.open("w", encoding="utf-8") as f:
        f.write("time\tcurrent\tvoltage\n")
        for pulse in pulses:
            f.write("start\t\t\n")
            for t, i, v in zip(pulse.time, pulse.current, pulse.voltage):
                f.write(f"{t}\t{i}\t{v}\n")