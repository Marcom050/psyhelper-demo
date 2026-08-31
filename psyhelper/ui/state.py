THERAPIST_ROUTES = ("oggi", "andamento", "homework", "percorso", "prepara")
PATIENT_ROUTES = ("patient_today", "patient_activities", "patient_journey", "patient_private", "patient_bridge")


def init_state(st):
    st.session_state.setdefault("route", "dashboard")
    st.session_state.setdefault("selected_patient_id", None)
    st.session_state.setdefault("demo_role", "Professionista")


def open_patient(st, patient_id: str):
    st.session_state.selected_patient_id = patient_id
    st.session_state.route = "oggi"


def dashboard(st):
    st.session_state.selected_patient_id = None
    st.session_state.route = "dashboard"


def reset_ui(st):
    for key in tuple(st.session_state):
        st.session_state.pop(key, None)
    init_state(st)


def switch_role(st, role: str):
    st.session_state.demo_role = role
    if role == "Paziente":
        st.session_state.route = "patient_today"
    else:
        st.session_state.route = "oggi" if st.session_state.selected_patient_id else "dashboard"


def select_demo_patient(st, patient_id: str):
    st.session_state.selected_patient_id = patient_id
    st.session_state.route = "patient_today"
