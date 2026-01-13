from dataclasses import dataclass
from typing import Optional


@dataclass
class Database:
    database_name: str
    server: str
    port: int
    database: str
    username: str
    password: str
    dialect: str
    new: bool
    project_uid: str  # = "0"
    uid: Optional[str] = None
