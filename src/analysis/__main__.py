"""
CLI для анализа импульсов: расчёт зарядов и построение гистограммы.
"""
import numpy as np
import argparse
import json
from pathlib import Path
from datetime import datetime
from src.core.config_loader import load_data_config
from src.analysis.charge_calculator import compute_all_charges
from src.analysis.histogram_plotter import plot_charge_histogram
from src.data.pulses_repository import PulsesRepository


def main():
    # Загружаем конфигурацию для правильных путей
    data_config = load_data_config()

    parser = argparse.ArgumentParser(
        description="Анализ импульсов: расчёт зарядов и построение гистограммы"
    )
    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=data_config.processed_folder / "extracted_pulses.txt",
        help="Путь к входному файлу с импульсами"
    )
    parser.add_argument(
        "-s", "--selections",
        type=Path,
        default=None,
        help="(опционально) путь к selections файлу. Если не задан, будет искаться автоматически"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Путь к выходному файлу гистограммы (по умолчанию: outputs/analysis/charge_histogram_<timestamp>.png)"
    )
    parser.add_argument(
        "--bins",
        type=int,
        default=20,
        help="Количество бинов для гистограммы (по умолчанию: 20)"
    )
    parser.add_argument(
        "--unit-scale",
        type=float,
        default=1e9,
        help="Масштаб единиц заряда (по умолчанию: 1e9 для нКл)"
    )
    parser.add_argument(
        "--unit-label",
        type=str,
        default="нКл",
        help="Метка единиц заряда (по умолчанию: 'нКл')"
    )

    args = parser.parse_args()

    # Автоматически определяем файл селекций, если не указан
    if args.selections is None:
        selections_candidate = data_config.selections_folder / f"{args.input.stem}_selections.json"
        if selections_candidate.exists():
            args.selections = selections_candidate
            print(f"📁 Используется файл селекций: {args.selections}")

    # Устанавливаем выходной путь по умолчанию
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_dir = data_config.outputs_folder / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        args.output = analysis_dir / f"charge_histogram_{timestamp}.png"

    # Проверка существования входного файла
    if not args.input.exists():
        parser.error(f"Входной файл не найден: {args.input}")
    if not args.input.is_file():
        parser.error(f"Указанный путь не является файлом: {args.input}")

    try:
        # Загружаем группу импульсов
        group = PulsesRepository.load_group(args.input, selections_path=args.selections)
        pulses = [item.pulse for item in group.pulses if item.approved]

        if not pulses:
            print("❌ Нет одобренных импульсов для анализа")
            return

        print(f"📊 Анализ {len(pulses)} импульсов из файла: {args.input.name}")

        # Вычисляем заряды
        charges = compute_all_charges(pulses)
        print(f"⚡ Рассчитаны заряды для {len(charges)} импульсов")

        # Строим гистограмму
        plot_charge_histogram(
            charges,
            save_path=args.output,
            bins=args.bins,
            unit_scale=args.unit_scale,
            unit_label=args.unit_label
        )
        print(f"📈 Гистограмма сохранена: {args.output}")

        # Сохраняем статистику в JSON
        stats_path = args.output.with_suffix(".json")
        stats = {
            "analysis_date": datetime.now().isoformat(),
            "input_file": str(args.input),
            "selections_file": str(args.selections) if args.selections else None,
            "total_pulses_analyzed": len(pulses),
            "charge_statistics": {
                "mean": float(charges.mean()),
                "std": float(charges.std()),
                "min": float(charges.min()),
                "max": float(charges.max()),
                "median": float(np.median(charges)),
                "unit": "C"
            },
            "histogram_settings": {
                "bins": args.bins,
                "unit_scale": args.unit_scale,
                "unit_label": args.unit_label,
                "output_path": str(args.output)
            }
        }

        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"📊 Статистика сохранена: {stats_path}")

        # Выводим краткую статистику
        print("\n📋 Краткая статистика:")
        print(f"   Средний заряд: {charges.mean() * args.unit_scale:.2f} {args.unit_label}")
        print(f"   Стандартное отклонение: {charges.std() * args.unit_scale:.2f} {args.unit_label}")
        print(f"   Минимальный заряд: {charges.min() * args.unit_scale:.2f} {args.unit_label}")
        print(f"   Максимальный заряд: {charges.max() * args.unit_scale:.2f} {args.unit_label}")
        print(f"   Медиана: {np.median(charges) * args.unit_scale:.2f} {args.unit_label}")

    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")
        raise


if __name__ == "__main__":
    main()