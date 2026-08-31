from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

DEMO_ANCHOR_DATE = date(2026, 8, 31)

@dataclass(frozen=True)
class DemoClock:
    anchor: date = DEMO_ANCHOR_DATE
    @property
    def now(self): return datetime.combine(self.anchor, time(12))
    def days_ago(self, days, hour=9): return datetime.combine(self.anchor - timedelta(days=days), time(hour))
