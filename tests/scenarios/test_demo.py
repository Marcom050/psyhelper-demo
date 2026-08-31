import hashlib
from psyhelper.demo.seed import seed_demo_database, validate_demo
from psyhelper.demo.reset import reset_demo_database
from psyhelper.demo.scenarios import EXPECTATIONS
from psyhelper.demo.scenarios import did
from psyhelper.demo.homework_catalog import HOMEWORK_CATALOG
from psyhelper.domain.models import EventKind
from psyhelper.services.core import build_bridge_candidates, build_report, derive_progress
from psyhelper.demo.clock import DemoClock
from datetime import timedelta

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def test_seed_idempotent_and_expectations(tmp_path):
    path=tmp_path/"demo.db"; repo=seed_demo_database(path); validate_demo(repo)
    ids=[p.id for p in repo.patients()]; seed_demo_database(path)
    assert ids==[p.id for p in repo.patients()] and len(EXPECTATIONS)==4

def test_reset_discards_changes(tmp_path):
    path=tmp_path/"demo.db"; repo=seed_demo_database(path); initial=sum(len(repo.checkins(p.id)) for p in repo.patients())
    repo.clear(); assert repo.patients()==[]
    reset_demo_database(path); repo=seed_demo_database(path)
    assert sum(len(repo.checkins(p.id)) for p in repo.patients())==initial

def test_catalog_and_scenarios_use_distinct_homework(tmp_path):
    assert len(HOMEWORK_CATALOG)==9
    assert {t.title for t in HOMEWORK_CATALOG.values()}=={"ABC","Registro dei pensieri","Ristrutturazione cognitiva","Esposizione graduale","Monitoraggio dell'evitamento","Behavioral activation","Scheda emozioni/trigger","Respiro 3 minuti","Pensiero più realistico"}
    repo=seed_demo_database(tmp_path/"demo.db")
    for patient in repo.patients():
        assignments=repo.assignments(patient.id)
        assert len({a.template.id for a in assignments})>1
        assert all(set(a.submission.answers)==set(a.template.prompts) for a in assignments if a.submission)

def test_scenario_events_are_supported_and_privacy_is_enforced(tmp_path):
    repo=seed_demo_database(tmp_path/"demo.db"); clock=DemoClock()
    for patient in repo.patients():
        checks=repo.checkins(patient.id); assignments=repo.assignments(patient.id); notes=repo.notes(patient.id); events=repo.events(patient.id)
        sources={c.id for c in checks}|{a.id for a in assignments}
        assert all(e.source_id in sources for e in events)
        candidates=build_bridge_candidates(notes,events,checkins=checks,assignments=assignments)
        private={n.id for n in notes if not n.is_shared}
        assert {"checkin","homework","note","progress_event"}.issubset({c.source_type for c in candidates})
        assert not private & {c.source_id for c in candidates}
        report=build_report(patient.id,clock.now-timedelta(days=21),clock.now,checks,assignments,notes,events)
        assert not private & {n.id for n in report.shared_notes}

    martina=repo.patient(did("martina","patient",0))
    assert any(i.kind=="recurring_trigger" and len(i.source_ids)>=3 for i in derive_progress(repo.checkins(martina.id),repo.events(martina.id)))
    luca=repo.patient(did("luca","patient",0)); luca_events=repo.events(luca.id); luca_checks={c.id:c for c in repo.checkins(luca.id)}
    dinner=next(e for e in luca_events if e.kind==EventKind.STEP_FORWARD)
    assert "cena" in luca_checks[dinner.source_id].trigger and "dolce" in luca_checks[dinner.source_id].behavior

def test_martina_recent_expiry_and_report_points_match_scenario(tmp_path):
    repo=seed_demo_database(tmp_path/"demo.db"); patient=repo.patient(did("martina","patient",0)); clock=DemoClock()
    expired=[a for a in repo.assignments(patient.id) if a.status.value=="expired"]
    assert len(expired)==2 and all((clock.now-a.due_at).days<=14 for a in expired)
    report=build_report(patient.id,clock.now-timedelta(days=21),clock.now,repo.checkins(patient.id),repo.assignments(patient.id),repo.notes(patient.id),repo.events(patient.id))
    assert report.homework_expired==2 and report.previous_stress is not None and report.stress_change>0
    assert any("studio/esami" in point for point in report.points_to_revisit)
