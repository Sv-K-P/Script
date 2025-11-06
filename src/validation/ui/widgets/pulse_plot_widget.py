"""
Виджет для отображения графика импульса с использованием matplotlib.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.models.pulse_models import PulseModel


class PulsePlotWidget(QWidget):
    """Виджет для отображения графика импульса."""

    def __init__(self):
        super().__init__()

        # Создать фигуру matplotlib
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        # Настройка layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # Создать оси
        self.ax1 = self.figure.add_subplot(111)
        self.ax2 = None  # Вторая ось Y для напряжения

    def plot_pulse(self, pulse: PulseModel, pulse_number: int, is_approved: bool) -> None:
        """Построить график импульса."""
        # Очистить предыдущий график
        self.ax1.clear()
        if self.ax2 is not None:
            self.ax2.remove()
            self.ax2 = None

        # Настроить первую ось (ток)
        self.ax1.set_xlabel("Время (с)", fontsize=10)
        self.ax1.set_ylabel("Ток (А)", color="tab:blue", fontsize=10)
        self.ax1.plot(pulse.time, pulse.current, color="tab:blue", label="Ток", linewidth=1.5)
        self.ax1.tick_params(axis="y", labelcolor="tab:blue")
        self.ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)

        # Вторая ось (напряжение)
        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel("Напряжение (В)", color="tab:red", fontsize=10)
        self.ax2.plot(pulse.time, pulse.voltage, color="tab:red", linestyle="--", label="Напряжение", linewidth=1.5)
        self.ax2.tick_params(axis="y", labelcolor="tab:red")

        # Заголовок с информацией о статусе
        status_text = "✓ Одобрен" if is_approved else "✗ Отклонен"
        status_color = "green" if is_approved else "red"
        self.ax1.set_title(
            f"Импульс #{pulse_number} — {status_text}",
            fontsize=12,
            color=status_color,
            fontweight="bold",
        )

        # Легенда
        lines1, labels1 = self.ax1.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        self.ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

        # Улучшить внешний вид
        self.figure.tight_layout()

        # Обновить canvas
        self.canvas.draw()


