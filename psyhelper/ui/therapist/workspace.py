from psyhelper.ui.presentation import patient_read_model
from psyhelper.ui.therapist import homework, journey, overview, pre_session, trends


def render(st, repo, patient_id, route, go_dashboard):
    model = patient_read_model(repo, patient_id)
    patient = model["patient"]
    model["goals"] = repo.goals(patient_id)
    if st.button("← Tutti i percorsi", key="back-main"): go_dashboard()
    weeks = max(1, round((model["checkins"][-1].recorded_at.date() - patient.pathway_started).days / 7))
    st.caption("Area professionista · Demo")
    st.title(patient.name)
    st.caption(f"{patient.age} anni · percorso iniziato il {patient.pathway_started:%d/%m/%Y} · circa {weeks} settimane")
    st.markdown(f"**Focus** · {model['onboarding'].focus.capitalize()}")
    pages = {"oggi":overview.render,"andamento":trends.render,"homework":homework.render,"percorso":journey.render,"prepara":pre_session.render}
    if route == "homework": pages[route](st, repo, model)
    elif route == "prepara": pages[route](st, repo, model)
    else: pages.get(route, overview.render)(st, model)
