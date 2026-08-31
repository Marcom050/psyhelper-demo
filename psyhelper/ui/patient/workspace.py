from __future__ import annotations

from psyhelper.demo.clock import DemoClock
from psyhelper.domain.models import BridgeStatus, GoalKind, GoalStatus, HomeworkStatus
from psyhelper.services.core import build_bridge_candidates
from psyhelper.ui.actions import (complete_homework, create_patient_checkin, create_private_note,
                                  prepare_patient_bridge, set_note_sharing)
from psyhelper.ui.components import trend_chart
from psyhelper.ui.presentation import italian_date


PROMPT_LABELS = {
    "situazione": "Qual era la situazione?", "pensieri_ed_emozioni": "Quali pensieri ed emozioni hai notato?",
    "conseguenze": "Che cosa è successo dopo?", "pensiero_automatico": "Quale pensiero è arrivato?",
    "emozione_e_intensita": "Quale emozione, e con quale intensità?", "cosa_e_successo": "Com'è andata?",
    "pensiero": "Quale pensiero vuoi osservare?", "elementi_a_favore": "Che cosa sembra sostenerlo?",
    "elementi_alternativi": "Ci sono elementi diversi?", "nuova_prospettiva": "Quale prospettiva alternativa emerge?",
    "passo_scelto": "Quale passo hai scelto?", "ansia_prima": "Com'era l'ansia prima?",
    "cosa_ho_fatto": "Che cosa hai fatto?", "ansia_dopo": "Com'era l'ansia dopo?",
    "impulso_a_evitare": "Che impulso a evitare hai notato?", "scelta_fatta": "Quale scelta hai fatto?",
    "esito": "Com'è andata?", "attivita_programmata": "Quale attività avevi programmato?",
    "quando": "Quando?", "energia_prima": "Com'era la tua energia prima?", "com_e_andata": "Com'è andata?",
    "evento": "Che cosa è successo?", "emozione": "Quale emozione hai notato?", "intensita": "Con quale intensità?",
    "segnali_del_corpo": "Quali segnali del corpo?", "bisogno_o_azione": "Di che cosa avevi bisogno o che cosa hai fatto?",
    "momento_scelto": "Quando hai scelto di fermarti?", "cosa_ho_notato_prima": "Che cosa hai notato prima?",
    "cosa_ho_notato_dopo": "Che cosa hai notato dopo?", "pensiero_iniziale": "Qual era il pensiero iniziale?",
    "domanda_utile": "Quale domanda ti è stata utile?", "pensiero_piu_realistico": "Quale pensiero più realistico hai trovato?",
}


def _go(st, route, **values):
    st.session_state.route = route
    for key, value in values.items():
        st.session_state[key] = value
    st.rerun()


def render(st, repo, patient_id: str, route: str):
    patient = repo.patient(patient_id)
    if route == "patient_checkin": return checkin_form(st, repo, patient)
    if route == "patient_homework": return homework_form(st, repo, patient)
    pages = {"patient_today": today, "patient_activities": activities, "patient_journey": journey,
             "patient_private": private_area, "patient_bridge": bridge}
    pages.get(route, today)(st, repo, patient)


def today(st, repo, patient):
    name = patient.name.split()[0]
    st.title(f"Ciao, {name}")
    st.markdown('<p class="ph-lead">Un piccolo spazio per continuare il percorso tra una seduta e l’altra.</p>', unsafe_allow_html=True)
    if st.button("Come stai oggi?", type="primary"): _go(st, "patient_checkin")
    left, right = st.columns(2, gap="large")
    assignments = repo.assignments(patient.id); pending = next((a for a in reversed(assignments) if a.status == HomeworkStatus.PENDING), None)
    with left:
        st.subheader("Da completare")
        if pending:
            st.markdown(f"**{pending.template.title}**  \nScadenza {italian_date(pending.due_at)}")
            if st.button("Continua attività", key="today-hw"): _go(st, "patient_homework", active_homework_id=pending.id)
        else: st.write("Non ci sono attività da completare in questo momento.")
        st.subheader("Ultimo check-in")
        latest = repo.checkins(patient.id)[-1]
        st.markdown(f"**{italian_date(latest.recorded_at, year=True)}**  \nAnsia {latest.anxiety} · Stress {latest.stress}  \n{latest.mood or ''} · {latest.trigger or 'Nessun dettaglio aggiunto'}")
        if st.button("Vedi", key="checkins"): _go(st, "patient_journey")
    with right:
        st.subheader("Il tuo percorso")
        copies = {"Luca": "Negli ultimi giorni hai continuato ad affrontare alcune situazioni sociali anche con ansia presente.",
                  "Giulia": "Stai sperimentando modi più flessibili per affrontare controlli e imprevisti.",
                  "Martina": "In un periodo intenso hai continuato a scegliere priorità e passi sostenibili.",
                  "Andrea": "Hai recuperato alcuni piccoli spazi per le attività che contano per te."}
        st.write(copies.get(name, "Il percorso continua attraverso i passi che stai osservando."))
        st.subheader("Prepara la seduta")
        current = next((b for b in reversed(repo.bridges(patient.id)) if b.status != BridgeStatus.ARCHIVED), None)
        message = {BridgeStatus.DRAFT: "Hai iniziato a preparare la prossima seduta", BridgeStatus.READY: "Bridge pronto",
                   BridgeStatus.REVIEWED: "Ripreso in seduta"}.get(current.status if current else None, "Puoi raccogliere ciò che vuoi portare in seduta")
        st.write(message)
        if st.button("Apri", key="today-bridge"): _go(st, "patient_bridge")


def checkin_form(st, repo, patient):
    st.title("Come stai oggi?")
    st.caption("Il check-in fa parte del percorso condiviso con il professionista.")
    with st.form("patient-checkin"):
        mood = st.text_input("Emozione principale", placeholder="Per esempio: teso, serena, stanco")
        intensity = st.slider("Intensità", 0, 10, 5); anxiety = st.slider("Ansia", 0, 10, 5); stress = st.slider("Stress", 0, 10, 5)
        add = st.checkbox("Vuoi aggiungere qualcosa?")
        optional = {}
        if add:
            optional["trigger"] = st.text_area("Cosa è successo?", help="La situazione o il momento che vuoi ricordare.", height=80)
            optional["automatic_thought"] = st.text_area("Pensiero automatico", help="Cosa ti è passato per la mente in quel momento?", height=80)
            optional["behavior"] = st.text_area("Cosa hai fatto?", height=80)
            optional["body_sensations"] = st.text_input("Sensazioni corporee")
            optional["alternative_response"] = st.text_area("Risposta alternativa", height=80)
            optional["note_for_therapist"] = st.text_area("Nota per il professionista", height=80)
        submitted = st.form_submit_button("Salva check-in", type="primary")
    if submitted:
        clean = {key: value.strip() or None for key, value in optional.items()}
        clean["trigger"] = clean.get("trigger") or ""; clean["behavior"] = clean.get("behavior") or ""
        create_patient_checkin(repo, patient.id, DemoClock().now, anxiety=anxiety, stress=stress,
                               mood=mood.strip() or None, mood_intensity=intensity, **clean)
        st.toast("Check-in salvato"); _go(st, "patient_today")
    if st.button("Torna a Oggi"): _go(st, "patient_today")


def activities(st, repo, patient):
    st.title("Attività")
    st.caption("Le attività concordate fanno parte del percorso condiviso.")
    assignments = list(reversed(repo.assignments(patient.id)))
    st.subheader("Da completare")
    pending = [a for a in assignments if a.status == HomeworkStatus.PENDING]
    if not pending: st.write("Non ci sono attività da completare.")
    for assignment in pending:
        st.markdown(f"**{assignment.template.title}**  \nUn'attività guidata in {len(assignment.template.prompts)} brevi passaggi.  \nScadenza {italian_date(assignment.due_at)}")
        if st.button("Inizia", key=f"start-{assignment.id}"): _go(st, "patient_homework", active_homework_id=assignment.id)
        st.divider()
    st.subheader("Completate")
    for assignment in [a for a in assignments if a.status != HomeworkStatus.PENDING]:
        label = "Completata" if assignment.status == HomeworkStatus.COMPLETED else "Non completata"
        date = assignment.submission.submitted_at if assignment.submission else assignment.due_at
        st.markdown(f"**{assignment.template.title}** · {label} · {italian_date(date)}")


def homework_form(st, repo, patient):
    assignment_id = st.session_state.get("active_homework_id")
    assignment = next((a for a in repo.assignments(patient.id) if a.id == assignment_id), None)
    if not assignment or assignment.status != HomeworkStatus.PENDING:
        st.warning("Questa attività non è disponibile."); return
    st.title(assignment.template.title); st.write(f"{len(assignment.template.prompts)} domande per raccogliere la tua esperienza.")
    with st.form("complete-homework"):
        answers = {prompt: st.text_area(PROMPT_LABELS.get(prompt, prompt.replace("_", " ").capitalize()), height=90)
                   for prompt in assignment.template.prompts}
        submitted = st.form_submit_button("Salva attività", type="primary")
    if submitted:
        try: complete_homework(repo, assignment, answers, DemoClock().now)
        except ValueError: st.error("Completa tutte le risposte prima di salvare.")
        else: st.toast("Attività completata"); _go(st, "patient_activities")
    if st.button("Torna alle attività"): _go(st, "patient_activities")


def journey(st, repo, patient):
    st.title("Percorso"); goals = repo.goals(patient.id)
    st.subheader("Obiettivi")
    for goal in goals:
        kind = "Obiettivo" if goal.kind == GoalKind.GOAL else "Passo concordato"
        status = "In corso" if goal.status == GoalStatus.ACTIVE else "Completato"
        st.markdown(f'<div class="ph-note"><span class="ph-eyebrow">{kind}</span><br><strong>{goal.title}</strong><br><span class="ph-meta">{status}</span></div>', unsafe_allow_html=True)
    st.subheader("Andamento")
    checks = repo.checkins(patient.id)
    trend_chart(st, checks[-12:], compact=True)
    st.caption("Un modo semplice per rileggere i check-in nel tempo, senza giudicare i singoli giorni.")
    st.subheader("Nel tempo")
    observations = {"Luca": ["Hai partecipato alla cena fino al dolce.", "Hai proposto una pausa caffè.", "Hai scelto più volte di avvicinarti alle situazioni sociali."],
                    "Giulia": ["Hai provato controlli più brevi.", "Hai lasciato più spazio alla delega."],
                    "Martina": ["Hai riorganizzato il piano nei giorni più intensi.", "Hai continuato a scegliere le priorità."],
                    "Andrea": ["Hai recuperato passeggiate e pause brevi.", "Hai protetto alcuni spazi serali."]}
    for text in observations.get(patient.name.split()[0], []): st.markdown(f"- {text}")
    st.subheader("Momenti del percorso")
    for event in reversed(repo.events(patient.id)): st.markdown(f"**{italian_date(event.occurred_at)}**  \n{event.text}")
    st.subheader("I tuoi check-in")
    for check in reversed(checks[-8:]):
        title = f"{italian_date(check.recorded_at)} · Ansia {check.anxiety} · Stress {check.stress}"
        with st.expander(title):
            fields = (("Emozione", check.mood), ("Cosa è successo", check.trigger), ("Pensiero", check.automatic_thought),
                      ("Cosa hai fatto", check.behavior), ("Sensazioni corporee", check.body_sensations),
                      ("Risposta alternativa", check.alternative_response), ("Nota per il professionista", check.note_for_therapist))
            for label, value in fields:
                if value: st.markdown(f"**{label}**  \n{value}")


def private_area(st, repo, patient):
    st.title("Area privata")
    st.write("Uno spazio per appuntare ciò che vuoi tenere per te o decidere di portare in seduta.")
    with st.form("private-note"):
        text = st.text_area("Scrivi qualcosa per te", height=130)
        saved = st.form_submit_button("Salva nota", type="primary")
    if saved and text.strip(): create_private_note(repo, patient.id, text, DemoClock().now); st.toast("Visibile solo a te"); st.rerun()
    for note in sorted(repo.notes(patient.id), key=lambda n: n.created_at, reverse=True):
        st.markdown(f'<div class="ph-note">{note.text}<br><span class="ph-meta">{italian_date(note.created_at, year=True)} · {"Condivisa" if note.is_shared else "Solo per me"}</span></div>', unsafe_allow_html=True)
        if note.is_shared:
            if st.button("Revoca condivisione", key=f"revoke-{note.id}"):
                set_note_sharing(repo, note, False, DemoClock().now); st.info("Non sarà più mostrata nelle viste future del professionista. Potrebbe essere già stata vista."); st.rerun()
        elif st.session_state.get("confirm_share_note") == note.id:
            st.info("Questa nota sarà visibile al professionista nelle sezioni dedicate alla preparazione della seduta.")
            if st.button("Condividi", key=f"confirm-{note.id}"):
                set_note_sharing(repo, note, True, DemoClock().now); st.session_state.pop("confirm_share_note", None); st.rerun()
        elif st.button("Condividi per la prossima seduta", key=f"share-{note.id}"):
            st.session_state.confirm_share_note = note.id; st.rerun()


def bridge(st, repo, patient):
    st.title("Prepara la prossima seduta"); st.write("Raccogli ciò che vuoi ricordare o portare con te.")
    bridges = repo.bridges(patient.id); current = next((b for b in reversed(bridges) if b.status != BridgeStatus.ARCHIVED), None)
    if current and current.status in (BridgeStatus.READY, BridgeStatus.REVIEWED):
        st.subheader("Bridge pronto" if current.status == BridgeStatus.READY else "Ripreso in seduta")
        for item in sorted(current.items, key=lambda item: -item.priority): st.markdown(f"- **{item.title}**{' · Da qui vorrei partire' if item.priority else ''}")
        if current.optional_text: st.write(current.optional_text)
        st.caption("Il professionista potrà vederlo nella preparazione della prossima seduta.")
    else:
        candidates = build_bridge_candidates(repo.notes(patient.id), repo.events(patient.id), checkins=repo.checkins(patient.id), assignments=repo.assignments(patient.id))
        st.subheader("Scegli fino a 4 cose che vorresti riprendere")
        selected = []
        for item in candidates:
            if st.checkbox(item.title, key=f"candidate-{item.id}"): selected.append(item)
        if len(selected) > 4: st.warning("Puoi scegliere al massimo 4 elementi.")
        labels = {item.id: item.title for item in selected}
        priority = st.radio("Da dove vuoi partire?", list(labels), format_func=lambda item_id: labels[item_id]) if selected else None
        optional = st.text_area("Vuoi aggiungere qualcosa?", height=100)
        if st.button("Prepara Bridge", type="primary", disabled=not selected or len(selected) > 4):
            prepare_patient_bridge(repo, patient.id, candidates, [item.id for item in selected], priority, optional, DemoClock().now); st.rerun()
        st.caption("Qui compaiono check-in, attività, momenti del percorso e soltanto le note che hai scelto di condividere.")
    archived = [b for b in reversed(bridges) if b.status == BridgeStatus.ARCHIVED]
    if archived:
        st.subheader("Sedute precedenti")
        for old in archived: st.markdown(f"**{italian_date(old.created_at, year=True)}** · {len(old.items)} elementi · Archiviato")
