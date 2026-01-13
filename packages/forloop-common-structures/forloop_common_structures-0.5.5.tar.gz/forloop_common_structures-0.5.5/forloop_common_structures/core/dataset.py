from dataclasses import dataclass, field
from typing import ClassVar, Any, Dict, List


@dataclass
class Dataset:
    
    dataset_name: str=""
    data: Any=None
    project_uid: int=0
    
    uid: str = field(init=False)
    instance_counter: ClassVar[int] = 0


    def __post_init__(self):
        self.__class__.instance_counter += 1
        self.uid = str(self.instance_counter)
        
