from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from forloop_modules.queries.db_model_templates import UserSubscriptionPlanStatusEnum


@dataclass
class SubscriptionPlan:
    name: str
    stripe_id: str
    lookup_key: str
    price: float
    total_credits: int
    max_concurrent_pipelines: int
    max_collaborators: int
    is_active: bool
    description: str
    uid: Optional[str] = None

@dataclass
class UserSubscriptionPlan:
    user_uid: str # Foreign Key Many-to-1
    subscription_plan_uid: str # Foreign Key Many-to-1
    end_datetime_utc: datetime
    start_datetime_utc: datetime
    status: UserSubscriptionPlanStatusEnum = UserSubscriptionPlanStatusEnum.UNPAID
    consumed_credits: int = 0
    uid: Optional[str] = None

