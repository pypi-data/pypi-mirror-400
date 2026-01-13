from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from forloop_modules.queries.db_model_templates import (
    PipelineTriggerParams,
    TimeTriggerParams,
    TriggerFrequencyEnum,
    TriggerType,
)


@dataclass
class Trigger:
    name: str
    type: TriggerType
    params: Union[TimeTriggerParams, PipelineTriggerParams]
    pipeline_uid: str
    project_uid: str
    last_run_date: Optional[datetime] = None
    uid: Optional[str] = None

    def __post_init__(self):
        if self.type == TriggerType.TIME and isinstance(self.params["first_run_date"], str):
            self.params = TimeTriggerParams(
                **self.params,
                first_run_date=datetime.fromisoformat(self.params["first_run_date"]),
                frequency=TriggerFrequencyEnum(self.params["frequency"])
            )
