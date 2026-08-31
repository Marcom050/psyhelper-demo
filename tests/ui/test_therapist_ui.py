from datetime import timedelta

from psyhelper.demo.clock import DemoClock
from psyhelper.demo.homework_catalog import homework_template
from psyhelper.demo.scenarios import did
from psyhelper.demo.seed import seed_demo_database
from psyhelper.domain.models import BridgeStatus, HomeworkStatus
from psyhelper.ui.actions import advance_bridge, assign_homework
from psyhelper.ui.presentation import patient_read_model, patient_summary
from psyhelper.ui import state


class _State(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class _Streamlit:
    session_state = _State()


def test_patient_selection_uses_only_small_route_state():
    st = _Streamlit(); st.session_state.clear()
    state.init_state(st)
    state.open_patient(st, "patient-1")
    assert st.session_state == {"route": "oggi", "selected_patient_id": "patient-1"}
    state.dashboard(st)
    assert st.session_state == {"route": "dashboard", "selected_patient_id": None}


def test_dashboard_summaries_are_derived_from_repository(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db")
    summaries = {p.name: patient_summary(repo, p) for p in repo.patients()}
    assert "Ansia più bassa" in summaries["Giulia Bianchi"].trend
    assert summaries["Luca Ferri"].highlight_label == "Passo avanti"
    assert "Stress aumentato" in summaries["Martina Romano"].trend
    assert summaries["Andrea Conti"].highlight_label == "Da riprendere"


def test_homework_assignment_is_persisted_and_read_model_refreshes(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db")
    patient = repo.patient(did("giulia", "patient", 0)); now = DemoClock().now
    before = len(repo.assignments(patient.id))
    created = assign_homework(repo, patient.id, homework_template("abc"), now, now + timedelta(days=7))
    assert len(repo.assignments(patient.id)) == before + 1
    assert repo.assignments(patient.id)[-1].id == created.id
    assert patient_read_model(repo, patient.id)["counts"]["pending"] >= 1


def test_bridge_actions_persist_and_archiving_creates_independent_draft(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db")
    patient = repo.patient(did("giulia", "patient", 0)); now = DemoClock().now
    ready = next(b for b in reversed(repo.bridges(patient.id)) if b.status != BridgeStatus.ARCHIVED)
    advance_bridge(repo, ready, now)
    reviewed = next(b for b in reversed(repo.bridges(patient.id)) if b.status != BridgeStatus.ARCHIVED)
    assert reviewed.status == BridgeStatus.REVIEWED
    draft = advance_bridge(repo, reviewed, now + timedelta(minutes=1))
    current = next(b for b in reversed(repo.bridges(patient.id)) if b.status != BridgeStatus.ARCHIVED)
    assert current.status == BridgeStatus.DRAFT and current.id == draft.id and current.id != reviewed.id


def test_therapist_model_never_contains_private_notes_and_matches_report(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db")
    patient = repo.patient(did("martina", "patient", 0))
    model = patient_read_model(repo, patient.id)
    private_ids = {n.id for n in repo.notes(patient.id) if not n.is_shared}
    assert not private_ids & {n.id for n in model["notes"]}
    assert not private_ids & {n.id for n in model["report"].shared_notes}
    assert model["report"].homework_expired == sum(a.status == HomeworkStatus.EXPIRED for a in model["assignments"] if a.assigned_at >= DemoClock().now - timedelta(days=21))
