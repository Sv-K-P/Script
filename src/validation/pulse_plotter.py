"""
Модуль для визуализации импульсов.
"""
import matplotlib.pyplot as plt
from pathlib import Path
from src.models.pulse_models import PulseModel
from typing import Sequence
from src.validation.pulse_mask import apply_pulse_mask
from src.models.pulse_group_models import PulseItem


def plot_pulses(pulses: list[PulseModel], save_dir: Path | None = None, mask: Sequence[bool] | None = None) -> None:

    # Применяем маску, если она задана
    items = [PulseItem(pulse=p, approved=True) for p in pulses]
    if mask is not None:
        items = apply_pulse_mask(items, list(mask))

    for idx, item in enumerate(items, start=1):
        p = item.pulse
        fig, ax1 = plt.subplots()
        ax1.set_title(f"Pulse #{idx}")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Current (A)", color="tab:blue")
        ax1.plot(p.time, p.current, color="tab:blue", label="Current")
        ax2 = ax1.twinx()
        ax2.set_ylabel("Voltage (V)", color="tab:red")
        ax2.plot(p.time, p.voltage, color="tab:red", linestyle="--", label="Voltage")

        fig.tight_layout()

        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
            path = save_dir / f"pulse_{idx:03d}.png"
            fig.savefig(path)
            plt.close(fig)

        else:
            plt.show()