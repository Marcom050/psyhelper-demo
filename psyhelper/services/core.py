from __future__ import annotations

from collections import Counter
from datetime import datetime
from uuid import NAMESPACE_URL, uuid4, uuid5

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


def _candidate(source_type: str, source_id: str, title: str, priority: int) -> SessionBridgeItem:
    candidate_id = str(uuid5(NAMESPACE_URL, f"psyhelper:bridge:{source_type}:{source_id}"))
    return SessionBridgeItem(candidate_id, source_type, source_id, title, priority)


def build_bridge_candidates(
    notes: list[PatientNote],
    events: list[TimelineEvent],
    limit: int = 12,
    *,
    checkins: list[CheckIn] | None = None,
    assignments: list[HomeworkAssignment] | None = None,
) -> list[SessionBridgeItem]:
    """Build reference-only candidates. Private notes are deliberately filtered out."""
    candidates = [_candidate("note", n.id, "Nota condivisa", 10) for n in notes if n.is_shared]
    candidates += [_candidate("progress_event", e.id, e.text, 7) for e in events]
    recent_checks = sorted(checkins or [], key=lambda c: c.recorded_at, reverse=True)[:4]
    candidates += [
        _candidate("checkin", c.id, f"Check-in: {c.mood or c.trigger or 'aggiornamento recente'}", 8)
        for c in recent_checks if c.trigger or c.mood or c.note_for_therapist
    ]
    completed = sorted(
        (a for a in assignments or [] if a.status == HomeworkStatus.COMPLETED and a.submission),
        key=lambda a: a.submission.submitted_at,
        reverse=True,
    )[:4]
    candidates += [_candidate("homework", a.id, f"Homework completato: {a.template.title}", 9) for a in completed]
    return sorted(candidates, key=lambda x: (-x.priority, x.source_type, x.source_id))[:limit]


def _average(checkins: list[CheckIn]) -> float:
    return sum(c.anxiety + c.stress for c in checkins) / (2 * len(checkins))


def derive_progress(checkins: list[CheckIn], events: list[TimelineEvent]) -> list[ProgressInsight]:
    """Use transparent time windows; this is descriptive logic, not a clinical algorithm."""
    if len(checkins) < 6:
        return [ProgressInsight("insufficient_data", "Servono almeno sei check-in per confrontare periodi distinti.")]
    ordered = sorted(checkins, key=lambda c: c.recorded_at)
    window = min(5, len(ordered) // 3)
    baseline, recent = ordered[:window], ordered[-window:]
    delta = _average(recent) - _average(baseline)
    result: list[ProgressInsight] = []
    if delta <= -0.8:
        result.append(ProgressInsight("improvement", "Nella finestra recente ansia e stress medi sono più bassi rispetto all'inizio.", tuple(c.id for c in baseline + recent)))
    elif delta >= 0.8:
        result.append(ProgressInsight("setback", "Nella finestra recente ansia e stress medi sono più alti rispetto all'inizio.", tuple(c.id for c in baseline + recent)))
    else:
        midpoint = ordered[window:-window]
        if midpoint and abs(_average(recent) - _average(midpoint[-window:])) < 0.6:
            result.append(ProgressInsight("maintained_progress", "I punteggi recenti mantengono un andamento simile alla finestra precedente.", tuple(c.id for c in recent)))

    normalized = [(c.trigger.strip().casefold(), c) for c in ordered if c.trigger.strip()]
    counts = Counter(name for name, _ in normalized)
    recurring = [name for name, count in counts.items() if count >= 3]
    if recurring:
        name = sorted(recurring, key=lambda x: (-counts[x], x))[0]
        supporting = tuple(c.id for trigger, c in normalized if trigger == name)
        result.append(ProgressInsight("recurring_trigger", f"Il contesto “{name}” ricorre in {counts[name]} check-in.", supporting))

    steps = [e for e in events if e.kind == EventKind.STEP_FORWARD]
    if steps:
        sources = tuple(e.source_id or e.id for e in steps)
        result.append(ProgressInsight("step_forward", "È presente un passo di avvicinamento collegato a un'attività registrata.", sources))
    return result


def _metric(checks: list[CheckIn], attr: str) -> float | None:
    return round(sum(getattr(c, attr) for c in checks) / len(checks), 1) if checks else None


def build_report(patient_id: str, start: datetime, end: datetime, checkins: list[CheckIn], assignments: list[HomeworkAssignment], notes: list[PatientNote], events: list[TimelineEvent]) -> PreSessionReport:
    checks = sorted((c for c in checkins if start <= c.recorded_at <= end), key=lambda c: c.recorded_at)
    duration = end - start
    previous = [c for c in checkins if start - duration <= c.recorded_at < start]
    hw = [a for a in assignments if start <= a.assigned_at <= end]
    completed = [a for a in hw if a.status == HomeworkStatus.COMPLETED]
    anxiety, stress = _metric(checks, "anxiety"), _metric(checks, "stress")
    previous_anxiety = _metric(previous, "anxiety") if len(previous) >= 2 and len(checks) >= 2 else None
    previous_stress = _metric(previous, "stress") if len(previous) >= 2 and len(checks) >= 2 else None
    insights = derive_progress(checkins, events)
    points = [i.text for i in insights if i.kind in ("setback", "recurring_trigger")]
    points.extend(
        e.text for e in events
        if start <= e.occurred_at <= end and e.kind in (EventKind.SETBACK, EventKind.RECURRING_TRIGGER)
    )
    expired = [a for a in hw if a.status == HomeworkStatus.EXPIRED]
    if expired:
        points.append(f"{len(expired)} homework recenti risultano scaduti e possono essere ripresi insieme.")
    shared = therapist_notes(notes)
    points.extend(f"Nota condivisa: {n.text}" for n in shared if start <= n.created_at <= end)
    recent_completed = sorted((a for a in completed if a.submission), key=lambda a: a.submission.submitted_at, reverse=True)[:3]
    answers = [{"homework": a.template.title, **a.submission.answers} for a in recent_completed]
    return PreSessionReport(
        patient_id, start, end, len(hw), len(completed),
        sum(a.status == HomeworkStatus.PENDING for a in hw), len(expired),
        round(len(completed) / len(hw) * 100, 1) if hw else None,
        anxiety, stress, previous_anxiety, previous_stress,
        round(anxiety - previous_anxiety, 1) if anxiety is not None and previous_anxiety is not None else None,
        round(stress - previous_stress, 1) if stress is not None and previous_stress is not None else None,
        answers, shared, list(dict.fromkeys(points)),
    )
