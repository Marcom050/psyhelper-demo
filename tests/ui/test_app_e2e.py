import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from psyhelper.demo.reset import reset_demo_database
from psyhelper.demo.scenarios import did
from psyhelper.demo.seed import DEFAULT_DB
from psyhelper.domain.models import HomeworkStatus
from psyhelper.repository import DemoRepository


def _button(app, label):
    return next(button for button in app.button if button.label == label)


def _assert_data_chart(app):
    assert not app.exception
    charts = app.get("vega_lite_chart")
    assert len(charts) == 1
    spec = json.loads(charts[0].proto.spec)
    assert charts[0].proto.data.data
    encodings = [layer["encoding"] for layer in spec["layer"]]
    assert all(encoding["color"]["field"] == "metric" for encoding in encodings)
    assert all(encoding["y"]["field"] == "value" for encoding in encodings)


def test_apptest_charts_and_therapist_to_patient_homework_flow():
    reset_demo_database(DEFAULT_DB)
    try:
        app = AppTest.from_file(Path(__file__).parents[2] / "app.py", default_timeout=20).run()
        _button(app, "Apri percorso →").click().run()  # Giulia
        _assert_data_chart(app)

        _button(app, "Andamento").click().run()
        _assert_data_chart(app)

        repo = DemoRepository(DEFAULT_DB); patient_id = did("giulia", "patient", 0)
        before = len(repo.assignments(patient_id))
        _button(app, "Homework").click().run()
        _button(app, "Assegna attività").click().run()
        assert not app.exception
        _button(app, "Assegna").click().run()
        assert not app.exception
        assert app.session_state.route == "homework"
        assignments = DemoRepository(DEFAULT_DB).assignments(patient_id)
        created = assignments[-1]
        assert len(assignments) == before + 1 and created.status == HomeworkStatus.PENDING

        app.radio[0].set_value("Paziente").run()
        app.selectbox[-1].set_value(patient_id).run()
        _button(app, "Attività").click().run()
        assert any(created.template.title in item.value and "Scadenza" in item.value for item in app.markdown)
        _button(app, "Percorso").click().run()
        _assert_data_chart(app)
    finally:
        reset_demo_database(DEFAULT_DB)
