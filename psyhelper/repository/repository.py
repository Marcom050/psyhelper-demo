from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from psyhelper.domain.models import *


def _json(value):
    if isinstance(value, (datetime, date)): return value.isoformat()
    if isinstance(value, StrEnum): return value.value
    raise TypeError(type(value).__name__)


class DemoRepository:
    """Small SQLite repository; domain objects never leak SQL into the UI."""
    def __init__(self, path: str | Path):
        self.path = str(path)

    def create_schema(self):
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS entities (kind TEXT, id TEXT PRIMARY KEY, patient_id TEXT, payload TEXT NOT NULL)")

    def clear(self):
        self.create_schema()
        with sqlite3.connect(self.path) as db: db.execute("DELETE FROM entities")

    def save(self, entity):
        self.create_schema()
        payload = json.dumps(asdict(entity), default=_json, ensure_ascii=False)
        patient_id = getattr(entity, "patient_id", None)
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT OR REPLACE INTO entities VALUES (?,?,?,?)", (type(entity).__name__, entity.id, patient_id, payload))

    def _rows(self, kind, patient_id=None):
        with sqlite3.connect(self.path) as db:
            sql, args = "SELECT payload FROM entities WHERE kind=?", [kind]
            if patient_id: sql, args = sql + " AND patient_id=?", args + [patient_id]
            return [json.loads(r[0]) for r in db.execute(sql, args)]

    def patients(self): return [Patient(**{**x, "pathway_started": date.fromisoformat(x["pathway_started"])}) for x in self._rows("Patient")]
    def patient(self, patient_id): return next((p for p in self.patients() if p.id == patient_id), None)
    def checkins(self, pid): return sorted([CheckIn(**{**x, "recorded_at": datetime.fromisoformat(x["recorded_at"])}) for x in self._rows("CheckIn", pid)], key=lambda x:x.recorded_at)
    def notes(self, pid):
        cv=lambda x: datetime.fromisoformat(x) if x else None
        return [PatientNote(**{**x,"created_at":cv(x["created_at"]),"shared_at":cv(x["shared_at"]),"revoked_at":cv(x["revoked_at"])}) for x in self._rows("PatientNote",pid)]
    def goals(self,pid):
        return [JourneyGoal(**{**x,"kind":GoalKind(x["kind"]),"status":GoalStatus(x["status"]),"created_at":datetime.fromisoformat(x["created_at"]),"updated_at":datetime.fromisoformat(x["updated_at"])}) for x in self._rows("JourneyGoal",pid)]
    def assignments(self,pid):
        out=[]
        for x in self._rows("HomeworkAssignment",pid):
            t=HomeworkTemplate(**{**x["template"],"prompts":tuple(x["template"]["prompts"])})
            s=x["submission"]
            sub=HomeworkSubmission(**{**s,"submitted_at":datetime.fromisoformat(s["submitted_at"])}) if s else None
            out.append(HomeworkAssignment(x["id"],x["patient_id"],t,datetime.fromisoformat(x["assigned_at"]),datetime.fromisoformat(x["due_at"]),HomeworkStatus(x["status"]),sub))
        return sorted(out,key=lambda a:a.assigned_at)
    def bridges(self,pid):
        out=[]
        for x in self._rows("SessionBridge",pid):
            out.append(SessionBridge(x["id"],pid,datetime.fromisoformat(x["created_at"]),BridgeStatus(x["status"]),[SessionBridgeItem(**i) for i in x["items"]],x["optional_text"],datetime.fromisoformat(x["updated_at"]) if x["updated_at"] else None))
        return sorted(out,key=lambda b:b.created_at)
    def events(self,pid): return sorted([TimelineEvent(**{**x,"occurred_at":datetime.fromisoformat(x["occurred_at"]),"kind":EventKind(x["kind"])}) for x in self._rows("TimelineEvent",pid)],key=lambda e:e.occurred_at)
    def onboarding(self,pid):
        rows=self._rows("PathwayOnboarding",pid)
        return PathwayOnboarding(**{**rows[0],"completed_at":datetime.fromisoformat(rows[0]["completed_at"]) if rows[0]["completed_at"] else None}) if rows else None
