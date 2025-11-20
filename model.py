from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import datetime

@dataclass
class Todo:
    id: Optional[int]
    task: str
    category: str
    status: int = 1             # 1=open, 2=done
    priority: str = "medium"    # low, medium, high
    due_date: Optional[str] = None   # ISO date string (YYYY-MM-DD) or None
    created_at: str = None      # ISO datetime
    date_completed: Optional[str] = None

    def __post_init__(self):
        now = datetime.datetime.utcnow().isoformat()
        if self.created_at is None:
            self.created_at = now