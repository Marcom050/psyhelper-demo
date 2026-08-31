ROUTES = ("oggi", "andamento", "homework", "percorso", "prepara")


def init_state(st):
    st.session_state.setdefault("route", "dashboard")
    st.session_state.setdefault("selected_patient_id", None)


def open_patient(st, patient_id: str):
    st.session_state.selected_patient_id = patient_id
    st.session_state.route = "oggi"


def dashboard(st):
    st.session_state.selected_patient_id = None
    st.session_state.route = "dashboard"


def reset_ui(st):
    for key in ("selected_patient_id", "route", "confirm_reset", "assign_open"):
        st.session_state.pop(key, None)
    init_state(st)
