from datetime import datetime
from uuid import uuid4

from psyhelper.domain.models import BridgeStatus, HomeworkAssignment, HomeworkStatus, SessionBridge
from psyhelper.services.core import transition_bridge


def assign_homework(repo, patient_id, template, assigned_at: datetime, due_at: datetime):
    assignment = HomeworkAssignment(str(uuid4()), patient_id, template, assigned_at, due_at, HomeworkStatus.PENDING)
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
