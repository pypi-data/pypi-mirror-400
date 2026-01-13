from __future__ import annotations

from typing import Annotated, Literal, Union

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, Field

__all__ = [
    "OutputTransform",
    "OutputTransformUnion",
    "UnityOutputTransform",
    "LogisticOutputTransform",
    "ScaleOutputTransform",
]


class OutputTransform(BaseModel):
    def __call__(self, x: Union[float, NDArray[np.float_]]) -> Union[float, NDArray[np.float_]]:
        raise NotImplementedError()


class UnityOutputTransform(OutputTransform):
    type: Literal["UnityOutputTransform"] = "UnityOutputTransform"

    def __call__(self, x: Union[float, NDArray[np.float_]]) -> Union[float, NDArray[np.float_]]:
        return x


class LogisticOutputTransform(OutputTransform):
    type: Literal["LogisticOutputTransform"] = "LogisticOutputTransform"
    steepness: float
    centre: float
    scale: float

    def __call__(self, x: Union[float, NDArray[np.float_]]) -> Union[float, NDArray[np.float_]]:
        return self.scale * (1.0 / (1.0 + np.exp(-self.steepness * (x - self.centre))))


class ScaleOutputTransform(OutputTransform):
    type: Literal["ScaleOutputTransform"] = "ScaleOutputTransform"
    scale_factor: float = 1.0

    def __call__(self, x: Union[float, NDArray[np.float_]]) -> Union[float, NDArray[np.float_]]:
        return x * self.scale_factor


OutputTransformUnion = Annotated[
    Union[UnityOutputTransform, LogisticOutputTransform, ScaleOutputTransform],
    Field(discriminator="type"),  # discriminator on the *field*, not on the models
]
