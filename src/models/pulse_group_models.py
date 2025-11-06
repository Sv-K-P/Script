from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field
from src.models.pulse_models import PulseModel


class PulseItem(BaseModel):
    pulse: PulseModel
    approved: bool = Field(default=True, description="Разрешён ли импульс для анализа (bool-маска)")


class PulseGroupModel(BaseModel):
    file_name: str
    pulses: List[PulseItem]


