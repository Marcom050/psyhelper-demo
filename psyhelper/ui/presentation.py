from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd

from psyhelper.demo.clock import DemoClock
from psyhelper.domain.models import BridgeStatus, EventKind, HomeworkStatus, TimelineEvent
from psyhelper.services.core import build_report, derive_progress, therapist_notes


MONTHS_SHORT = ("gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic")
MONTHS_LONG = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre")


def italian_date(value: date | datetime, *, style: str = "long", year: bool = False) -> str:
    """Format a date without relying on the process locale."""
    names = MONTHS_SHORT if style == "short" else MONTHS_LONG
    suffix = f" {value.year}" if year else ""
    return f"{value.day} {names[value.month - 1]}{suffix}"


@dataclass(frozen=True)
class MetricDelta:
    text: str
    tone: str


def metric_delta_model(value, previous) -> MetricDelta:
    if value is None or previous is None:
        return MetricDelta("Confronto non disponibile", "neutral")
    delta = round(value - previous, 1)
    if abs(delta) < .1:
        return MetricDelta("→ stabile", "neutral")
    direction, tone = ("↓", "positive") if delta < 0 else ("↑", "attention")
    text = f"{direction} {abs(delta):.1f} rispetto al periodo precedente".replace(".", ",")
    return MetricDelta(text, tone)


def metric_delta(value, previous) -> str:
    """Backward-compatible textual form of the semantic metric delta."""
    return metric_delta_model(value, previous).text


def trend_dataset(checkins, limit=None):
    """Build the numeric, chronological long-form dataset consumed by Altair."""
    ordered = sorted(checkins, key=lambda check: check.recorded_at)
    if limit is not None:
        ordered = ordered[-limit:]
    rows = [
        {"date": check.recorded_at, "metric": metric, "value": float(value)}
        for check in ordered
        for metric, value in (("Ansia", check.anxiety), ("Stress", check.stress))
        if value is not None
    ]
    frame = pd.DataFrame(rows, columns=["date", "metric", "value"])
    frame["date"] = pd.to_datetime(frame["date"])
    frame["metric"] = frame["metric"].astype("string")
    frame["value"] = pd.to_numeric(frame["value"])
    return frame.sort_values("date", kind="stable").reset_index(drop=True)


def significant_events(events, checkins=(), limit=5):
    relevant = (EventKind.STEP_FORWARD, EventKind.SETBACK, EventKind.RECURRING_TRIGGER, EventKind.IMPROVEMENT)
    selected = [event for event in events if event.kind in relevant and "Cambiamento nei comportamenti" not in event.text]
    existing_sources = {event.source_id for event in selected}
    for check in sorted(checkins, key=lambda item: item.recorded_at, reverse=True):
        if check.behavior and check.id not in existing_sources and len(selected) < 3:
            selected.append(TimelineEvent(
                f"presentation-{check.id}", check.patient_id, check.recorded_at,
                EventKind.MAINTAINED_PROGRESS, check.behavior, check.id, "source",
            ))
    return sorted(selected, key=lambda event: event.occurred_at, reverse=True)[:limit]


def narrative_insights(insights, checkins, events, limit=4):
    """Keep quantitative observations intact; describe a step from its source."""
    by_id = {check.id: check for check in checkins}
    by_id.update({event.id: event for event in events})
    narratives = []
    for item in insights:
        sources = [by_id[source_id] for source_id in item.source_ids if source_id in by_id]
        event = next((source for source in sources if hasattr(source, "text")), None)
        check = next((source for source in reversed(sources) if hasattr(source, "behavior") and source.behavior), None)
        text = (event.text if event else check.behavior if check else item.text) if item.kind == "step_forward" else item.text
        if text and text not in [existing.text for existing in narratives]:
            narratives.append(type(item)(item.kind, text, item.source_ids))
    return narratives[:limit]


def bridge_reference(item, model):
    """Resolve a Bridge reference using only content visible in this read model."""
    sources = {
        "note": model["notes"], "checkin": model["checkins"],
        "homework": model["assignments"], "progress_event": model["events"],
    }
    source = next((entry for entry in sources.get(item.source_type, ()) if entry.id == item.source_id), None)
    if source is None:
        return "Contenuto non più condiviso o non disponibile."
    if item.source_type == "note":
        return source.text if source.is_shared else "La nota non è più condivisa."
    if item.source_type == "checkin":
        values = [source.trigger, source.behavior, source.note_for_therapist]
        return f"{italian_date(source.recorded_at)} · Ansia {source.anxiety}/10 · Stress {source.stress}/10\n\n" + "\n\n".join(value for value in values if value)
    if item.source_type == "homework":
        if not source.submission:
            return "Questa attività non è ancora stata completata."
        return "\n\n".join(f"{prompt.replace('_', ' ').capitalize()}: {answer}" for prompt, answer in source.submission.answers.items())
    return source.text


def latest_activity(checkins, assignments, notes, bridges):
    moments = [check.recorded_at for check in checkins]
    moments.extend(a.submission.submitted_at if a.submission else a.assigned_at for a in assignments)
    moments.extend(moment for note in notes for moment in (note.created_at, note.shared_at, note.revoked_at) if moment)
    moments.extend(bridge.updated_at or bridge.created_at for bridge in bridges)
    return max(moments) if moments else None


def distinct_revisit_points(report, displayed_insights):
    shown = {text.strip().casefold() for text in displayed_insights}
    shown.update(note.text.strip().casefold() for note in report.shared_notes)
    return [point for point in report.points_to_revisit if point.removeprefix("Nota condivisa:").strip().casefold() not in shown]


@dataclass(frozen=True)
class PatientSummary:
    patient_id: str
    name: str
    age: int
    focus: str
    last_activity: str
    trend: str
    homework: str
    highlight_label: str
    highlight: str
    tone: str


def relative_day(moment, now):
    days = (now.date() - moment.date()).days
    return "Oggi" if days == 0 else "Ieri" if days == 1 else f"{days} giorni fa"


def homework_counts(assignments):
    return {
        "assigned": len(assignments),
        "completed": sum(a.status == HomeworkStatus.COMPLETED for a in assignments),
        "pending": sum(a.status == HomeworkStatus.PENDING for a in assignments),
        "expired": sum(a.status == HomeworkStatus.EXPIRED for a in assignments),
    }


def recent_metrics(checkins, size=5):
    ordered = sorted(checkins, key=lambda c: c.recorded_at)
    recent, previous = ordered[-size:], ordered[-size * 2:-size]
    avg = lambda rows, field: round(sum(getattr(x, field) for x in rows) / len(rows), 1) if rows else None
    return {key: avg(rows, field) for key, rows, field in (
        ("anxiety", recent, "anxiety"), ("stress", recent, "stress"),
        ("previous_anxiety", previous, "anxiety"), ("previous_stress", previous, "stress"))}


def patient_summary(repo, patient, now=None):
    now = now or DemoClock().now
    checks, assignments, events = repo.checkins(patient.id), repo.assignments(patient.id), repo.events(patient.id)
    metrics, counts = recent_metrics(checks), homework_counts(assignments)
    last = latest_activity(checks, assignments, therapist_notes(repo.notes(patient.id)), repo.bridges(patient.id))
    current = next((b for b in reversed(repo.bridges(patient.id)) if b.status != BridgeStatus.ARCHIVED), None)
    step = next((e for e in reversed(events) if e.kind == EventKind.STEP_FORWARD), None)
    setback = next((e for e in reversed(events) if e.kind == EventKind.SETBACK), None)
    baseline_anxiety = sum(check.anxiety for check in checks[:5]) / len(checks[:5]) if checks else None
    delta = None if baseline_anxiety is None else metrics["anxiety"] - baseline_anxiety
    stress_delta = None if metrics["previous_stress"] is None else metrics["stress"] - metrics["previous_stress"]
    if step:
        trend, label, highlight, tone = "Un passo avanti, anche con ansia presente", "Passo avanti", step.text, "positive"
    elif setback and delta is not None and delta <= -.5 and stress_delta is not None and stress_delta >= .5:
        trend, label, highlight, tone = "Miglioramento iniziale, difficoltà recente", "Da riprendere", setback.text, "attention"
    elif stress_delta is not None and stress_delta >= .8:
        shared = therapist_notes(repo.notes(patient.id))
        trend = "Stress aumentato nei check-in recenti"
        label, highlight, tone = ("Contenuto condiviso", "Una nota condivisa da riprendere", "attention") if shared else ("Da riprendere", "Stress medio più alto rispetto ai cinque check-in precedenti", "attention")
    else:
        trend = "Ansia più bassa rispetto all'inizio" if delta is not None and delta <= -.5 else "Andamento da osservare insieme"
        label, highlight, tone = ("Bridge", "Pronto per la seduta", "positive") if current and current.status == BridgeStatus.READY else ("Ultimo segnale", "Andamento da osservare", "")
    hw = f"{counts['completed']} di {counts['assigned']} completati"
    if counts["expired"]: hw += f" · {counts['expired']} scaduti"
    return PatientSummary(patient.id, patient.name, patient.age, patient.scenario, relative_day(last, now) if last else "Nessuna attività", trend, hw, label, highlight, tone)


def patient_read_model(repo, patient_id, now=None):
    now = now or DemoClock().now
    patient = repo.patient(patient_id)
    checks, assignments, notes, events = repo.checkins(patient_id), repo.assignments(patient_id), repo.notes(patient_id), repo.events(patient_id)
    return {
        "patient": patient, "onboarding": repo.onboarding(patient_id), "checkins": checks,
        "assignments": assignments, "notes": therapist_notes(notes), "events": events,
        "bridges": repo.bridges(patient_id), "metrics": recent_metrics(checks),
        "counts": homework_counts(assignments), "insights": narrative_insights(derive_progress(checks, events), checks, events),
        "report": build_report(patient_id, now - timedelta(days=21), now, checks, assignments, notes, events),
        "last_activity": latest_activity(checks, assignments, therapist_notes(notes), repo.bridges(patient_id)),
    }
