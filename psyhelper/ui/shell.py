from psyhelper.demo.reset import reset_demo_database
from psyhelper.demo.seed import DEFAULT_DB, seed_demo_database
from psyhelper.repository import DemoRepository
from psyhelper.ui import state
from psyhelper.ui.theme import apply_theme
from psyhelper.ui.therapist import dashboard, workspace
from psyhelper.ui.patient import workspace as patient_workspace


def repository():
    return seed_demo_database(DEFAULT_DB) if not DEFAULT_DB.exists() else DemoRepository(DEFAULT_DB)


def render():
    import streamlit as st
    st.set_page_config(page_title="PsyHelper", page_icon="P", layout="wide", initial_sidebar_state="expanded")
    apply_theme(st); state.init_state(st); repo = repository()
    if st.session_state.demo_role == "Paziente" and not st.session_state.selected_patient_id:
        first = next((p for p in repo.patients() if p.name.startswith("Luca")), repo.patients()[0])
        st.session_state.selected_patient_id = first.id
    with st.sidebar:
        st.title("PsyHelper")
        st.caption("Area personale" if st.session_state.demo_role == "Paziente" else "Area professionista")
        patient = repo.patient(st.session_state.selected_patient_id) if st.session_state.selected_patient_id else None
        if st.session_state.demo_role == "Paziente":
            labels = (("patient_today","Oggi"),("patient_activities","Attività"),("patient_journey","Percorso"),("patient_private","Area privata"),("patient_bridge","Prepara la seduta"))
            for route, label in labels:
                if st.button(label, key=f"nav-{route}", use_container_width=True, type="primary" if st.session_state.route == route else "secondary"):
                    st.session_state.route = route
        else:
            if st.button("Panoramica", use_container_width=True): state.dashboard(st)
            st.caption("I miei percorsi")
            if patient:
                st.markdown(f"**{patient.name}**")
                labels = (("oggi","Oggi"),("andamento","Andamento"),("homework","Homework"),("percorso","Percorso"),("prepara","Prepara seduta"))
                for route, label in labels:
                    if st.button(label, key=f"nav-{route}", use_container_width=True, type="primary" if st.session_state.route == route else "secondary"):
                        st.session_state.route = route
        st.write(""); st.write("")
        with st.expander("Impostazioni demo"):
            role = st.radio("Cambia vista demo", ("Professionista", "Paziente"),
                            index=0 if st.session_state.demo_role == "Professionista" else 1)
            if role != st.session_state.demo_role:
                state.switch_role(st, role); st.rerun()
            if role == "Paziente":
                patients = repo.patients(); ids = [p.id for p in patients]
                selected = st.selectbox("Paziente demo", ids, index=ids.index(st.session_state.selected_patient_id),
                                        format_func=lambda pid: repo.patient(pid).name)
                if selected != st.session_state.selected_patient_id:
                    state.select_demo_patient(st, selected); st.rerun()
            if not st.session_state.get("confirm_reset"):
                if st.button("Ripristina dati demo"): st.session_state.confirm_reset = True; st.rerun()
            else:
                st.caption("Tutte le modifiche della demo verranno eliminate.")
                if st.button("Conferma ripristino", type="primary"):
                    reset_demo_database(DEFAULT_DB); state.reset_ui(st); st.rerun()
        st.caption("Demo PsyHelper  \nDati completamente fittizi")
    if st.session_state.demo_role == "Paziente":
        patient_workspace.render(st, repo, st.session_state.selected_patient_id, st.session_state.route)
    elif st.session_state.route == "dashboard" or not st.session_state.selected_patient_id:
        dashboard.render(st, repo, lambda pid: (state.open_patient(st, pid), st.rerun()))
    else:
        workspace.render(st, repo, st.session_state.selected_patient_id, st.session_state.route, lambda: (state.dashboard(st), st.rerun()))
