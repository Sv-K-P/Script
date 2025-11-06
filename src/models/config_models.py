from __future__ import annotations
from pathlib import Path
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from src.core.project_root import PROJECT_ROOT


class ConfigModel(BaseModel):
    data_folder: Annotated[Path, Field(alias="data_folder_path", description="Путь к папке с .npz файлами")]
    output_file: Annotated[Path, Field(default=Path("pulses.txt"), description="Имя файла для записи импульсов")]

    model_config = ConfigDict(populate_by_name=True, validate_default=True)

    @field_validator("data_folder", mode="before")
    @classmethod
    def validate_data_folder(cls, v):
        path = Path(v)
        if not path.exists():
            raise FileNotFoundError(f"Путь не существует: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Путь не является директорией: {path}")
        return path


class DataConfigModel(BaseModel):
    raw_data_folder: Path = Field(default=PROJECT_ROOT / "data/raw", description="Папка с исходными .npz файлами")
    processed_folder: Path = Field(default=PROJECT_ROOT / "data/processed",
                                   description="Папка для обработанных импульсов")
    selections_folder: Path = Field(default=PROJECT_ROOT / "data/selections", description="Папка для файлов селекций")
    outputs_folder: Path = Field(default=PROJECT_ROOT / "outputs", description="Корневая папка для результатов")
    approved_subfolder: Path = Field(default=Path("approved"), description="Подпапка для одобренных импульсов")
    validation_subfolder: Path = Field(default=Path("validation"), description="Подпапка для графиков валидации")
    analysis_subfolder: Path = Field(default=Path("analysis"), description="Подпапка для результатов анализа")

    model_config = ConfigDict(validate_default=True)

    @field_validator("raw_data_folder", "processed_folder", "selections_folder", "outputs_folder", mode="before")
    @classmethod
    def validate_and_create_folders(cls, v):
        path = Path(v)
        # Если путь относительный, делаем его абсолютным относительно корня проекта
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        path.mkdir(parents=True, exist_ok=True)
        return path

    @model_validator(mode="after")
    def create_subfolders(self):
        """Создает все необходимые подпапки."""
        (self.outputs_folder / self.approved_subfolder).mkdir(parents=True, exist_ok=True)
        (self.outputs_folder / self.validation_subfolder).mkdir(parents=True, exist_ok=True)
        (self.outputs_folder / self.analysis_subfolder).mkdir(parents=True, exist_ok=True)
        return self