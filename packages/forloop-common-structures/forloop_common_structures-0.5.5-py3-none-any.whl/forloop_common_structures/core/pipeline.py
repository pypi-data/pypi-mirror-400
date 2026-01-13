from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pipeline:
    name: str
    start_node_uid: str = "0"
    is_active: bool = False
    system_reactivation_status: Optional[str] = None
    active_nodes_uids: list = field(default_factory=list)
    remaining_nodes_uids: list = field(default_factory=list)

    project_uid: str = "0"
    uid: Optional[str] = None

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in vars(self).keys():
                setattr(self, key, value)
            else:
                raise AttributeError(f"Attribute '{key}' cannot be updated, as it does not exist")

    def run(self):
        self.is_active = True

    def stop(self):  #todo: pause
        self.is_active = False
