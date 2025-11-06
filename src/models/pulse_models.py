from __future__ import annotations

from typing import Annotated

import numpy as np
from pydantic import BaseModel, Field, ConfigDict, model_validator


class PulseModel(BaseModel):
    time: Annotated[np.ndarray, Field(description="Массив времени импульса")]
    current: Annotated[np.ndarray, Field(description="Массив тока импульса")]
    voltage: Annotated[np.ndarray, Field(description="Массив напряжения импульса")]
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_default=True
    )

    @model_validator(mode="after")
    def validate_array_lengths(self):
        """Проверяет, что все массивы имеют одинаковую длину."""
        lengths = [len(self.time), len(self.current), len(self.voltage)]
        if len(set(lengths)) > 1:
            raise ValueError(
                f"Массивы имеют разную длину: time={lengths[0]}, "
                f"current={lengths[1]}, voltage={lengths[2]}"
            )
        if lengths[0] == 0:
            raise ValueError("Массивы не могут быть пустыми")
        return self



