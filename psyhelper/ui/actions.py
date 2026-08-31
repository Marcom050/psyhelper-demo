from datetime import date, datetime, time
from uuid import uuid4

from psyhelper.domain.models import (BridgeStatus, CheckIn, HomeworkAssignment, HomeworkStatus, HomeworkTemplate,
                                    PatientNote, SessionBridge, SessionBridgeItem)
from psyhelper.services.core import revoke_note, share_note, submit_homework, transition_bridge


def assign_homework(repo, patient_id, template, assigned_at: datetime, due_at: date | datetime):
    if isinstance(due_at, date) and not isinstance(due_at, datetime):
        due_at = datetime.combine(due_at, time.max, tzinfo=assigned_at.tzinfo)
    snapshot = HomeworkTemplate(template.id, template.title, tuple(template.prompts))
    assignment = HomeworkAssignment(str(uuid4()), patient_id, snapshot, assigned_at, due_at, HomeworkStatus.PENDING)
    repo.save(assignment)
    return assignment


def advance_bridge(repo, bridge, now: datetime):
    target = {BridgeStatus.READY: BridgeStatus.REVIEWED, BridgeStatus.REVIEWED: BridgeStatus.ARCHIVED}[bridge.status]
    transition_bridge(bridge, target, now)
    repo.save(bridge)
    if target == BridgeStatus.ARCHIVED:
        draft = SessionBridge(str(uuid4()), bridge.patient_id, now)
        repo.save(draft)
        return draft
    return bridge


def create_patient_checkin(repo, patient_id: str, now: datetime, **values):
    checkin = CheckIn(str(uuid4()), patient_id, now, **values)
    repo.save(checkin)
    return checkin


def complete_homework(repo, assignment, answers: dict[str, str], now: datetime):
    submit_homework(assignment, answers, now)
    repo.save(assignment)
    return assignment


def create_private_note(repo, patient_id: str, text: str, now: datetime):
    if not text.strip():
        raise ValueError("La nota non può essere vuota")
    note = PatientNote(str(uuid4()), patient_id, text.strip(), now)
    repo.save(note)
    return note


def set_note_sharing(repo, note, shared: bool, now: datetime):
    (share_note if shared else revoke_note)(note, now)
    repo.save(note)
    return note


def prepare_patient_bridge(repo, patient_id: str, candidates, selected_ids: list[str], priority_id: str,
                           optional_text: str, now: datetime):
    if not 1 <= len(selected_ids) <= 4:
        raise ValueError("Scegli da uno a quattro elementi")
    if priority_id not in selected_ids:
        raise ValueError("La priorità deve essere uno degli elementi scelti")
    available = {item.id: item for item in candidates}
    if any(item_id not in available for item_id in selected_ids):
        raise ValueError("Elemento non disponibile")
    current = next((b for b in reversed(repo.bridges(patient_id)) if b.status != BridgeStatus.ARCHIVED), None)
    if current is None:
        current = SessionBridge(str(uuid4()), patient_id, now)
    if current.status != BridgeStatus.DRAFT:
        raise ValueError("Il Bridge corrente non è modificabile")
    current.items = [SessionBridgeItem(available[item_id].id, available[item_id].source_type,
                                       available[item_id].source_id, available[item_id].title,
                                       1 if item_id == priority_id else 0) for item_id in selected_ids]
    current.optional_text = optional_text.strip()
    transition_bridge(current, BridgeStatus.READY, now)
    repo.save(current)
    return current
