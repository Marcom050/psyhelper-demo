from html import escape

from psyhelper.domain.models import BridgeStatus
from psyhelper.ui.actions import advance_bridge
from psyhelper.ui.components import KIND_LABELS, bridge_items, homework_answer, insight
from psyhelper.demo.clock import DemoClock
from psyhelper.ui.presentation import distinct_revisit_points, italian_date, metric_delta


def render(st, repo, model):
    report = model["report"]
    st.subheader("Prepara la prossima seduta")
    st.markdown('<p class="ph-lead">Una sintesi descrittiva di ciò che è emerso tra una seduta e l’altra.</p>', unsafe_allow_html=True)
    st.caption(f"Riepilogo dal {italian_date(report.window_start)} al {italian_date(report.window_end, year=True)}. I contenuti condivisi per la seduta restano disponibili finché il paziente li condivide.")
    changed, bridge = st.columns([1.85, 1], gap="large")
    with changed:
        st.subheader("Osservazioni sul percorso")
        st.caption("Dai check-in dell'intero percorso: confronti descrittivi e contesti ricorrenti.")
        for item in model["insights"][:4]: insight(st, KIND_LABELS.get(item.kind, "Osservazione"), item.text)
    with bridge:
        render_bridge(st, repo, model)
    st.subheader("Homework")
    adherence = f"{str(report.homework_adherence).replace('.', ',')}% completati" if report.homework_adherence is not None else "Nessuna attività recente"
    st.markdown(f'<div class="ph-adherence"><strong>{adherence}</strong><span>{report.homework_assigned} assegnati · {report.homework_completed} completati · {report.homework_pending} da completare · {report.homework_expired} scaduti</span></div>', unsafe_allow_html=True)
    st.subheader("Risposte recenti")
    completed = sorted((a for a in model["assignments"] if a.submission and report.window_start <= a.submission.submitted_at <= report.window_end), key=lambda a: a.submission.submitted_at, reverse=True)[:3]
    if not completed:
        st.write("Nessuna attività completata nel periodo. Lo storico completo è nella sezione Homework.")
    for assignment in completed:
        st.markdown(f"**{assignment.template.title}** · completato il {italian_date(assignment.submission.submitted_at, style='short')}")
        homework_answer(st, assignment)
    st.subheader("Come si è sentito il paziente")
    st.caption("Medie di ansia e stress nel periodo del riepilogo, sulla scala 0–10, confrontate con i 21 giorni precedenti.")
    cols = st.columns(2)
    cols[0].metric("Ansia", str(report.recent_anxiety).replace(".", ",") if report.recent_anxiety is not None else "—", metric_delta(report.recent_anxiety, report.previous_anxiety), delta_color="off")
    cols[1].metric("Stress", str(report.recent_stress).replace(".", ",") if report.recent_stress is not None else "—", metric_delta(report.recent_stress, report.previous_stress), delta_color="off")
    st.subheader("Contenuti condivisi")
    st.caption("Condivisi dal paziente per la seduta")
    if not report.shared_notes: st.write("Nessun contenuto attualmente condiviso per la seduta.")
    for note in report.shared_notes: st.markdown(f'<div class="ph-note">“{escape(note.text).replace(chr(10), "<br>")}”<br><small>Condiviso il {italian_date(note.shared_at, year=True)}</small></div>', unsafe_allow_html=True)
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
    if current.items:
        st.caption(f"{len(current.items)} elementi scelti dal paziente · una priorità")
        bridge_items(st, current.items, model)
    else:
        st.caption("Il paziente può scegliere dall'area personale ciò che desidera riprendere insieme.")
    if current.optional_text: st.write(current.optional_text)
    if current.status == BridgeStatus.READY and st.button("Segna come discusso", type="primary"):
        advance_bridge(repo, current, DemoClock().now); st.rerun()
    if current.status == BridgeStatus.REVIEWED and st.button("Archivia Bridge", type="primary"):
        advance_bridge(repo, current, DemoClock().now)
        st.session_state.demo_notice = "Bridge archiviato. Il paziente può prepararne uno nuovo."
        st.rerun()
