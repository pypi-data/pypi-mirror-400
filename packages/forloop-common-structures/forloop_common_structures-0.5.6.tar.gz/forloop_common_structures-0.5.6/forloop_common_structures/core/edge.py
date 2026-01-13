from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Edge:
    from_node_uid: int
    to_node_uid: int
    channel: Any
    pipeline_uid: str = "0"
    project_uid: str = "0"
    visible: bool = True
    uid: Optional[str] = None

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in vars(self).keys():
                setattr(self, key, value)
            else:
                raise AttributeError(f"Attribute '{key}' cannot be updated, as it does not exist")
