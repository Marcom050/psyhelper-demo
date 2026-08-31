from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid5
from datetime import timedelta
from psyhelper.domain.models import *
from .clock import DemoClock

NS=UUID("bf853ec3-31ba-4bc2-9e3e-2c49dd2ec821")
def did(slug, kind, n): return str(uuid5(NS,f"{slug}:{kind}:{n}"))

@dataclass(frozen=True)
class ScenarioExpectation:
    checkins:int; assigned:int; completed:int; expired:int; active_goals:int; achieved_goals:int; private_notes:int; shared_notes:int; current_bridge:BridgeStatus; archived_bridges:int

SPECS={
 "giulia":("Giulia Bianchi",27,"ansia anticipatoria e perfezionismo lavorativo",20,[8,7,8,7,6,7,6,6,5,6,5,5,4,5,4,5,4,4,5,4],[7,8,7,7,6,7,6,5,6,5,5,5,4,5,4,4,5,4,4,4],8,7,1,BridgeStatus.READY,2),
 "luca":("Luca Ferri",31,"evitamento sociale e difficoltà nell'esporsi",18,[7,8,7,7,6,7,7,6,7,6,6,7,6,6,5,6,5,6],[6]*18,7,4,2,BridgeStatus.DRAFT,1),
 "martina":("Martina Romano",24,"stress universitario",20,[5,4,5,5,4,5,5,4,5,5,5,6,5,6,6,7,7,8,7,8],[5,5,4,5,5,5,4,5,5,5,6,6,6,7,7,8,8,9,8,9],8,5,2,BridgeStatus.READY,1),
 "andrea":("Andrea Conti",38,"stress lavorativo e riduzione delle attività gratificanti",18,[6,6,7,6,5,6,5,4,5,4,4,5,4,4,5,5,6,5],[7,6,7,6,5,5,4,5,4,4,4,5,4,5,5,6,6,6],7,5,1,BridgeStatus.DRAFT,2)}

EXPECTATIONS={s:ScenarioExpectation(v[3],v[6],v[7],v[8],1,1,1,1,v[9],v[10]) for s,v in SPECS.items()}

def build_scenario(slug, therapist_id, clock=DemoClock()):
    name,age,desc,count,anx,stress,assigned,completed,expired,current,archived=SPECS[slug]
    patient=Patient(did(slug,"patient",0),therapist_id,name,age,clock.anchor-timedelta(days=60),desc)
    gaps=[59,56,53,49,46,43,39,36,33,29,26,23,20,17,14,12,9,6,3,1][:count]
    trigger="riunione" if slug=="giulia" else "situazione sociale" if slug=="luca" else "studio ed esami" if slug=="martina" else "carico di lavoro"
    checks=[CheckIn(did(slug,"checkin",i),patient.id,clock.days_ago(d),anx[i],stress[i],trigger if i%2==0 else "", "Sono rimasto nella situazione" if slug=="luca" and i>10 else "") for i,d in enumerate(gaps)]
    template=HomeworkTemplate(did(slug,"template",0),"Scheda pensiero-comportamento",("situazione","pensiero","risposta alternativa"))
    homework=[]
    for i in range(assigned):
        at=clock.days_ago(55-i*7); status=HomeworkStatus.COMPLETED if i<completed else HomeworkStatus.EXPIRED if i<completed+expired else HomeworkStatus.PENDING
        sub=HomeworkSubmission(did(slug,"submission",i),did(slug,"homework",i),at.replace(day=at.day) if False else clock.days_ago(52-i*7),{"situazione":trigger,"pensiero":"Potrei non farcela","risposta alternativa":"Posso procedere un passo alla volta"}) if status==HomeworkStatus.COMPLETED else None
        homework.append(HomeworkAssignment(did(slug,"homework",i),patient.id,template,at,clock.days_ago(49-i*7),status,sub))
    goals=[JourneyGoal(did(slug,"goal",0),patient.id,"Fare un passo concreto questa settimana",GoalKind.GOAL,GoalStatus.ACTIVE,clock.days_ago(58),clock.days_ago(5)),JourneyGoal(did(slug,"goal",1),patient.id,"Mantenere un piccolo impegno",GoalKind.COMMITMENT,GoalStatus.ACHIEVED,clock.days_ago(55),clock.days_ago(18))]
    shared="Vorrei parlare dell'esame: faccio fatica ad ammettere quanto mi pesa." if slug=="martina" else "Vorrei riprendere questo episodio nella prossima seduta."
    notes=[PatientNote(did(slug,"note",0),patient.id,shared,clock.days_ago(7),clock.days_ago(6)),PatientNote(did(slug,"note",1),patient.id,"Appunto personale per mettere ordine nei pensieri.",clock.days_ago(4))]
    bridges=[]
    for i in range(archived): bridges.append(SessionBridge(did(slug,"bridge",i),patient.id,clock.days_ago(45-i*16),BridgeStatus.ARCHIVED,[],"Tema discusso in seduta",clock.days_ago(43-i*16)))
    items=[] if current==BridgeStatus.DRAFT else [SessionBridgeItem(did(slug,"bridge-item",0),"note",notes[0].id,"Tema recente da riprendere",10)]
    bridges.append(SessionBridge(did(slug,"bridge",archived),patient.id,clock.days_ago(3),current,items,"Vorrei partire da qui." if items else ""))
    kinds=[EventKind.IMPROVEMENT,EventKind.SETBACK]
    if slug=="luca": kinds.append(EventKind.STEP_FORWARD)
    if slug=="martina": kinds.append(EventKind.RECURRING_TRIGGER)
    events=[TimelineEvent(did(slug,"event",i),patient.id,clock.days_ago(25-i*9),k,"Partecipazione a una cena e permanenza nella situazione" if k==EventKind.STEP_FORWARD else "Cambiamento recente da osservare senza interpretazioni diagnostiche") for i,k in enumerate(kinds)]
    onboarding=PathwayOnboarding(did(slug,"onboarding",0),patient.id,clock.days_ago(58),desc)
    return [patient,*checks,*homework,*goals,*notes,*bridges,*events,onboarding]
