from datetime import timedelta

import pytest

from psyhelper.demo.clock import DemoClock
from psyhelper.demo.scenarios import did
from psyhelper.demo.seed import seed_demo_database
from psyhelper.domain.models import BridgeStatus, HomeworkStatus
from psyhelper.services.core import build_bridge_candidates, therapist_notes
from psyhelper.ui import state
from psyhelper.ui.actions import (complete_homework, create_patient_checkin, create_private_note,
                                  prepare_patient_bridge, set_note_sharing)


class _State(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class _Streamlit:
    session_state = _State()


def test_patient_checkin_and_homework_persist_across_views(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db"); now = DemoClock().now
    patient = repo.patient(did("luca", "patient", 0))
    check = create_patient_checkin(repo, patient.id, now, anxiety=4, stress=3, mood="presente", mood_intensity=5)
    assert repo.checkins(patient.id)[-1].id == check.id
    assignment = next(a for a in repo.assignments(patient.id) if a.status == HomeworkStatus.PENDING)
    answers = {prompt: "Una risposta completa" for prompt in assignment.template.prompts}
    complete_homework(repo, assignment, answers, now)
    persisted = next(a for a in repo.assignments(patient.id) if a.id == assignment.id)
    assert persisted.status == HomeworkStatus.COMPLETED and persisted.submission.answers == answers


def test_note_is_private_by_default_then_share_revoke_hides_from_therapist(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db"); now = DemoClock().now
    patient = repo.patient(did("martina", "patient", 0))
    note = create_private_note(repo, patient.id, "Resta per me", now)
    assert not note.is_shared and note.id not in {n.id for n in therapist_notes(repo.notes(patient.id))}
    set_note_sharing(repo, note, True, now + timedelta(minutes=1))
    assert note.id in {n.id for n in therapist_notes(repo.notes(patient.id))}
    set_note_sharing(repo, note, False, now + timedelta(minutes=2))
    assert note.id not in {n.id for n in therapist_notes(repo.notes(patient.id))}


def test_patient_bridge_has_one_priority_and_private_notes_never_candidates(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db"); now = DemoClock().now
    patient = repo.patient(did("luca", "patient", 0)); notes = repo.notes(patient.id)
    candidates = build_bridge_candidates(notes, repo.events(patient.id), checkins=repo.checkins(patient.id), assignments=repo.assignments(patient.id))
    private_ids = {n.id for n in notes if not n.is_shared}
    assert not private_ids & {item.source_id for item in candidates}
    selected = [item.id for item in candidates[:3]]
    ready = prepare_patient_bridge(repo, patient.id, candidates, selected, selected[1], "Vorrei parlarne", now)
    assert ready.status == BridgeStatus.READY and sum(item.priority == 1 for item in ready.items) == 1
    therapist_bridge = next(b for b in reversed(repo.bridges(patient.id)) if b.status != BridgeStatus.ARCHIVED)
    assert therapist_bridge.id == ready.id and therapist_bridge.optional_text == "Vorrei parlarne"
    with pytest.raises(ValueError): prepare_patient_bridge(repo, patient.id, candidates, selected, "missing", "", now)


def test_role_switch_keeps_patient_and_uses_small_state():
    st = _Streamlit(); st.session_state.clear(); state.init_state(st)
    state.open_patient(st, "luca-id"); state.switch_role(st, "Paziente")
    assert st.session_state == {"route": "patient_today", "selected_patient_id": "luca-id", "demo_role": "Paziente"}
    state.switch_role(st, "Professionista")
    assert st.session_state == {"route": "oggi", "selected_patient_id": "luca-id", "demo_role": "Professionista"}
