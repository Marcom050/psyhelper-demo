from psyhelper.ui.components import KIND_LABELS, insight, trend_chart
from psyhelper.ui.presentation import italian_date, significant_events


def render(st, model):
    st.subheader("Andamento nel tempo")
    st.caption("I punti corrispondono ai check-in registrati dal paziente.")
    trend_chart(st, model["checkins"])
    st.subheader("Cosa è cambiato")
    for item in model["insights"]: insight(st, KIND_LABELS.get(item.kind, "Osservazione"), item.text)
    st.subheader("Timeline significativa")
    for event in significant_events(model["events"], model["checkins"]):
        st.markdown(f'<div class="ph-timeline"><div class="ph-eyebrow">{italian_date(event.occurred_at, year=True)} · {KIND_LABELS.get(event.kind.value, event.kind.value)}</div><p>{event.text}</p></div>', unsafe_allow_html=True)
    st.subheader("Check-in recenti")
    for check in reversed(model["checkins"][-6:]):
        title = f"{italian_date(check.recorded_at)} · Ansia {check.anxiety} · Stress {check.stress} · {check.trigger.capitalize()}"
        with st.expander(title):
            compact = (("Emozione", check.mood), ("Intensità", check.mood_intensity), ("Trigger", check.trigger), ("Sensazioni corporee", check.body_sensations))
            values = [(label, value) for label, value in compact if value not in (None, "")]
            for index in range(0, len(values), 2):
                cols = st.columns(2)
                for col, (label, value) in zip(cols, values[index:index + 2]): col.markdown(f"**{label}**  \n{value}")
            for label, value in (("Pensiero automatico", check.automatic_thought), ("Comportamento", check.behavior), ("Risposta alternativa", check.alternative_response), ("Nota per il terapeuta", check.note_for_therapist)):
                if value not in (None, ""): st.markdown(f"**{label}**  \n{value}")
