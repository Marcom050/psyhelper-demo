from psyhelper.domain.models import BridgeStatus
from psyhelper.ui.actions import advance_bridge
from psyhelper.ui.components import KIND_LABELS, homework_answer, insight
from psyhelper.demo.clock import DemoClock
from psyhelper.ui.presentation import distinct_revisit_points, italian_date, metric_delta


def render(st, repo, model):
    report = model["report"]
    st.subheader("Prepara la prossima seduta")
    st.markdown('<p class="ph-lead">Una sintesi descrittiva di ciò che è emerso tra una seduta e l’altra.</p>', unsafe_allow_html=True)
    changed, bridge = st.columns([1.85, 1], gap="large")
    with changed:
        st.subheader("Cosa è cambiato")
        for item in model["insights"][:4]: insight(st, KIND_LABELS.get(item.kind, "Osservazione"), item.text)
    with bridge:
        render_bridge(st, repo, model)
    st.subheader("Homework")
    adherence = f"{str(report.homework_adherence).replace('.', ',')}% completati" if report.homework_adherence is not None else "Nessuna attività recente"
    st.markdown(f'<div class="ph-adherence"><strong>{adherence}</strong><span>{report.homework_assigned} assegnati · {report.homework_completed} completati · {report.homework_pending} da completare · {report.homework_expired} scaduti</span></div>', unsafe_allow_html=True)
    st.subheader("Risposte recenti")
    completed = [a for a in reversed(model["assignments"]) if a.submission][:3]
    for assignment in completed:
        st.markdown(f"**{assignment.template.title}** · completato il {italian_date(assignment.submission.submitted_at, style='short')}")
        homework_answer(st, assignment)
    st.subheader("Wellness recente")
    cols = st.columns(2)
    cols[0].metric("Ansia", report.recent_anxiety, metric_delta(report.recent_anxiety, report.previous_anxiety), delta_color="off")
    cols[1].metric("Stress", report.recent_stress, metric_delta(report.recent_stress, report.previous_stress), delta_color="off")
    st.subheader("Contenuti condivisi")
    st.caption("Condivisi dal paziente per la seduta")
    if not report.shared_notes: st.write("Nessun contenuto condiviso in questa finestra.")
    for note in report.shared_notes: st.markdown(f'<div class="ph-note">“{note.text}”<br><small>Condiviso il {italian_date(note.shared_at, year=True)}</small></div>', unsafe_allow_html=True)
    st.subheader("Punti da riprendere")
    displayed = [item.text for item in model["insights"][:4]]
    points = distinct_revisit_points(report, displayed)
    if points:
        for point in points[:5]: st.markdown(f"- {point}")
    else: st.write("Nessun nuovo punto emerso nella finestra recente.")
    st.markdown(f'<div class="ph-disclaimer">{report.disclaimer}</div>', unsafe_allow_html=True)


def render_bridge(st, repo, model):
    st.markdown('<div class="ph-eyebrow">Session Bridge</div>', unsafe_allow_html=True)
    current = next((b for b in reversed(model["bridges"]) if b.status != BridgeStatus.ARCHIVED), None)
    if not current: st.write("Il Bridge non è ancora stato avviato."); return
    labels = {BridgeStatus.DRAFT:"Bridge in preparazione",BridgeStatus.READY:"BRIDGE PRONTO",BridgeStatus.REVIEWED:"Bridge discusso"}
    st.markdown(f"### {labels[current.status]}")
    if current.status == BridgeStatus.READY:
        st.caption("Il paziente ha preparato alcuni elementi per la seduta.")
    if current.items: st.caption(f"{len(current.items)} elementi · priorità {max(i.priority for i in current.items)}")
    for item in sorted(current.items, key=lambda x: -x.priority): st.markdown(f"- {item.title}{' · priorità' if item.priority == max(i.priority for i in current.items) else ''}")
    if current.optional_text: st.write(current.optional_text)
    if current.status == BridgeStatus.READY and st.button("Segna come discusso", type="primary"):
        advance_bridge(repo, current, DemoClock().now); st.rerun()
    if current.status == BridgeStatus.REVIEWED and st.button("Archivia Bridge", type="primary"):
        advance_bridge(repo, current, DemoClock().now); st.rerun()
