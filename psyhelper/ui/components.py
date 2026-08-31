from html import escape

import altair as alt

from psyhelper.ui.presentation import italian_date, metric_delta_model, trend_dataset


KIND_LABELS = {
    "improvement": "Miglioramento", "setback": "Da riprendere", "step_forward": "Passo avanti",
    "recurring_trigger": "Contesto ricorrente", "maintained_progress": "Continuità",
}


def eyebrow(st, text):
    st.markdown(f'<div class="ph-eyebrow">{escape(text)}</div>', unsafe_allow_html=True)


def insight(st, label, text):
    st.markdown(f'<div class="ph-insight"><div class="ph-eyebrow">{escape(label)}</div><p>{escape(text)}</p></div>', unsafe_allow_html=True)


def semantic_metric(st, label, value, current, previous):
    delta = metric_delta_model(current, previous)
    st.markdown(
        f'<div class="ph-semantic-metric"><span>{escape(label)}</span>'
        f'<strong>{escape(str(value))}</strong>'
        f'<small class="ph-delta-{delta.tone}">{escape(delta.text)}</small></div>',
        unsafe_allow_html=True,
    )


def trend_chart(st, checks, compact=False):
    data = trend_dataset(checks, limit=20 if compact else None)
    if not data:
        st.info("Non ci sono ancora abbastanza check-in per mostrare l'andamento.")
        return None
    base = alt.Chart(alt.Data(values=data))
    encoding = dict(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%d/%m", grid=False, labelColor="#756f68", tickColor="#d8d1c9")),
        y=alt.Y("value:Q", title=None, scale=alt.Scale(domain=[0, 10]), axis=alt.Axis(grid=True, gridColor="#eee9e3", tickCount=6)),
        color=alt.Color("metric:N", scale=alt.Scale(domain=["Ansia", "Stress"], range=["#A35F46", "#65766B"]), legend=alt.Legend(title=None, orient="top")),
    )
    lines = base.mark_line(strokeWidth=1.8).encode(**encoding)
    points = base.mark_point(filled=True, size=52, stroke="white", strokeWidth=1).encode(
        **encoding,
        tooltip=[alt.Tooltip("date:T", title="Data", format="%d/%m/%Y"), alt.Tooltip("metric:N", title="Indicatore"), alt.Tooltip("value:Q", title="Valore")],
    )
    chart = (lines + points).properties(height=260 if compact else 360).configure_view(stroke=None).configure(background="#ffffff")
    st.altair_chart(chart, use_container_width=True, theme=None)
    return chart


def homework_answer(st, assignment):
    with st.expander("Vedi risposte"):
        for prompt, answer in assignment.submission.answers.items():
            st.markdown(f'<div class="ph-answer"><strong>{escape(prompt.replace("_", " ").capitalize())}</strong><br>{escape(answer)}</div>', unsafe_allow_html=True)
