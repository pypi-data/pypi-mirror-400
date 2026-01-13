from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    email: str
    auth0_subject_id: str
    stripe_id: str
    given_name: str
    family_name: str
    picture_url: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    uid: Optional[str] = None
