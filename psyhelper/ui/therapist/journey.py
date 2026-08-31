from psyhelper.domain.models import GoalKind, GoalStatus
from psyhelper.ui.components import KIND_LABELS
from psyhelper.ui.presentation import italian_date, significant_events


def render(st, model):
    st.subheader("Percorso")
    st.caption("Obiettivi, passi concordati e momenti significativi in un’unica lettura.")
    st.subheader("Obiettivi e passi concordati")
    for goal in model.get("goals", []):
        label = "Obiettivo" if goal.kind == GoalKind.GOAL else "Passo concordato"
        status = "Raggiunto" if goal.status == GoalStatus.ACHIEVED else "In corso"
        st.markdown(f'<div class="ph-note"><div class="ph-eyebrow">{label}</div><h4>{goal.title}</h4><span>Stato: <strong>{status}</strong></span></div>', unsafe_allow_html=True)
        st.write("")
    st.subheader("Progressi osservati")
    for item in model["insights"]: st.markdown(f"**{KIND_LABELS.get(item.kind, 'Osservazione')}**  \n{item.text}")
    st.subheader("Timeline significativa")
    for event in significant_events(model["events"], model["checkins"]): st.markdown(f"**{italian_date(event.occurred_at)} · {KIND_LABELS.get(event.kind.value, event.kind.value)}**  \n{event.text}")
