from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional


@dataclass
class Session:
    user_uid: str
    auth0_session_id: str  #auth0 response - session_id
    platform_type: Literal["cloud", "desktop"]  #cloud or desktop
    version: Optional[str] = None  #forloop platform version
    ip: Optional[str] = None  # only in desktop/execution core version
    mac_address: Optional[str] = None  # only in desktop/execution core version
    hostname: Optional[str] = None  # only in desktop/execution core version
    start_datetime_utc: datetime = field(default_factory=datetime.utcnow)
    last_datetime_utc: datetime = field(default_factory=datetime.utcnow)
    uid: Optional[str] = None