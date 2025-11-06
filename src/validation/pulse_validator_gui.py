"""
Главное окно PyQt приложения для валидации импульсов.
"""
import json
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QColor
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QMessageBox,
    QFileDialog,
    QStatusBar,
    QSplitter,
)

from src.core.config_loader import load_data_config
from src.data.pulses_repository import PulsesRepository
from src.models.config_models import DataConfigModel
from src.validation.ui.widgets.pulse_plot_widget import PulsePlotWidget
from src.models.pulse_models import PulseModel
from src.core.pulse_writer import write_pulses
from src.models.pulse_group_models import PulseGroupModel, PulseItem
from src.validation.pulse_mask import apply_pulse_mask


class PulseValidatorMainWindow(QMainWindow):
    """Главное окно приложения для валидации импульсов."""

    def __init__(self, data_config: DataConfigModel | None = None) -> None:
        super().__init__()
        self.data_config = data_config or load_data_config()

        self.setWindowTitle("Валидатор импульсов")
        self.setGeometry(100, 100, 1200, 700)

        # Данные: {file_path: PulseGroupModel}
        self.pulse_data: dict[Path, PulseGroupModel] = {}
        # Необязательные внешние маски по файлу (bool-списки)
        self.mask_by_file: dict[Path, list[bool]] = {}

        # Текущий выбранный импульс
        self.current_file: Optional[Path] = None
        self.current_pulse_index: Optional[int] = None

        self._setup_ui()
        self._setup_shortcuts()
        self._auto_load_files()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Дерево файлов и импульсов слева
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Файлы и импульсы")
        self.tree_widget.setColumnCount(1)
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree_widget.itemDoubleClicked.connect(self._on_double_click)
        splitter.addWidget(self.tree_widget)

        # Виджет графика справа
        self.plot_widget = PulsePlotWidget()
        splitter.addWidget(self.plot_widget)

        # Статус-бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")

        # Простое меню через кнопки в статус-баре (без QMenuBar для компактности)
        open_btn = self.status_bar.addPermanentWidget(QWidget())
        # Используем сочетания клавиш для открытия/сохранения

    def _setup_shortcuts(self) -> None:
        """Настройка горячих клавиш."""
        # Ctrl+O — открыть файлы
        o_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        o_shortcut.activated.connect(self._open_files)

        # Ctrl+S — сохранить одобренные
        s_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        s_shortcut.activated.connect(self._save_approved)

        # Q — предыдущий импульс
        prev_shortcut = QShortcut(QKeySequence("Q"), self)
        prev_shortcut.activated.connect(self._prev_pulse)

        # E — следующий импульс
        next_shortcut = QShortcut(QKeySequence("E"), self)
        next_shortcut.activated.connect(self._next_pulse)

        # Пробел — переключить одобрение
        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self._toggle_current_approval)

    def _open_files(self) -> None:
        """Открыть диалог выбора файлов и загрузить все выбранные файлы."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите файлы с импульсами",
            "",
            "Text Files (*.txt);;All Files (*)",
        )
        if not file_paths:
            return

        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            try:
                # Загружаем группу с авто-применением selections, если лежит рядом
                group = PulsesRepository.load_group(file_path)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка загрузки", f"{file_path.name}: {e}")
                continue

            if not group.pulses:
                continue

            self.pulse_data[file_path] = group
            self._add_file_to_tree(file_path)

        if self.pulse_data:
            self.status_bar.showMessage(f"Загружено файлов: {len(self.pulse_data)}")
            self._select_first_pulse()

    def _add_file_to_tree(self, file_path: Path) -> None:
        """Добавить файл и его импульсы в дерево."""
        file_item = QTreeWidgetItem(self.tree_widget)
        file_item.setText(0, file_path.name)
        file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)

        group = self.pulse_data[file_path]
        for idx, item in enumerate(group.pulses):
            pulse_item = QTreeWidgetItem(file_item)
            pulse_item.setText(0, f"Импульс {idx + 1}")
            pulse_item.setData(0, Qt.ItemDataRole.UserRole, (file_path, idx))
            self._update_item_appearance(pulse_item, item.approved)

        file_item.setExpanded(True)

    def _update_item_appearance(self, item: QTreeWidgetItem, is_approved: bool) -> None:
        """Обновить внешний вид элемента дерева в зависимости от статуса одобрения."""
        if is_approved:
            item.setForeground(0, QColor("green"))
            text = item.text(0).replace(" [✗]", "")
            if " [✓]" not in text:
                text += " [✓]"
            item.setText(0, text)
        else:
            item.setForeground(0, QColor("red"))
            text = item.text(0).replace(" [✓]", "")
            if " [✗]" not in text:
                text += " [✗]"
            item.setText(0, text)

    def _on_selection_changed(self) -> None:
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        data = item.data(0, Qt.ItemDataRole.UserRole)

        # Если выбран файл — ничего не делаем
        if isinstance(data, Path):
            return

        # Если выбран импульс
        if isinstance(data, tuple):
            file_path, pulse_index = data
            self._show_pulse(file_path, pulse_index)

    def _on_double_click(self, item: QTreeWidgetItem, column: int) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple):
            file_path, pulse_index = data
            self._toggle_approval_at(file_path, pulse_index)

    def _show_pulse(self, file_path: Path, pulse_index: int) -> None:
        if file_path not in self.pulse_data:
            return
        group = self.pulse_data[file_path]
        if pulse_index >= len(group.pulses):
            return

        pulse = group.pulses[pulse_index].pulse
        self.current_file = file_path
        self.current_pulse_index = pulse_index

        is_approved = group.pulses[pulse_index].approved
        self.plot_widget.plot_pulse(pulse, pulse_index + 1, is_approved)

        total_pulses = len(group.pulses)
        approved_count = sum(1 for it in group.pulses if it.approved)
        self.status_bar.showMessage(
            f"Файл: {file_path.name} | Импульс {pulse_index + 1}/{total_pulses} | Одобрено: {approved_count}/{total_pulses}"
        )

    def _toggle_current_approval(self) -> None:
        if self.current_file is None or self.current_pulse_index is None:
            return
        self._toggle_approval_at(self.current_file, self.current_pulse_index)

    def _toggle_approval_at(self, file_path: Path, pulse_index: int) -> None:
        if file_path not in self.pulse_data:
            return
        group = self.pulse_data[file_path]
        if pulse_index >= len(group.pulses):
            return
        group.pulses[pulse_index].approved = not group.pulses[pulse_index].approved

        # Найти элемент в дереве
        file_item = None
        for i in range(self.tree_widget.topLevelItemCount()):
            top_item = self.tree_widget.topLevelItem(i)
            if top_item.data(0, Qt.ItemDataRole.UserRole) == file_path:
                file_item = top_item
                break
        if file_item is None:
            return

        pulse_item = file_item.child(pulse_index)
        if pulse_item is None:
            return

        self._update_item_appearance(pulse_item, group.pulses[pulse_index].approved)

        # Обновить график, если это текущий
        if self.current_file == file_path and self.current_pulse_index == pulse_index:
            self.plot_widget.plot_pulse(
                group.pulses[pulse_index].pulse,
                pulse_index + 1,
                group.pulses[pulse_index].approved,
            )

        total_pulses = len(group.pulses)
        approved_count = sum(1 for it in group.pulses if it.approved)
        self.status_bar.showMessage(
            f"Файл: {file_path.name} | Импульс {pulse_index + 1}/{total_pulses} | Одобрено: {approved_count}/{total_pulses}"
        )

    def _next_pulse(self) -> None:
        if not self.pulse_data or self.current_file is None or self.current_pulse_index is None:
            return

        files = list(self.pulse_data.keys())
        try:
            file_index = files.index(self.current_file)
        except ValueError:
            return

        next_pulse_index = self.current_pulse_index + 1
        group = self.pulse_data[self.current_file]
        if next_pulse_index < len(group.pulses):
            self._select_pulse(self.current_file, next_pulse_index)
        elif file_index + 1 < len(files):
            next_file = files[file_index + 1]
            # переходим к следующему файлу только если в нём есть импульсы
            if len(self.pulse_data[next_file].pulses) > 0:
                self._select_pulse(next_file, 0)

    def _prev_pulse(self) -> None:
        if not self.pulse_data or self.current_file is None or self.current_pulse_index is None:
            return

        prev_pulse_index = self.current_pulse_index - 1
        if prev_pulse_index >= 0:
            self._select_pulse(self.current_file, prev_pulse_index)
        else:
            files = list(self.pulse_data.keys())
            try:
                file_index = files.index(self.current_file)
            except ValueError:
                return
            if file_index > 0:
                prev_file = files[file_index - 1]
                last_index = len(self.pulse_data[prev_file].pulses) - 1
                if last_index >= 0:
                    self._select_pulse(prev_file, last_index)

    def _select_pulse(self, file_path: Path, pulse_index: int) -> None:
        # Найти файл в дереве
        file_item = None
        for i in range(self.tree_widget.topLevelItemCount()):
            top_item = self.tree_widget.topLevelItem(i)
            if top_item.data(0, Qt.ItemDataRole.UserRole) == file_path:
                file_item = top_item
                break
        if file_item is None:
            return

        pulse_item = file_item.child(pulse_index)
        if pulse_item is None:
            return

        self.tree_widget.setCurrentItem(pulse_item)
        file_item.setExpanded(True)
        self._show_pulse(file_path, pulse_index)

    def _select_first_pulse(self) -> None:
        if not self.pulse_data:
            return
        first_file = list(self.pulse_data.keys())[0]
        self._select_pulse(first_file, 0)

    def _save_approved(self) -> None:
        if not self.pulse_data:
            QMessageBox.information(self, "Информация", "Нет данных для сохранения")
            return

        approved_pulses: list[PulseModel] = []
        metadata: list[dict] = []
        for file_path, group in self.pulse_data.items():
            for idx, item in enumerate(group.pulses):
                if item.approved:
                    approved_pulses.append(item.pulse)
                    metadata.append({
                        "file": str(file_path),
                        "pulse_index": idx,
                        "original_index": idx + 1,
                    })
        if not approved_pulses:
            QMessageBox.information(self, "Информация", "Нет одобренных импульсов для сохранения")
            return

        # Используем правильные пути из конфигурации
        default_dir = self.data_config.outputs_folder / "approved"
        default_dir.mkdir(parents=True, exist_ok=True)

        # Автоматическое имя файла с временной меткой
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"approved_pulses_{timestamp}.txt"

        output_path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить одобренные импульсы",
            str(default_dir / default_filename),
            "Text Files (*.txt);;All Files (*)",
        )
        if not output_path_str:
            return
        output_path = Path(output_path_str)

        try:
            write_pulses(approved_pulses, output_path)

            # Сохраняем метаданные в ту же папку
            metadata_path = output_path.with_suffix(".json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "source_file": str(output_path),
                        "total_approved": len(approved_pulses),
                        "pulses": metadata,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Сохраняем selections для каждого исходного файла в правильные папки
            try:
                for fpath, group in self.pulse_data.items():
                    # Сохраняем selections рядом с исходными файлами
                    selections_path = PulsesRepository.default_selections_path(fpath)
                    PulsesRepository.write_selections_for_group(fpath, group)
            except Exception as save_e:
                QMessageBox.warning(self, "Предупреждение", f"Не удалось сохранить selections: {save_e}")

            QMessageBox.information(
                self,
                "Успех",
                f"Сохранено {len(approved_pulses)} импульсов в: {output_path}\n"
                f"Метаданные: {metadata_path}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

    # Утилита для применения bool-маски к группе и обновления дерева (без UI)
    def _apply_mask_to_group(self, file_path: Path, mask: list[bool]) -> None:
        if file_path not in self.pulse_data:
            return
        group = self.pulse_data[file_path]
        items = apply_pulse_mask(group.pulses, mask)
        group.pulses = items
        # Перестроить ветку файла
        # Удаляем и заново добавляем
        for i in range(self.tree_widget.topLevelItemCount()):
            top_item = self.tree_widget.topLevelItem(i)
            if top_item.data(0, Qt.ItemDataRole.UserRole) == file_path:
                self.tree_widget.takeTopLevelItem(i)
                break
        self._add_file_to_tree(file_path)

    def _auto_load_files(self) -> None:
        """Автоматическая загрузка всех файлов из configured folders."""
        try:
            self.pulse_data = PulsesRepository.auto_discover_files(self.data_config)
            for file_path in self.pulse_data.keys():
                self._add_file_to_tree(file_path)

            if self.pulse_data:
                self.status_bar.showMessage(f"Автоматически загружено файлов: {len(self.pulse_data)}")
                self._select_first_pulse()
            else:
                self.status_bar.showMessage("Файлы не найдены. Используйте Ctrl+O для загрузки вручную.")

        except Exception as e:
            QMessageBox.warning(self, "Ошибка авто-загрузки", f"{e}")
