from dataclasses import dataclass, field
from typing import ClassVar, Any, Dict, List


@dataclass
class File:

    file_name: str = "default.txt"
    data: Any = None
    project_uid: str = "0"
    upload_status: str = "Not started"
    
    uid: int = field(init=False)
    instance_counter: ClassVar[int] = 0

    def __post_init__(self):
        self.__class__.instance_counter += 1
        self.uid = str(self.instance_counter)
        self.path = "./tmp/" + self.file_name
