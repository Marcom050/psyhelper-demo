from html import escape

import altair as alt

from psyhelper.ui.presentation import italian_date


KIND_LABELS = {
    "improvement": "Miglioramento", "setback": "Da riprendere", "step_forward": "Passo avanti",
    "recurring_trigger": "Contesto ricorrente", "maintained_progress": "Continuità",
}


def eyebrow(st, text):
    st.markdown(f'<div class="ph-eyebrow">{escape(text)}</div>', unsafe_allow_html=True)


def insight(st, label, text):
    st.markdown(f'<div class="ph-insight"><div class="ph-eyebrow">{escape(label)}</div><p>{escape(text)}</p></div>', unsafe_allow_html=True)


def trend_chart(st, checks, compact=False):
    rows = checks[-20:] if compact else checks
    data = [{"Data": c.recorded_at, "Ansia": c.anxiety, "Stress": c.stress,
             "Data italiana": italian_date(c.recorded_at, year=True)} for c in rows]
    base = alt.Chart(alt.Data(values=data)).transform_fold(["Ansia", "Stress"], as_=["Indicatore", "Valore"])
    encoding = dict(
        x=alt.X("Data:T", title=None, axis=alt.Axis(format="%d/%m", grid=False, labelColor="#756f68", tickColor="#d8d1c9")),
        y=alt.Y("Valore:Q", title=None, scale=alt.Scale(domain=[0, 10]), axis=alt.Axis(grid=True, gridColor="#eee9e3", tickCount=6)),
        color=alt.Color("Indicatore:N", scale=alt.Scale(domain=["Ansia", "Stress"], range=["#A35F46", "#65766B"]), legend=alt.Legend(title=None, orient="top")),
    )
    lines = base.mark_line(strokeWidth=1.8).encode(**encoding)
    points = base.mark_point(filled=True, size=52, stroke="white", strokeWidth=1).encode(
        **encoding,
        tooltip=[alt.Tooltip("Data italiana:N", title="Data"), alt.Tooltip("Ansia:Q"), alt.Tooltip("Stress:Q")],
    )
    chart = (lines + points).properties(height=260 if compact else 360).configure_view(stroke=None).configure(background="#ffffff")
    st.altair_chart(chart, use_container_width=True, theme=None)


def homework_answer(st, assignment):
    with st.expander("Vedi risposte"):
        for prompt, answer in assignment.submission.answers.items():
            st.markdown(f'<div class="ph-answer"><strong>{escape(prompt.replace("_", " ").capitalize())}</strong><br>{escape(answer)}</div>', unsafe_allow_html=True)
