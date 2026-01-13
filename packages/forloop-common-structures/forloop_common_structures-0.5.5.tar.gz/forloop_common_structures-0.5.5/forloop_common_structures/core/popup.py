from dataclasses import dataclass, field
from typing import ClassVar, Any, Dict, List


@dataclass
class Popup:
    pos: List[Any]
    typ: str
    params: Dict[str, Dict[str, Any]] = field(compare=False, default_factory=dict, repr=False)
    project_uid: str=""  

    uid: str = field(init=False)
    instance_counter: ClassVar[int] = 0

    def __post_init__(self):
        self.__class__.instance_counter += 1
        self.uid = str(self.instance_counter)
