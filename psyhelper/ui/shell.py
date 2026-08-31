from psyhelper.demo.reset import reset_demo_database
from psyhelper.demo.seed import DEFAULT_DB, seed_demo_database
from psyhelper.repository import DemoRepository
from psyhelper.ui import state
from psyhelper.ui.theme import apply_theme
from psyhelper.ui.therapist import dashboard, workspace


def repository():
    return seed_demo_database(DEFAULT_DB) if not DEFAULT_DB.exists() else DemoRepository(DEFAULT_DB)


def render():
    import streamlit as st
    st.set_page_config(page_title="PsyHelper · Area professionista", page_icon="P", layout="wide", initial_sidebar_state="expanded")
    apply_theme(st); state.init_state(st); repo = repository()
    with st.sidebar:
        st.title("PsyHelper")
        st.caption("Area professionista")
        if st.button("Panoramica", use_container_width=True): state.dashboard(st); st.rerun()
        st.caption("I miei percorsi")
        patient = repo.patient(st.session_state.selected_patient_id) if st.session_state.selected_patient_id else None
        if patient:
            st.markdown(f"**{patient.name}**")
            labels = (("oggi","Oggi"),("andamento","Andamento"),("homework","Homework"),("percorso","Percorso"),("prepara","Prepara seduta"))
            for route, label in labels:
                if st.button(label, key=f"nav-{route}", use_container_width=True, type="primary" if st.session_state.route == route else "secondary"):
                    st.session_state.route = route; st.rerun()
        st.write(""); st.write("")
        with st.expander("Impostazioni demo"):
            if not st.session_state.get("confirm_reset"):
                if st.button("Ripristina dati demo"): st.session_state.confirm_reset = True; st.rerun()
            else:
                st.caption("Tutte le modifiche della demo verranno eliminate.")
                if st.button("Conferma ripristino", type="primary"):
                    reset_demo_database(DEFAULT_DB); state.reset_ui(st); st.rerun()
        st.caption("Demo PsyHelper  \nDati completamente fittizi")
    if st.session_state.route == "dashboard" or not st.session_state.selected_patient_id:
        dashboard.render(st, repo, lambda pid: (state.open_patient(st, pid), st.rerun()))
    else:
        workspace.render(st, repo, st.session_state.selected_patient_id, st.session_state.route, lambda: (state.dashboard(st), st.rerun()))
