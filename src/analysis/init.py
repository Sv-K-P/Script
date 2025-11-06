"""
Модуль анализа импульсов - расчет зарядов, построение гистограмм и статистика.
"""

from src.analysis.charge_calculator import compute_charge, compute_all_charges
from src.analysis.histogram_plotter import plot_charge_histogram
from src.analysis.batch_analyzer import BatchAnalyzer

__all__ = [
    'compute_charge',
    'compute_all_charges',
    'plot_charge_histogram',
    'BatchAnalyzer'
]