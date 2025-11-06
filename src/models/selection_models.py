from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel, Field, model_validator


class SelectionEntryModel(BaseModel):
    start_index: Annotated[int, Field(ge=0, description="Начальный индекс импульса")]
    end_index: Annotated[int, Field(ge=0, description="Конечный индекс импульса")]

    @model_validator(mode="after")
    def check_order(self):
        if self.end_index <= self.start_index:
            self.end_index, self.start_index = self.start_index, self.end_index
        return self


class SelectionModel(BaseModel):
    file_name: Annotated[str, Field(min_length=1, description="Имя файла .npz")]
    batch_size: Annotated[int, Field(ge=0, description="Размер пакета обработки")]
    overlap_size: Annotated[int, Field(ge=0, description="Размер перекрытия")]
    selections: Annotated[list[SelectionEntryModel], Field(min_length=1, description="Список импульсов")]

