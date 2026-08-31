from psyhelper.domain.models import BridgeStatus, EventKind
from psyhelper.ui.components import insight, trend_chart
from psyhelper.ui.presentation import italian_date, metric_delta


def render(st, model):
    st.subheader("Da sapere oggi")
    st.caption("Se la seduta fosse tra poco, questi sono gli elementi più recenti da cui partire.")
    metrics, counts = model["metrics"], model["counts"]
    cols = st.columns(4)
    cols[0].metric("Ansia recente", metrics["anxiety"], metric_delta(metrics["anxiety"], metrics["previous_anxiety"]), delta_color="off")
    cols[1].metric("Stress recente", metrics["stress"], metric_delta(metrics["stress"], metrics["previous_stress"]), delta_color="off")
    adherence = round(counts["completed"] / counts["assigned"] * 100) if counts["assigned"] else 0
    cols[2].metric("Homework", f"{adherence}%", f"{counts['completed']} di {counts['assigned']} completati")
    cols[3].metric("Ultima attività", italian_date(model["checkins"][-1].recorded_at, style="short"), "Check-in", delta_color="off")
    st.write("")
    shown = 0
    for event in reversed(model["events"]):
        if event.kind in (EventKind.STEP_FORWARD, EventKind.SETBACK, EventKind.RECURRING_TRIGGER) and shown < 2:
            insight(st, {EventKind.STEP_FORWARD:"Passo avanti", EventKind.SETBACK:"Da riprendere", EventKind.RECURRING_TRIGGER:"Contesto ricorrente"}[event.kind], event.text); shown += 1
    if model["notes"] and shown < 3: insight(st, "Contenuto condiviso", model["notes"][0].text)
    current = next((b for b in reversed(model["bridges"]) if b.status != BridgeStatus.ARCHIVED), None)
    if current and current.status == BridgeStatus.READY and shown < 3: insight(st, "Bridge pronto", "Il paziente ha scelto gli elementi da portare nella prossima seduta.")
    st.subheader("Ultimi 60 giorni")
    trend_chart(st, model["checkins"], compact=True)
    st.caption(f"Ansia media recente {metrics['anxiety']} · periodo precedente {metrics['previous_anxiety']} · Stress recente {metrics['stress']} · periodo precedente {metrics['previous_stress']}")
