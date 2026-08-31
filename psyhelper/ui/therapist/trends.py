from psyhelper.ui.components import KIND_LABELS, insight, trend_chart


def render(st, model):
    st.subheader("Andamento nel tempo")
    st.caption("I punti corrispondono ai check-in registrati dal paziente.")
    trend_chart(st, model["checkins"])
    st.subheader("Cosa è cambiato")
    for item in model["insights"]: insight(st, KIND_LABELS.get(item.kind, "Osservazione"), item.text)
    st.subheader("Timeline significativa")
    for event in reversed(model["events"]):
        st.markdown(f'<div class="ph-timeline"><div class="ph-eyebrow">{event.occurred_at:%d %B %Y} · {KIND_LABELS.get(event.kind.value, event.kind.value)}</div><p>{event.text}</p></div>', unsafe_allow_html=True)
    st.subheader("Check-in recenti")
    for check in reversed(model["checkins"][-6:]):
        title = f"{check.recorded_at:%d %B} · Ansia {check.anxiety} · Stress {check.stress} · {check.trigger.capitalize()}"
        with st.expander(title):
            fields = (("Emozione", check.mood), ("Intensità", check.mood_intensity), ("Trigger", check.trigger), ("Pensiero automatico", check.automatic_thought), ("Comportamento", check.behavior), ("Sensazioni corporee", check.body_sensations), ("Risposta alternativa", check.alternative_response), ("Nota per il terapeuta", check.note_for_therapist))
            for label, value in fields:
                if value not in (None, ""): st.markdown(f"**{label}**  \n{value}")
