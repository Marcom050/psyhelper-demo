from psyhelper.demo.seed import DEFAULT_DB, seed_demo_database
from psyhelper.domain.models import HomeworkStatus, BridgeStatus
from psyhelper.services.core import therapist_notes

def render():
    import streamlit as st
    repo=seed_demo_database(DEFAULT_DB) if not DEFAULT_DB.exists() else __import__("psyhelper.repository",fromlist=["DemoRepository"]).DemoRepository(DEFAULT_DB)
    st.title("PsyHelper Demo")
    patients=sorted(repo.patients(),key=lambda p:p.name)
    patient=next(p for p in patients if p.name==st.selectbox("Paziente",[p.name for p in patients]))
    checks=repo.checkins(patient.id); hw=repo.assignments(patient.id); bridges=repo.bridges(patient.id)
    recent=checks[-3:]
    st.subheader(patient.name)
    st.write(f"Percorso: {(checks[-1].recorded_at.date()-patient.pathway_started).days} giorni")
    cols=st.columns(4)
    cols[0].metric("Check-in",len(checks)); cols[1].metric("Ansia recente",round(sum(c.anxiety for c in recent)/len(recent),1)); cols[2].metric("Stress recente",round(sum(c.stress for c in recent)/len(recent),1)); cols[3].metric("Homework",f"{sum(a.status==HomeworkStatus.COMPLETED for a in hw)}/{len(hw)}")
    current=next(b for b in reversed(bridges) if b.status!=BridgeStatus.ARCHIVED)
    st.write(f"Bridge: **{current.status.value}** · storico archiviato: {sum(b.status==BridgeStatus.ARCHIVED for b in bridges)}")
    st.subheader("Note condivise"); [st.write(f"• {n.text}") for n in therapist_notes(repo.notes(patient.id))]
    st.subheader("Eventi recenti"); [st.write(f"• {e.occurred_at:%d/%m}: {e.text}") for e in repo.events(patient.id)[-5:]]
