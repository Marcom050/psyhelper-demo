import hashlib
from psyhelper.demo.seed import seed_demo_database, validate_demo
from psyhelper.demo.reset import reset_demo_database
from psyhelper.demo.scenarios import EXPECTATIONS

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
