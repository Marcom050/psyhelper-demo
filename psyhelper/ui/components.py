from html import escape


KIND_LABELS = {
    "improvement": "Miglioramento", "setback": "Da riprendere", "step_forward": "Passo avanti",
    "recurring_trigger": "Contesto ricorrente", "maintained_progress": "Continuità",
}


def eyebrow(st, text):
    st.markdown(f'<div class="ph-eyebrow">{escape(text)}</div>', unsafe_allow_html=True)


def insight(st, label, text):
    st.markdown(f'<div class="ph-insight"><div class="ph-eyebrow">{escape(label)}</div><p>{escape(text)}</p></div>', unsafe_allow_html=True)


def metric_delta(value, previous):
    if value is None or previous is None: return "Confronto non disponibile"
    delta = round(value - previous, 1)
    if abs(delta) < .1: return "In linea con il periodo precedente"
    return f"{abs(delta):.1f} punti {'in meno' if delta < 0 else 'in più'} rispetto a prima"


def trend_chart(st, checks, compact=False):
    rows = checks[-20:] if compact else checks
    data = [{"Data": c.recorded_at, "Ansia": c.anxiety, "Stress": c.stress} for c in rows]
    st.line_chart(data, x="Data", y=["Ansia", "Stress"], color=["#A35F46", "#65766B"], height=290 if compact else 390)


def homework_answer(st, assignment):
    with st.expander("Vedi risposte"):
        for prompt, answer in assignment.submission.answers.items():
            st.markdown(f"**{prompt.replace('_', ' ').capitalize()}**")
            st.write(answer)
