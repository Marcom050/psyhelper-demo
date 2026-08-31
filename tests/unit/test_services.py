from datetime import datetime, timedelta
import pytest
from psyhelper.domain.models import *
from psyhelper.services.core import *

NOW=datetime(2026,8,31,12)

def test_homework_complete_validation_and_expiry():
    t=HomeworkTemplate("t","CBT",("a","b")); a=HomeworkAssignment("a","p",t,NOW-timedelta(days=3),NOW-timedelta(days=1))
    with pytest.raises(ValueError): submit_homework(a,{"a":"ok"},NOW)
    submit_homework(a,{"a":"ok","b":"complete"},NOW)
    assert a.status==HomeworkStatus.COMPLETED and a.submission.answers["b"]=="complete"
    expired=HomeworkAssignment("e","p",t,NOW-timedelta(days=3),NOW-timedelta(days=1))
    assert expire_homework(expired,NOW).status==HomeworkStatus.EXPIRED

def test_private_note_share_revoke_and_candidates():
    note=PatientNote("n","p","privata",NOW)
    assert therapist_notes([note])==[] and build_bridge_candidates([note],[])==[]
    share_note(note,NOW+timedelta(minutes=1)); assert therapist_notes([note])==[note]
    assert build_bridge_candidates([note],[])[0].source_id=="n"
    revoke_note(note,NOW+timedelta(minutes=2)); assert therapist_notes([note])==[]

def test_bridge_lifecycle_and_new_cycle():
    b=SessionBridge("b","p",NOW)
    for status in (BridgeStatus.READY,BridgeStatus.REVIEWED,BridgeStatus.ARCHIVED): transition_bridge(b,status,NOW)
    new=SessionBridge("new","p",NOW+timedelta(days=1))
    assert b.status==BridgeStatus.ARCHIVED and new.status==BridgeStatus.DRAFT and new.id!=b.id

def test_goal_update_and_achieve():
    g=JourneyGoal("g","p","Prima",GoalKind.GOAL,GoalStatus.ACTIVE,NOW,NOW)
    update_goal(g,"Aggiornato",NOW+timedelta(hours=1)); achieve_goal(g,NOW+timedelta(hours=2))
    assert g.title=="Aggiornato" and g.status==GoalStatus.ACHIEVED

def checks(values): return [CheckIn(str(i),"p",NOW+timedelta(days=i),v,v) for i,v in enumerate(values)]

def test_progress_variants_and_step_forward():
    assert derive_progress(checks([8,7,8,5,4,4]),[])[0].kind=="improvement"
    assert derive_progress(checks([3,4,3,6,7,7]),[])[0].kind=="setback"
    event=TimelineEvent("e","p",NOW,EventKind.STEP_FORWARD,"Cena")
    assert any(x.kind=="step_forward" for x in derive_progress(checks([6]*6),[event]))
    assert derive_progress(checks([5,5]),[])[0].kind=="insufficient_data"

def test_report_excludes_private_notes_and_has_metrics():
    shared=PatientNote("s","p","visibile",NOW,shared_at=NOW); private=PatientNote("x","p","segreta",NOW)
    t=HomeworkTemplate("t","x",("a",)); a=HomeworkAssignment("a","p",t,NOW,NOW+timedelta(days=1)); submit_homework(a,{"a":"risposta"},NOW)
    r=build_report("p",NOW-timedelta(days=1),NOW+timedelta(days=1),checks([5]),[a],[shared,private],[])
    assert (r.homework_assigned,r.homework_completed,r.recent_anxiety)==(1,1,5)
    assert [n.text for n in r.shared_notes]==["visibile"] and r.recent_answers
