from dataclasses import dataclass
from numbers import Number
from typing import Optional, Union

import pandas as pd

VariableValueTypes = Union[str, Number, pd.DataFrame, list, dict]


@dataclass
class Variable:
    """Class containing Dataframes, Lists, Dicts (JSON) - objects visible and possible to manipulate."""

    name: str
    value: VariableValueTypes
    type: Optional[str] = None
    size: Union[int, tuple, None] = None
    is_result: bool = False
    pipeline_job_uid: str = "0"
    project_uid: str = "0"
    uid: Optional[str] = None

    def __post_init__(self) -> None:
        if self.type is None:
            self.type = type(self.value).__name__

        if self.size is None:
            try:
                self.size = len(self.value)
            except TypeError:
                self.size = 1

    def __str__(self) -> str:
        return f"{self.value}"

    # Misleading repr looking like a simple data type when debugging
    # retained as the Platform might depend on it
    def __repr__(self) -> str:
        return f"{self.value}"

    def __len__(self) -> int:
        return self.size

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in vars(self).keys():
                setattr(self, key, value)
            else:
                raise AttributeError(f"Attribute '{key}' cannot be updated, as it does not exist")
