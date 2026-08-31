from datetime import timedelta

import pandas as pd
from psyhelper.demo.clock import DemoClock
from psyhelper.demo.homework_catalog import homework_template
from psyhelper.demo.scenarios import did
from psyhelper.demo.seed import seed_demo_database
from psyhelper.domain.models import BridgeStatus, HomeworkStatus
from psyhelper.repository import DemoRepository
from psyhelper.ui.actions import advance_bridge, assign_homework
from psyhelper.ui.presentation import (MetricDelta, distinct_revisit_points, italian_date,
                                       metric_delta_model, patient_read_model, patient_summary,
                                       significant_events, trend_dataset)
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
    assert st.session_state == {"route": "oggi", "selected_patient_id": "patient-1", "demo_role": "Professionista"}
    state.dashboard(st)
    assert st.session_state == {"route": "dashboard", "selected_patient_id": None, "demo_role": "Professionista"}


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


def test_therapist_assignment_survives_reload_and_is_visible_to_patient(tmp_path):
    path = tmp_path / "demo.db"; repo = seed_demo_database(path)
    patient = repo.patient(did("giulia", "patient", 0)); now = DemoClock().now
    created = assign_homework(repo, patient.id, homework_template("abc"), now, (now + timedelta(days=7)).date())
    reloaded = DemoRepository(path)
    therapist_assignment = next(a for a in patient_read_model(reloaded, patient.id)["assignments"] if a.id == created.id)
    assert therapist_assignment.template.prompts == homework_template("abc").prompts
    assert any(a.id == created.id for a in reloaded.assignments(patient.id) if a.status == HomeworkStatus.PENDING)
    assert therapist_assignment.due_at.tzinfo == now.tzinfo


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


def test_italian_dates_do_not_depend_on_system_locale():
    now = DemoClock().now
    assert italian_date(now, style="short") == "31 ago"
    assert italian_date(now, year=True) == "31 agosto 2026"


def test_metric_delta_has_semantic_direction_and_complete_copy():
    assert metric_delta_model(4.2, 5.0) == MetricDelta("↓ 0,8 rispetto al periodo precedente", "positive")
    assert metric_delta_model(5.8, 5.0) == MetricDelta("↑ 0,8 rispetto al periodo precedente", "attention")
    assert metric_delta_model(5.0, 5.0) == MetricDelta("→ stabile", "neutral")
    assert metric_delta_model(None, 5.0) == MetricDelta("Confronto non disponibile", "neutral")


def test_chart_dataset_contains_both_numeric_series_for_every_seed_patient(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db")
    expected = {"Giulia Bianchi": 20, "Luca Ferri": 18, "Martina Romano": 20, "Andrea Conti": 18}
    for patient in repo.patients():
        checks = repo.checkins(patient.id); data = trend_dataset(checks)
        assert len(checks) == expected[patient.name]
        assert isinstance(data, pd.DataFrame)
        assert len(data) == expected[patient.name] * 2
        assert set(data["metric"]) == {"Ansia", "Stress"}
        assert pd.api.types.is_datetime64_any_dtype(data["date"])
        assert pd.api.types.is_string_dtype(data["metric"])
        assert pd.api.types.is_numeric_dtype(data["value"])
        assert data["date"].is_monotonic_increasing


def test_pre_session_revisit_points_do_not_repeat_shared_notes(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db")
    model = patient_read_model(repo, did("martina", "patient", 0))
    points = distinct_revisit_points(model["report"], [item.text for item in model["insights"][:4]])
    shared = {note.text.casefold() for note in model["report"].shared_notes}
    assert not shared & {point.removeprefix("Nota condivisa:").strip().casefold() for point in points}


def test_bridge_is_available_with_significant_pre_session_context(tmp_path):
    repo = seed_demo_database(tmp_path / "demo.db")
    model = patient_read_model(repo, did("giulia", "patient", 0))
    current = next(b for b in reversed(model["bridges"]) if b.status != BridgeStatus.ARCHIVED)
    assert current.status == BridgeStatus.READY
    assert current.items
    assert 3 <= len(significant_events(model["events"], model["checkins"])) <= 5
