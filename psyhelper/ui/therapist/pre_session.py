from psyhelper.domain.models import BridgeStatus
from psyhelper.ui.actions import advance_bridge
from psyhelper.ui.components import KIND_LABELS, homework_answer, insight, metric_delta
from psyhelper.demo.clock import DemoClock


def render(st, repo, model):
    report = model["report"]
    st.subheader("Prepara la prossima seduta")
    st.markdown('<p class="ph-lead">Una sintesi descrittiva di ciò che è emerso tra una seduta e l’altra.</p>', unsafe_allow_html=True)
    st.subheader("Cosa è cambiato")
    for item in model["insights"][:4]: insight(st, KIND_LABELS.get(item.kind, "Osservazione"), item.text)
    st.subheader("Homework")
    cols = st.columns(5)
    values = (report.homework_assigned, report.homework_completed, report.homework_pending, report.homework_expired, f"{report.homework_adherence}%" if report.homework_adherence is not None else "—")
    for col, label, value in zip(cols, ("Assegnati","Completati","Da completare","Scaduti","Aderenza"), values): col.metric(label, value)
    st.subheader("Risposte recenti")
    completed = [a for a in reversed(model["assignments"]) if a.submission][:3]
    for assignment in completed:
        st.markdown(f"**{assignment.template.title}** · completato il {assignment.submission.submitted_at:%d/%m}")
        homework_answer(st, assignment)
    st.subheader("Wellness recente")
    cols = st.columns(2)
    cols[0].metric("Ansia", report.recent_anxiety, metric_delta(report.recent_anxiety, report.previous_anxiety))
    cols[1].metric("Stress", report.recent_stress, metric_delta(report.recent_stress, report.previous_stress))
    st.subheader("Contenuti condivisi")
    st.caption("Condivisi dal paziente per la seduta")
    if not report.shared_notes: st.write("Nessun contenuto condiviso in questa finestra.")
    for note in report.shared_notes: st.markdown(f'<div class="ph-note">“{note.text}”<br><small>Condiviso il {note.shared_at:%d/%m/%Y}</small></div>', unsafe_allow_html=True)
    st.subheader("Punti da riprendere")
    if report.points_to_revisit:
        for point in report.points_to_revisit[:5]: st.markdown(f"- {point}")
    else: st.write("Nessun nuovo punto emerso nella finestra recente.")
    render_bridge(st, repo, model)
    st.markdown(f'<div class="ph-disclaimer">{report.disclaimer}</div>', unsafe_allow_html=True)


def render_bridge(st, repo, model):
    st.subheader("Bridge di seduta")
    current = next((b for b in reversed(model["bridges"]) if b.status != BridgeStatus.ARCHIVED), None)
    if not current: st.write("Il Bridge non è ancora stato avviato."); return
    labels = {BridgeStatus.DRAFT:"In preparazione",BridgeStatus.READY:"Bridge pronto per la seduta",BridgeStatus.REVIEWED:"Bridge discusso"}
    st.markdown(f"**{labels[current.status]}**")
    for item in sorted(current.items, key=lambda x: -x.priority): st.markdown(f"- {item.title}{' · priorità' if item.priority == max(i.priority for i in current.items) else ''}")
    if current.optional_text: st.write(current.optional_text)
    if current.status == BridgeStatus.READY and st.button("Segna come discusso", type="primary"):
        advance_bridge(repo, current, DemoClock().now); st.rerun()
    if current.status == BridgeStatus.REVIEWED and st.button("Archivia Bridge", type="primary"):
        advance_bridge(repo, current, DemoClock().now); st.rerun()
