from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from psyhelper.domain.models import *


def submit_homework(assignment: HomeworkAssignment, answers: dict[str, str], now: datetime) -> HomeworkAssignment:
    expected = set(assignment.template.prompts)
    if set(answers) != expected or any(not value.strip() for value in answers.values()):
        raise ValueError("All homework answers are required")
    assignment.submission = HomeworkSubmission(str(uuid4()), assignment.id, now, answers)
    assignment.status = HomeworkStatus.COMPLETED
    return assignment


def expire_homework(assignment: HomeworkAssignment, now: datetime) -> HomeworkAssignment:
    if assignment.status == HomeworkStatus.PENDING and now > assignment.due_at:
        assignment.status = HomeworkStatus.EXPIRED
    return assignment


def share_note(note: PatientNote, now: datetime) -> None:
    note.shared_at, note.revoked_at = now, None


def revoke_note(note: PatientNote, now: datetime) -> None:
    note.revoked_at = now


def therapist_notes(notes: list[PatientNote]) -> list[PatientNote]:
    return sorted((n for n in notes if n.is_shared), key=lambda n: n.created_at, reverse=True)


def update_goal(goal: JourneyGoal, title: str, now: datetime) -> None:
    goal.title, goal.updated_at = title, now


def achieve_goal(goal: JourneyGoal, now: datetime) -> None:
    goal.status, goal.updated_at = GoalStatus.ACHIEVED, now


def transition_bridge(bridge: SessionBridge, target: BridgeStatus, now: datetime) -> None:
    allowed = {BridgeStatus.DRAFT: BridgeStatus.READY, BridgeStatus.READY: BridgeStatus.REVIEWED,
               BridgeStatus.REVIEWED: BridgeStatus.ARCHIVED}
    if allowed.get(bridge.status) != target:
        raise ValueError("Invalid bridge transition")
    bridge.status, bridge.updated_at = target, now


def build_bridge_candidates(notes: list[PatientNote], events: list[TimelineEvent], limit: int = 5) -> list[SessionBridgeItem]:
    candidates = [SessionBridgeItem(str(uuid4()), "note", n.id, n.text, 10) for n in notes if n.is_shared]
    candidates += [SessionBridgeItem(str(uuid4()), "event", e.id, e.text, 5) for e in events]
    return sorted(candidates, key=lambda x: x.priority, reverse=True)[:limit]


def derive_progress(checkins: list[CheckIn], events: list[TimelineEvent]) -> list[ProgressInsight]:
    if len(checkins) < 4:
        return [ProgressInsight("insufficient_data", "Servono più dati per descrivere un andamento.")]
    ordered = sorted(checkins, key=lambda c: c.recorded_at)
    baseline = sum(c.anxiety + c.stress for c in ordered[:3]) / 6
    recent = sum(c.anxiety + c.stress for c in ordered[-3:]) / 6
    kind = "improvement" if recent <= baseline - 1 else "setback" if recent >= baseline + 1 else "stable"
    result = [ProgressInsight(kind, "Il confronto temporale mostra un cambiamento descrittivo nei punteggi recenti.")]
    triggers = [c.trigger for c in ordered if c.trigger]
    if triggers and max(map(triggers.count, set(triggers))) >= 3:
        result.append(ProgressInsight("recurring_trigger", "Un contesto compare più volte nei check-in."))
    if any(e.kind == EventKind.STEP_FORWARD for e in events):
        result.append(ProgressInsight("step_forward", "È stato registrato un passo avanti concreto."))
    return result


def build_report(patient_id: str, start: datetime, end: datetime, checkins: list[CheckIn], assignments: list[HomeworkAssignment], notes: list[PatientNote], events: list[TimelineEvent]) -> PreSessionReport:
    checks = [c for c in checkins if start <= c.recorded_at <= end]
    hw = [a for a in assignments if start <= a.assigned_at <= end]
    avg = lambda attr: round(sum(getattr(c, attr) for c in checks) / len(checks), 1) if checks else None
    return PreSessionReport(patient_id, start, end, len(hw), sum(a.status == HomeworkStatus.COMPLETED for a in hw),
        avg("anxiety"), avg("stress"), [a.submission.answers for a in hw if a.submission], therapist_notes(notes),
        [e.text for e in events if start <= e.occurred_at <= end and e.kind in (EventKind.SETBACK, EventKind.RECURRING_TRIGGER)])
