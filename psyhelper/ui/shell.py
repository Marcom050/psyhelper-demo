from psyhelper.demo.reset import reset_demo_database
from psyhelper.demo.seed import DEFAULT_DB, seed_demo_database
from psyhelper.demo.clock import DemoClock
from psyhelper.repository import DemoRepository
from psyhelper.ui import state
from psyhelper.ui.theme import apply_theme
from psyhelper.ui.presentation import italian_date
from psyhelper.ui.therapist import dashboard, workspace
from psyhelper.ui.patient import workspace as patient_workspace


def repository():
    return seed_demo_database(DEFAULT_DB) if not DEFAULT_DB.exists() else DemoRepository(DEFAULT_DB)


def render():
    import streamlit as st
    st.set_page_config(page_title="PsyHelper Demo", page_icon="P", layout="wide", initial_sidebar_state="expanded")
    apply_theme(st); state.init_state(st); repo = repository()
    if st.session_state.demo_role == "Paziente" and not st.session_state.selected_patient_id:
        first = next((p for p in repo.patients() if p.name.startswith("Luca")), repo.patients()[0])
        st.session_state.selected_patient_id = first.id
    with st.sidebar:
        st.title("PsyHelper")
        st.caption("Area personale" if st.session_state.demo_role == "Paziente" else "Area professionista")
        st.markdown('<span class="ph-badge">DEMO · DATI FITTIZI</span>', unsafe_allow_html=True)
        st.write("")
        patient = repo.patient(st.session_state.selected_patient_id) if st.session_state.selected_patient_id else None
        if st.session_state.demo_role == "Paziente":
            st.markdown(f"**{patient.name}**")
            labels = (("patient_today","Oggi"),("patient_activities","Attività"),("patient_journey","Percorso"),("patient_private","Area privata"),("patient_bridge","Prepara la seduta"))
            for route, label in labels:
                st.button(label, key=f"nav-{route}", use_container_width=True,
                          type="primary" if st.session_state.route == route else "secondary",
                          on_click=state.set_route, args=(st, route))
        else:
            st.button("Panoramica", key="nav-dashboard", use_container_width=True,
                      type="primary" if st.session_state.route == "dashboard" else "secondary",
                      on_click=state.dashboard, args=(st,))
            st.caption("I miei percorsi")
            if patient:
                st.markdown(f"**{patient.name}**")
                labels = (("oggi","Oggi"),("andamento","Andamento"),("homework","Homework"),("percorso","Percorso"),("prepara","Prepara seduta"))
                for route, label in labels:
                    st.button(label, key=f"nav-{route}", use_container_width=True,
                              type="primary" if st.session_state.route == route else "secondary",
                              on_click=state.set_route, args=(st, route))
        st.divider()
        if patient:
            target = "Professionista" if st.session_state.demo_role == "Paziente" else "Paziente"
            st.button(f"Vedi come {target.lower()}", key="switch-demo-view", use_container_width=True,
                      on_click=state.switch_role, args=(st, target))
        with st.expander("Impostazioni demo"):
            role = st.radio("Cambia vista demo", ("Professionista", "Paziente"),
                            key="demo_role", on_change=state.role_changed, args=(st,))
            st.caption("Le due viste condividono lo stesso percorso fittizio. Il cambio vista non è un'autenticazione.")
            st.caption(f"Data dello scenario: {italian_date(DemoClock().anchor, year=True)}. Le date restano fisse durante la dimostrazione.")
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
                if st.button("Annulla ripristino"):
                    st.session_state.confirm_reset = False; st.rerun()
        st.caption("Demo PsyHelper  \nDati completamente fittizi")
    notice = st.session_state.pop("demo_notice", None)
    if notice:
        st.success(notice)
    if st.session_state.demo_role == "Paziente":
        patient_workspace.render(st, repo, st.session_state.selected_patient_id, st.session_state.route)
    elif st.session_state.route == "dashboard" or not st.session_state.selected_patient_id:
        dashboard.render(st, repo, lambda pid: (state.open_patient(st, pid), st.rerun()))
    else:
        workspace.render(st, repo, st.session_state.selected_patient_id, st.session_state.route, lambda: (state.dashboard(st), st.rerun()))
