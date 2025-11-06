"""
Модуль для пакетного анализа нескольких файлов с импульсами.
"""
from pathlib import Path
import json
import numpy as np
from src.core.config_loader import load_data_config
from src.data.pulses_repository import PulsesRepository
from src.analysis.charge_calculator import compute_all_charges
from src.analysis.histogram_plotter import plot_charge_histogram, plot_charge_statistics


class BatchAnalyzer:
    """Анализатор нескольких файлов с импульсами."""

    def __init__(self):
        self.data_config = load_data_config()

    def analyze_processed_files(self):
        """Анализирует все файлы в папке processed."""
        results = {}

        for txt_file in self.data_config.processed_folder.glob("*.txt"):
            print(f"🔍 Анализ файла: {txt_file.name}")

            try:
                # Пытаемся найти соответствующий файл селекций
                selections_path = self.data_config.selections_folder / f"{txt_file.stem}_selections.json"
                selections_path = selections_path if selections_path.exists() else None

                # Загружаем импульсы
                group = PulsesRepository.load_group(txt_file, selections_path)
                pulses = [item.pulse for item in group.pulses if item.approved]

                if not pulses:
                    print(f"   ⚠️  Нет одобренных импульсов")
                    continue

                # Вычисляем заряды
                charges = compute_all_charges(pulses)

                # Сохраняем результаты
                results[txt_file.name] = {
                    "file_path": str(txt_file),
                    "total_pulses": len(pulses),
                    "charge_statistics": {
                        "mean": float(np.mean(charges)),
                        "std": float(np.std(charges)),
                        "min": float(np.min(charges)),
                        "max": float(np.max(charges)),
                    }
                }

                # Создаем отдельную папку для каждого файла
                analysis_dir = self.data_config.outputs_folder / "analysis" / txt_file.stem
                analysis_dir.mkdir(parents=True, exist_ok=True)

                # Строим графики
                plot_charge_statistics(charges, analysis_dir)

                print(f"   ✅ Проанализировано {len(pulses)} импульсов")

            except Exception as e:
                print(f"   ❌ Ошибка анализа {txt_file.name}: {e}")
                continue

        # Сохраняем сводный отчет
        if results:
            summary_path = self.data_config.outputs_folder / "analysis" / "batch_analysis_summary.json"
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"📊 Сводный отчет сохранен: {summary_path}")

            # Выводим краткую статистику
            self._print_summary(results)
        else:
            print("❌ Не удалось проанализировать ни один файл")

    def _print_summary(self, results):
        """Выводит краткую сводку по анализу."""
        print("\n" + "=" * 50)
        print("📈 СВОДКА АНАЛИЗА")
        print("=" * 50)

        for filename, data in results.items():
            stats = data["charge_statistics"]
            print(f"📁 {filename}:")
            print(f"   Импульсов: {data['total_pulses']}")
            print(f"   Средний заряд: {stats['mean']:.2e} Кл")
            print(f"   Стандартное отклонение: {stats['std']:.2e} Кл")
            print()


def main():
    """Точка входа для пакетного анализа."""
    analyzer = BatchAnalyzer()
    analyzer.analyze_processed_files()


if __name__ == "__main__":
    main()