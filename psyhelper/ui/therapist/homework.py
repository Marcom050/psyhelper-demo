from datetime import timedelta

from psyhelper.demo.clock import DemoClock
from psyhelper.demo.homework_catalog import HOMEWORK_CATALOG, homework_template
from psyhelper.domain.models import HomeworkStatus
from psyhelper.ui.actions import assign_homework
from psyhelper.ui.components import homework_answer
from psyhelper.ui.presentation import italian_date


DESCRIPTIONS = {
    "ABC":"Osservare il legame tra situazione, pensieri e conseguenze.", "thought_record":"Raccogliere pensieri ed emozioni in un episodio concreto.",
    "cognitive_restructuring":"Esplorare elementi a favore e prospettive alternative.", "graded_exposure":"Concordare un passo graduale e osservarne l'esito.",
    "avoidance_monitoring":"Notare l'impulso a evitare e la scelta compiuta.", "behavioral_activation":"Programmare un'attività significativa e verificarne l'esito.",
    "emotion_trigger":"Riconoscere emozioni, segnali e contesto.", "three_minute_breathing":"Creare una breve pausa di osservazione.",
    "realistic_thought":"Formulare un pensiero più aderente ai fatti.",
}


def render(st, repo, model):
    st.subheader("Homework")
    c = model["counts"]
    cols = st.columns(4)
    for col, label, value in zip(cols, ("Assegnati","Completati","Da completare","Scaduti"), (c["assigned"],c["completed"],c["pending"],c["expired"])): col.metric(label, value)
    if st.button("Assegna attività", type="primary"): st.session_state.assign_open = not st.session_state.get("assign_open", False)
    if st.session_state.get("assign_open"):
        with st.form("assign-homework"):
            slugs = list(HOMEWORK_CATALOG)
            slug = st.selectbox("Attività", slugs, format_func=lambda x: HOMEWORK_CATALOG[x].title)
            st.caption(DESCRIPTIONS[slug])
            due = st.date_input("Scadenza", value=(DemoClock().now + timedelta(days=7)).date(), min_value=DemoClock().now.date())
            if st.form_submit_button("Assegna", type="primary"):
                now = DemoClock().now
                assign_homework(repo, model["patient"].id, homework_template(slug), now, now.replace(year=due.year, month=due.month, day=due.day))
                st.session_state.assign_open = False
                st.success("Attività assegnata.")
                st.rerun()
    st.subheader("Storico attività")
    labels = {HomeworkStatus.COMPLETED:"Completato",HomeworkStatus.PENDING:"Da completare",HomeworkStatus.EXPIRED:"Scaduto"}
    for assignment in reversed(model["assignments"]):
        cols = st.columns([3,1])
        cols[0].markdown(f"**{assignment.template.title}**  \n<span class='ph-meta'>Assegnato {italian_date(assignment.assigned_at)} · Scadenza {italian_date(assignment.due_at)}</span>", unsafe_allow_html=True)
        cols[1].markdown(f'<span class="ph-badge ph-{assignment.status.value}">{labels[assignment.status]}</span>', unsafe_allow_html=True)
        if assignment.submission: homework_answer(st, assignment)
        st.divider()
