from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class Screenshot:
    url: str
    screenshot: str
    prototype_job_uid: str
    uid: Optional[str] = None


@dataclass
class Elements:
    elements: Union[list[dict], dict[str, dict]]
    prototype_job_uid: str
    uid: Optional[str] = None
