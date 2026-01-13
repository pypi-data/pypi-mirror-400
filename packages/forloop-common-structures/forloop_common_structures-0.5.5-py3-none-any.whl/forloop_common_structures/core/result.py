from dataclasses import dataclass
from numbers import Number
from typing import Optional, Union

import pandas as pd

VariableValueTypes = Union[str, Number, pd.DataFrame, list, dict]


@dataclass
class Result:
    """Class containing Dataframes, Lists, Dicts (JSON) - objects visible and possible to manipulate."""

    name: str
    value: VariableValueTypes
    pipeline_job_uid: str
    type: Optional[str] = None
    size: Optional[int] = None
    uid: Optional[str] = None

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in vars(self).keys():
                setattr(self, key, value)
            else:
                raise AttributeError(f"Attribute '{key}' cannot be updated, as it does not exist")
