from dataclasses import dataclass
from datetime import timedelta

from psyhelper.demo.clock import DemoClock
from psyhelper.domain.models import BridgeStatus, EventKind, HomeworkStatus
from psyhelper.services.core import build_report, derive_progress, therapist_notes


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
    last = max([c.recorded_at for c in checks] + [a.assigned_at for a in assignments])
    current = next((b for b in reversed(repo.bridges(patient.id)) if b.status != BridgeStatus.ARCHIVED), None)
    step = next((e for e in reversed(events) if e.kind == EventKind.STEP_FORWARD), None)
    setback = next((e for e in reversed(events) if e.kind == EventKind.SETBACK), None)
    delta = None if metrics["previous_anxiety"] is None else metrics["anxiety"] - metrics["previous_anxiety"]
    if step:
        trend, label, highlight, tone = "Punteggi stabili, comportamento in evoluzione", "Passo avanti", step.text, "positive"
    elif patient.name == "Martina Romano":
        trend, label, highlight, tone = "Stress aumentato nelle ultime settimane", "Cambiamento recente", "Nuova nota condivisa", "attention"
    elif patient.name == "Andrea Conti" and setback:
        trend, label, highlight, tone = "Miglioramento iniziale, difficoltà recente", "Da riprendere", setback.text, "attention"
    else:
        trend = "Ansia più bassa rispetto all'inizio" if delta is not None and delta < 0 else "Andamento stabile"
        label, highlight, tone = ("Bridge", "Pronto per la seduta", "positive") if current and current.status == BridgeStatus.READY else ("Ultimo segnale", "Andamento da osservare", "")
    hw = f"{counts['completed']} di {counts['assigned']} completati"
    if counts["expired"]: hw += f" · {counts['expired']} scaduti"
    return PatientSummary(patient.id, patient.name, patient.age, patient.scenario, relative_day(last, now), trend, hw, label, highlight, tone)


def patient_read_model(repo, patient_id, now=None):
    now = now or DemoClock().now
    patient = repo.patient(patient_id)
    checks, assignments, notes, events = repo.checkins(patient_id), repo.assignments(patient_id), repo.notes(patient_id), repo.events(patient_id)
    return {
        "patient": patient, "onboarding": repo.onboarding(patient_id), "checkins": checks,
        "assignments": assignments, "notes": therapist_notes(notes), "events": events,
        "bridges": repo.bridges(patient_id), "metrics": recent_metrics(checks),
        "counts": homework_counts(assignments), "insights": derive_progress(checks, events),
        "report": build_report(patient_id, now - timedelta(days=21), now, checks, assignments, notes, events),
    }
