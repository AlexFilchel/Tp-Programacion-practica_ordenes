from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Orden(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str
    total_amount: float = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)