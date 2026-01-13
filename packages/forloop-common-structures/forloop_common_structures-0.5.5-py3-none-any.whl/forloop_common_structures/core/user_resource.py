from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional


class UserResourceTypeEnum(str, Enum):
    def __str__(self):
        return self.value

    MYSQL_SHARED_DB = 'MySQL_Shared'
    MYSQL_DEDICATED_DB = 'MySQL_Dedicated'


@dataclass(frozen=True)
class UserResource:
    user_uid: str
    resource_type: UserResourceTypeEnum
    resource_name: str
    created_at: datetime = field(default_factory=datetime.now)
    removed_at: Optional[datetime] = None
    uid: Optional[str] = None

    def mark_as_removed(self):
        object.__setattr__(self, 'removed_at', datetime.now())

    def to_dict(self) -> dict:
        return asdict(self)
