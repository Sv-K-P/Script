from pathlib import Path
from src.models.config_models import DataConfigModel


class FolderStructureValidator:
    def __init__(self, data_config: DataConfigModel):
        self.data_config = data_config

    def validate_and_create_structure(self) -> bool:
        """Проверяет и создает структуру папок."""
        folders = [
            self.data_config.raw_data_folder,
            self.data_config.processed_folder,
            self.data_config.selections_folder,
            self.data_config.outputs_folder,
        ]

        all_created = True
        for folder in folders:
            try:
                folder.mkdir(parents=True, exist_ok=True)
                print(f"✓ Папка {folder} создана/проверена")
            except Exception as e:
                print(f"✗ Ошибка создания папки {folder}: {e}")
                all_created = False

        return all_created

    def check_for_files(self) -> dict:
        """Проверяет наличие файлов в папках."""
        result = {
            'raw_npz': list(self.data_config.raw_data_folder.glob("*.npz")),
            'processed_txt': list(self.data_config.processed_folder.glob("*.txt")),
            'selections_json': list(self.data_config.selections_folder.glob("*.json")),
        }
        return result