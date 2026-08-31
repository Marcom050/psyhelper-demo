from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any


class HomeworkStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"


class GoalStatus(StrEnum):
    ACTIVE = "active"
    ACHIEVED = "achieved"


class GoalKind(StrEnum):
    GOAL = "goal"
    COMMITMENT = "commitment"


class BridgeStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class EventKind(StrEnum):
    IMPROVEMENT = "improvement"
    SETBACK = "setback"
    STEP_FORWARD = "step_forward"
    RECURRING_TRIGGER = "recurring_trigger"


@dataclass
class Therapist:
    id: str
    name: str


@dataclass
class Patient:
    id: str
    therapist_id: str
    name: str
    age: int
    pathway_started: date
    scenario: str


@dataclass
class CheckIn:
    id: str
    patient_id: str
    recorded_at: datetime
    anxiety: int
    stress: int
    trigger: str = ""
    behavior: str = ""

    def __post_init__(self):
        if not all(0 <= value <= 10 for value in (self.anxiety, self.stress)):
            raise ValueError("Anxiety and stress must be between 0 and 10")


@dataclass
class HomeworkTemplate:
    id: str
    title: str
    prompts: tuple[str, ...]


@dataclass
class HomeworkSubmission:
    id: str
    assignment_id: str
    submitted_at: datetime
    answers: dict[str, str]


@dataclass
class HomeworkAssignment:
    id: str
    patient_id: str
    template: HomeworkTemplate
    assigned_at: datetime
    due_at: datetime
    status: HomeworkStatus = HomeworkStatus.PENDING
    submission: HomeworkSubmission | None = None


@dataclass
class JourneyGoal:
    id: str
    patient_id: str
    title: str
    kind: GoalKind
    status: GoalStatus
    created_at: datetime
    updated_at: datetime


@dataclass
class PatientNote:
    id: str
    patient_id: str
    text: str
    created_at: datetime
    shared_at: datetime | None = None
    revoked_at: datetime | None = None

    @property
    def is_shared(self) -> bool:
        return self.shared_at is not None and (self.revoked_at is None or self.revoked_at < self.shared_at)


@dataclass
class SessionBridgeItem:
    id: str
    source_type: str
    source_id: str
    title: str
    priority: int = 0


@dataclass
class SessionBridge:
    id: str
    patient_id: str
    created_at: datetime
    status: BridgeStatus = BridgeStatus.DRAFT
    items: list[SessionBridgeItem] = field(default_factory=list)
    optional_text: str = ""
    updated_at: datetime | None = None


@dataclass
class PathwayOnboarding:
    id: str
    patient_id: str
    completed_at: datetime | None
    focus: str


@dataclass
class TimelineEvent:
    id: str
    patient_id: str
    occurred_at: datetime
    kind: EventKind
    text: str
    source_id: str | None = None


@dataclass
class ProgressInsight:
    kind: str
    text: str


@dataclass
class PreSessionReport:
    patient_id: str
    window_start: datetime
    window_end: datetime
    homework_assigned: int
    homework_completed: int
    recent_anxiety: float | None
    recent_stress: float | None
    recent_answers: list[dict[str, str]]
    shared_notes: list[PatientNote]
    points_to_revisit: list[str]
    disclaimer: str = "Sintesi descrittiva di supporto al percorso, non diagnostica."
