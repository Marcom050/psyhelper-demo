from pathlib import Path
from psyhelper.domain.models import Therapist, HomeworkStatus, GoalStatus, BridgeStatus
from psyhelper.repository import DemoRepository
from .scenarios import build_scenario, EXPECTATIONS, did

DEFAULT_DB=Path(__file__).resolve().parents[2]/"data"/"psyhelper-demo.sqlite3"

def validate_demo(repo):
    patients=repo.patients()
    if len(patients)!=4: raise ValueError("The demo must contain exactly four patients")
    for slug, expected in EXPECTATIONS.items():
        patient=next(p for p in patients if p.id==did(slug,"patient",0))
        hw=repo.assignments(patient.id); goals=repo.goals(patient.id); notes=repo.notes(patient.id); bridges=repo.bridges(patient.id)
        actual=(len(repo.checkins(patient.id)),len(hw),sum(x.status==HomeworkStatus.COMPLETED for x in hw),sum(x.status==HomeworkStatus.EXPIRED for x in hw),sum(x.status==GoalStatus.ACTIVE for x in goals),sum(x.status==GoalStatus.ACHIEVED for x in goals),sum(not x.is_shared for x in notes),sum(x.is_shared for x in notes),next(x.status for x in reversed(bridges) if x.status!=BridgeStatus.ARCHIVED),sum(x.status==BridgeStatus.ARCHIVED for x in bridges))
        if actual != tuple(expected.__dict__.values()): raise ValueError(f"Invalid scenario {slug}: {actual}")

def seed_demo_database(path=DEFAULT_DB):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    repo=DemoRepository(path); repo.create_schema(); repo.clear()
    therapist=Therapist(did("demo","therapist",0),"Dott.ssa Elena Riva"); repo.save(therapist)
    for slug in EXPECTATIONS:
        for entity in build_scenario(slug,therapist.id): repo.save(entity)
    validate_demo(repo)
    return repo

if __name__=="__main__": seed_demo_database()
