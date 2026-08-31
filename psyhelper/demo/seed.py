from pathlib import Path
from psyhelper.domain.models import Therapist, HomeworkStatus, GoalStatus, BridgeStatus
from psyhelper.repository import DemoRepository
from .scenarios import build_scenario, EXPECTATIONS, did
from psyhelper.services.core import build_bridge_candidates, build_report, derive_progress
from .clock import DemoClock
from datetime import timedelta

DEFAULT_DB=Path(__file__).resolve().parents[2]/"data"/"psyhelper-demo.sqlite3"

def validate_demo(repo):
    patients=repo.patients()
    if len(patients)!=4: raise ValueError("The demo must contain exactly four patients")
    for slug, expected in EXPECTATIONS.items():
        patient=next(p for p in patients if p.id==did(slug,"patient",0))
        hw=repo.assignments(patient.id); goals=repo.goals(patient.id); notes=repo.notes(patient.id); bridges=repo.bridges(patient.id)
        actual=(len(repo.checkins(patient.id)),len(hw),sum(x.status==HomeworkStatus.COMPLETED for x in hw),sum(x.status==HomeworkStatus.EXPIRED for x in hw),sum(x.status==GoalStatus.ACTIVE for x in goals),sum(x.status==GoalStatus.ACHIEVED for x in goals),sum(not x.is_shared for x in notes),sum(x.is_shared for x in notes),next(x.status for x in reversed(bridges) if x.status!=BridgeStatus.ARCHIVED),sum(x.status==BridgeStatus.ARCHIVED for x in bridges))
        if actual != tuple(expected.__dict__.values()): raise ValueError(f"Invalid scenario {slug}: {actual}")
        if len({a.template.id for a in hw}) < 2: raise ValueError(f"Scenario {slug} uses only one Homework template")
        checks, events = repo.checkins(patient.id), repo.events(patient.id)
        valid_sources = {c.id for c in checks} | {a.id for a in hw}
        if any(e.source_id and e.source_id not in valid_sources for e in events): raise ValueError(f"Unlinked event in {slug}")
        candidates = build_bridge_candidates(notes, events, checkins=checks, assignments=hw)
        private_ids = {n.id for n in notes if not n.is_shared}
        if any(c.source_id in private_ids for c in candidates): raise ValueError(f"Private note in Bridge for {slug}")
        clock = DemoClock()
        report = build_report(patient.id, clock.now-timedelta(days=21), clock.now, checks, hw, notes, events)
        if any(n.id in private_ids for n in report.shared_notes): raise ValueError(f"Private note in report for {slug}")
        if slug == "martina" and not any(i.kind == "recurring_trigger" for i in derive_progress(checks, events)):
            raise ValueError("Martina recurring trigger is not data-derived")

def seed_demo_database(path=DEFAULT_DB):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    repo=DemoRepository(path); repo.create_schema(); repo.clear()
    therapist=Therapist(did("demo","therapist",0),"Dott.ssa Elena Riva"); repo.save(therapist)
    for slug in EXPECTATIONS:
        for entity in build_scenario(slug,therapist.id): repo.save(entity)
    validate_demo(repo)
    return repo

if __name__=="__main__": seed_demo_database()
