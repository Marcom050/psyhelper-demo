from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from psyhelper.demo.clock import DemoClock
from psyhelper.demo.scenarios import did
from psyhelper.demo.seed import seed_demo_database
from psyhelper.domain.models import BridgeStatus
from psyhelper.repository import DemoRepository
from psyhelper.ui import shell
from psyhelper.ui.presentation import bridge_reference, patient_read_model


def button(app, label):
    return next(item for item in app.button if item.label == label)


def textarea(app, label):
    return next(item for item in app.text_area if item.label == label)


@pytest.fixture
def demo(tmp_path, monkeypatch):
    path = tmp_path / "presentation.sqlite3"
    seed_demo_database(path)
    monkeypatch.setattr(shell, "DEFAULT_DB", path)
    app = AppTest.from_file(Path(__file__).parents[2] / "app.py", default_timeout=20).run()
    yield app, DemoRepository(path)


def open_luca(app):
    next(item for item in app.button if item.key == f"open-{did('luca', 'patient', 0)}").click().run()
    button(app, "Vedi come paziente").click().run()
    assert app.session_state.selected_patient_id == did("luca", "patient", 0)
    assert app.session_state.demo_role == "Paziente"


def test_checkin_details_save_on_first_submission_and_reach_therapist(demo):
    app, repo = demo
    open_luca(app)
    button(app, "Come stai oggi?").click().run()
    # An expander exposes the fields without needing to submit an incomplete form.
    assert any(item.label == "Aggiungi un dettaglio (facoltativo)" for item in app.expander)
    textarea(app, "Cosa è successo?").set_value("Pausa con i colleghi")
    textarea(app, "Cosa hai fatto?").set_value("Ho proposto io un caffè")
    textarea(app, "Nota per il professionista").set_value("Vorrei riprendere questo passo")
    button(app, "Salva check-in").click().run()
    assert not app.exception
    check = repo.checkins(did("luca", "patient", 0))[-1]
    assert (check.trigger, check.behavior, check.note_for_therapist) == (
        "Pausa con i colleghi", "Ho proposto io un caffè", "Vorrei riprendere questo passo"
    )
    button(app, "Vedi come professionista").click().run()
    button(app, "Andamento").click().run()
    assert not app.exception
    assert any("Vorrei riprendere questo passo" in item.value for item in app.markdown)


def test_note_share_revoke_updates_the_therapist_view(demo):
    app, repo = demo
    open_luca(app)
    button(app, "Area privata").click().run()
    text = "Questo pensiero lo condivido soltanto quando scelgo io."
    textarea(app, "Scrivi qualcosa per te").set_value(text)
    button(app, "Salva nota").click().run()
    pid = did("luca", "patient", 0)
    note = next(item for item in repo.notes(pid) if item.text == text)
    assert note.id not in {item.id for item in patient_read_model(repo, pid)["notes"]}
    next(item for item in app.button if item.key == f"share-{note.id}").click().run()
    button(app, "Condividi").click().run()
    button(app, "Vedi come professionista").click().run()
    button(app, "Prepara seduta").click().run()
    assert any(text in item.value for item in app.markdown)
    button(app, "Vedi come paziente").click().run()
    button(app, "Area privata").click().run()
    next(item for item in app.button if item.key == f"revoke-{note.id}").click().run()
    assert any("Potrebbe essere già stata letta" in item.value for item in app.success)
    button(app, "Vedi come professionista").click().run()
    button(app, "Prepara seduta").click().run()
    assert not app.exception
    assert not any(text in item.value for item in app.markdown)


def test_bridge_complete_cycle_starts_a_clean_next_draft(demo):
    app, repo = demo
    open_luca(app)
    button(app, "Prepara la seduta").click().run()
    app.checkbox[0].check().run()
    textarea(app, "Vuoi aggiungere qualcosa?").set_value("Partirei da questa nota.")
    button(app, "Prepara Bridge").click().run()
    assert not app.exception
    pid = did("luca", "patient", 0)
    ready = next(item for item in repo.bridges(pid) if item.status == BridgeStatus.READY)
    button(app, "Vedi come professionista").click().run()
    button(app, "Prepara seduta").click().run()
    assert any("Partirei da questa nota" in item.value for item in app.markdown)
    button(app, "Segna come discusso").click().run()
    button(app, "Archivia Bridge").click().run()
    archived = next(item for item in repo.bridges(pid) if item.id == ready.id)
    assert archived.status == BridgeStatus.ARCHIVED and archived.items == ready.items
    button(app, "Vedi come paziente").click().run()
    button(app, "Prepara la seduta").click().run()
    assert not app.exception
    assert app.checkbox and not any(item.value for item in app.checkbox)
    assert textarea(app, "Vuoi aggiungere qualcosa?").value == ""
    assert button(app, "Prepara Bridge").disabled
    app.checkbox[1].check().run()
    button(app, "Prepara Bridge").click().run()
    next_ready = next(item for item in repo.bridges(pid) if item.status == BridgeStatus.READY)
    assert next_ready.id != archived.id
    assert next(item for item in repo.bridges(pid) if item.id == archived.id) == archived


def test_bridge_does_not_expose_note_after_revocation(demo):
    _, repo = demo
    pid = did("giulia", "patient", 0)
    model = patient_read_model(repo, pid)
    ready = next(item for item in model["bridges"] if item.status == BridgeStatus.READY)
    reference = next(item for item in ready.items if item.source_type == "note")
    note = next(item for item in repo.notes(pid) if item.id == reference.source_id)
    assert note.text in bridge_reference(reference, model)
    note.revoked_at = DemoClock().now
    repo.save(note)
    assert note.text not in bridge_reference(reference, patient_read_model(repo, pid))
