from html import escape

from psyhelper.ui.presentation import patient_summary


def render(st, repo, on_open):
    st.caption("Area professionista · Demo")
    st.title("Buongiorno, Elena")
    st.markdown('<p class="ph-lead">Una vista essenziale su ciò che è cambiato tra una seduta e l’altra.</p>', unsafe_allow_html=True)
    st.write("")
    st.subheader("4 percorsi attivi")
    order = ("Giulia Bianchi", "Luca Ferri", "Martina Romano", "Andrea Conti")
    patients = sorted(repo.patients(), key=lambda p: order.index(p.name))
    for start in range(0, 4, 2):
        cols = st.columns(2, gap="large")
        for col, patient in zip(cols, patients[start:start + 2]):
            summary = patient_summary(repo, patient)
            with col:
                tone = f"ph-{summary.tone}" if summary.tone else ""
                st.markdown(f'''<div class="ph-patient"><div class="ph-eyebrow">{escape(summary.name)} · {summary.age} anni</div><h3>{escape(summary.focus.capitalize())}</h3><p class="ph-focus">{escape(summary.trend)}</p><div class="ph-row"><span class="ph-label">Ultima attività</span><span>{summary.last_activity}</span></div><div class="ph-row"><span class="ph-label">Homework</span><span>{summary.homework}</span></div><div class="ph-row"><span class="ph-label">{summary.highlight_label}</span><span class="{tone}">{escape(summary.highlight)}</span></div></div>''', unsafe_allow_html=True)
                if st.button("Apri percorso →", key=f"open-{patient.id}", use_container_width=True): on_open(patient.id)
        st.write("")
