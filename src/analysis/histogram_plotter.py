import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# Константы для оформления гистограммы (старый дизайн)
X_AXIS_MARGIN_RATIO = 0.05  # Запас по оси X (5% с каждой стороны)
HISTOGRAM_RWIDTH = 0.9  # Ширина столбцов гистограммы относительно бина
STATS_TEXT_X_POS = 0.98  # Позиция текста статистики по X (относительно)
STATS_TEXT_Y_POS = 0.95  # Позиция текста статистики по Y (относительно)


def plot_charge_histogram(
        charges: np.ndarray,
        save_path: Path | None = None,
        bins: int = 20,
        unit_scale: float = 1e9,  # переводим в нКл
        unit_label: str = "нКл",
        align: str = "mid"
) -> None:
    """Построение гистограммы распределения зарядов с оформлением по ГОСТ."""
    if charges.size == 0:
        raise ValueError("Массив зарядов не может быть пустым")

    # Масштабируем
    charges_scaled = charges * unit_scale

    # Определяем границы по оси X с учетом отрицательных значений
    # Добавляем небольшой запас по обе стороны
    data_range = charges_scaled.max() - charges_scaled.min()
    x_min = charges_scaled.min() - X_AXIS_MARGIN_RATIO * data_range
    x_max = charges_scaled.max() + X_AXIS_MARGIN_RATIO * data_range

    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    # Создаем бины вручную для точного контроля
    bin_edges = np.linspace(x_min, x_max, bins + 1)

    counts, edges, patches = ax.hist(
        charges_scaled,
        bins=bin_edges,  # используем специально созданные бины
        density=True,  # ВКЛЮЧАЕМ относительные частоты!
        color="white",  # заливка белая (по ГОСТ – нейтральные цвета)
        edgecolor="black",
        linewidth=0.7,
        align=align,
        rwidth=HISTOGRAM_RWIDTH
    )

    # Оформление осей
    ax.set_xlim(left=x_min, right=x_max)
    ax.set_xlabel(f"Заряд ({unit_label})", fontsize=10)
    ax.set_ylabel("Частота", fontsize=10)

    # Устанавливаем деления по центрам бинов
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    ax.set_xticks(bin_centers)

    # Форматируем подписи делений
    ax.set_xticklabels([f"{x:.2f}" for x in bin_centers], rotation=45)

    ax.grid(True, linestyle="--", linewidth=0.4, color="grey", alpha=0.6)
    ax.tick_params(labelsize=9)

    # Название графика
    ax.set_title("Распределение зарядов импульсов", fontsize=12, pad=10)

    # Статистика
    mean_q = np.mean(charges_scaled)
    std_q = np.std(charges_scaled)
    stats_text = f"Среднее = {mean_q:.2f} {unit_label}\nσ = {std_q:.2f} {unit_label}"
    ax.text(
        STATS_TEXT_X_POS, STATS_TEXT_Y_POS, stats_text,
        transform=ax.transAxes,
        ha="right", va="top",
        fontsize=9, color="black",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.5)
    )

    fig.tight_layout()

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()