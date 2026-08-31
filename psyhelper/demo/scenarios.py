from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID, uuid5

from psyhelper.domain.models import *
from .clock import DemoClock
from .homework_catalog import homework_template

NS = UUID("bf853ec3-31ba-4bc2-9e3e-2c49dd2ec821")


def did(slug, kind, n):
    return str(uuid5(NS, f"{slug}:{kind}:{n}"))


@dataclass(frozen=True)
class ScenarioExpectation:
    checkins: int
    assigned: int
    completed: int
    expired: int
    active_goals: int
    achieved_goals: int
    private_notes: int
    shared_notes: int
    current_bridge: BridgeStatus
    archived_bridges: int


SPECS = {
    "giulia": ("Giulia Bianchi", 27, "ansia anticipatoria e perfezionismo lavorativo", [8,7,8,7,6,7,6,6,5,6,5,5,4,5,4,5,4,4,5,4], [7,8,7,7,6,7,6,5,6,5,5,5,4,5,4,4,5,4,4,4], 8, 7, 1, BridgeStatus.READY, 2),
    "luca": ("Luca Ferri", 31, "evitamento sociale e difficoltà nell'esporsi", [7,8,7,7,6,7,7,6,7,6,6,7,6,6,5,6,5,6], [6]*18, 7, 4, 2, BridgeStatus.DRAFT, 1),
    "martina": ("Martina Romano", 24, "stress universitario", [5,4,5,5,4,5,5,4,5,5,5,6,5,6,6,7,7,8,7,8], [5,5,4,5,5,5,4,5,5,5,6,6,6,7,7,8,8,9,8,9], 8, 5, 2, BridgeStatus.READY, 1),
    "andrea": ("Andrea Conti", 38, "stress lavorativo e riduzione delle attività gratificanti", [6,6,7,6,5,6,5,4,5,4,4,5,4,4,5,5,6,5], [7,6,7,6,5,5,4,5,4,4,4,5,4,5,5,6,6,6], 7, 5, 1, BridgeStatus.DRAFT, 2),
}
EXPECTATIONS = {s: ScenarioExpectation(len(v[3]), v[5], v[6], v[7], 1, 1, 1, 1, v[8], v[9]) for s, v in SPECS.items()}

GAPS = [59,56,53,49,46,43,39,36,33,29,26,23,20,17,14,12,9,6,3,1]

CHECKIN_STORIES = {
    "giulia": [
        ("riunione di reparto", "Ho rimandato la preparazione delle slide", "preoccupata", "Farò sicuramente confusione", "Tensione alle spalle"),
        ("email al responsabile", "Ho riletto la mail sette volte", "tesa", "Troverà un errore", "Stomaco chiuso"),
        ("presentazione", "Ho parlato velocemente e controllato ogni dettaglio", "agitata", "Noteranno che non sono pronta", "Cuore accelerato"),
        ("delega di un'attività", "Ho ripreso il lavoro affidato a una collega", "inquieta", "Se non controllo io qualcosa sfuggirà", None),
        ("riunione di reparto", "Ho preparato una scaletta breve", "preoccupata", "Potrei bloccarmi", "Mani fredde"),
        ("scadenza del progetto", "Sono rimasta oltre l'orario", "sotto pressione", "Non posso permettermi imprecisioni", "Mascella contratta"),
        ("feedback del responsabile", "Ho chiesto un chiarimento invece di immaginare il peggio", "incerta", "Forse il lavoro non basta", None),
        ("email al cliente", "Ho fatto due revisioni e poi inviato", "tesa", "Una svista rovinerebbe tutto", "Respiro corto"),
        ("riunione di reparto", "Ho espresso un dubbio senza preparare ogni parola", "sollevata", "Posso correggermi se serve", None),
        ("delega di un'attività", "Ho lasciato alla collega la consegna finale", "incerta", "Posso verificare solo i punti essenziali", None),
        ("presentazione", "Ho provato una volta e poi mi sono fermata", "concentrata", "Non deve essere perfetta per essere chiara", None),
        ("email al responsabile", "Ho inviato dopo una sola rilettura", "prudente", "Un refuso non definisce il mio lavoro", None),
        ("riunione di reparto", "Sono intervenuta con una domanda", "soddisfatta", None, None),
        ("scadenza del progetto", "Ho diviso il lavoro e chiesto supporto", "affaticata", "Posso consegnare bene senza fare tutto sola", "Tensione cervicale"),
        ("presentazione", "Ho tollerato una piccola esitazione", "sollevata", "Gli altri erano interessati al contenuto", None),
        ("errore in un allegato", "Ho corretto e avvisato senza prolungare i controlli", "dispiaciuta", "Posso rimediare a un errore", "Calore al viso"),
        ("riunione di reparto", "Ho presentato senza leggere le slide", "fiduciosa", "Posso restare sul punto principale", None),
        ("delega di un'attività", "Ho concordato un controllo finale e lasciato autonomia", "tranquilla", None, None),
        ("scadenza importante", "Ho ricontrollato più del previsto e dormito poco", "tesa", "Se sbaglio deludo tutti", "Tensione alle spalle"),
        ("riunione di reparto", "Nonostante la settimana intensa ho esposto la mia parte", "stanca", "L'ansia può esserci senza impedirmi di parlare", None),
    ],
    "luca": [
        ("invito a cena", "Ho detto che avevo un impegno", "in ansia", "Non saprei cosa dire", "Nodo allo stomaco"),
        ("pausa con i colleghi", "Sono rimasto alla scrivania", "a disagio", "Sembrerei fuori posto", None),
        ("conversazione con un vicino", "Ho salutato ma chiuso subito lo scambio", "teso", "Finiremo gli argomenti", "Voce rigida"),
        ("invito a cena", "Ho chiesto chi ci sarebbe stato prima di decidere", "incerto", "Sarò quello silenzioso", None),
        ("caffè con colleghi", "Sono sceso al bar per cinque minuti", "agitato", "Posso ascoltare senza dover intrattenere", "Cuore veloce"),
        ("chat di gruppo", "Ho scritto una risposta breve", "esposto", "Forse il messaggio sembrerà banale", None),
        ("aperitivo", "Sono arrivato ma sono andato via presto", "teso", "Non riuscirò a inserirmi", "Spalle rigide"),
        ("caffè con colleghi", "Ho fatto una domanda sul fine settimana", "curioso", "Una domanda semplice è sufficiente", None),
        ("invito a cena", "Ho accettato rimandando la risposta solo un'ora", "preoccupato", "Potrei restare anche se arriva il silenzio", None),
        ("conversazione in palestra", "Ho commentato l'esercizio con una persona", "impacciato", "Non devo trovare la frase perfetta", None),
        ("caffè con colleghi", "Sono rimasto fino alla fine della pausa", "presente", None, "Tensione lieve"),
        ("cena con amici", "Sono andato via dopo il primo piatto", "deluso", "L'ansia significa che devo uscire", "Stomaco chiuso"),
        ("pranzo in ufficio", "Mi sono seduto con due colleghi", "teso", "Posso fare una pausa nella conversazione", None),
        ("invito a cena", "Ho confermato e preparato due argomenti, senza annullare", "in ansia", "Non devo essere brillante", None),
        ("cena con amici", "Sono rimasto fino al dolce pur con ansia", "orgoglioso", "Il disagio è sceso mentre restavo", "Calore al viso"),
        ("conversazione con collega", "Ho iniziato io chiedendo del suo progetto", "incerto", "Posso concentrarmi sull'ascolto", None),
        ("caffè con colleghi", "Ho proposto io la pausa", "soddisfatto", None, None),
        ("evento aziendale", "Sono rimasto quaranta minuti e parlato con due persone", "teso", "L'ansia non cancella il passo fatto", "Respiro corto"),
    ],
    "martina": [
        ("studio/esami", "Ho studiato due ore seguendo il piano", "concentrata", "Il programma è gestibile a blocchi", None),
        ("lezione universitaria", "Ho preso appunti e fatto una pausa", "tranquilla", None, None),
        ("studio/esami", "Ho rimandato un capitolo al pomeriggio", "in colpa", "Sto già perdendo terreno", "Peso sul petto"),
        ("confronto con colleghi", "Ho chiesto come si stavano organizzando", "incerta", "Sono tutti più avanti", None),
        ("studio/esami", "Ho completato la sessione prevista", "soddisfatta", None, None),
        ("biblioteca", "Ho alternato studio e pause brevi", "presente", "Le pause non sono tempo perso", None),
        ("studio/esami", "Ho procrastinato al telefono per un'ora", "frustrata", "Non recupererò", "Testa pesante"),
        ("pianificazione settimanale", "Ho diviso tre capitoli in compiti piccoli", "sollevata", "Posso partire dal primo pezzo", None),
        ("studio/esami", "Ho seguito il programma senza prolungare la sera", "calma", None, None),
        ("confronto con colleghi", "Ho notato il confronto e sono tornata al mio piano", "insicura", "I ritmi degli altri non misurano la mia preparazione", None),
        ("studio/esami", "Ho iniziato tardi ma completato una parte", "stanca", "Una sessione imperfetta è comunque utile", None),
        ("simulazione d'esame", "Ho svolto metà prova", "tesa", "Gli errori mostrano cosa ripassare", "Stomaco chiuso"),
        ("studio/esami", "Ho organizzato la giornata e chiuso i libri alle 19", "soddisfatta", None, None),
        ("data dell'esame", "Ho contato i giorni più volte", "preoccupata", "Non sarò pronta", "Tensione al collo"),
        ("studio/esami", "Ho prolungato lo studio fino a tardi", "affaticata", "Devo recuperare tutto subito", "Occhi pesanti"),
        ("simulazione d'esame", "Ho evitato la prova completa", "in ansia", "Il risultato confermerebbe che non so abbastanza", "Nausea lieve"),
        ("studio/esami", "Ho saltato la pausa e riletto senza concentrarmi", "sopraffatta", "Manca troppo poco tempo", "Mal di testa"),
        ("confronto con colleghi", "Ho controllato i loro progressi invece di iniziare", "scoraggiata", "Sono indietro rispetto a tutti", "Sonno agitato"),
        ("studio/esami", "Dopo aver rifatto il piano ho completato due blocchi", "tesa", "Posso scegliere le priorità", None),
        ("notte prima della prova", "Ho faticato ad addormentarmi e studiato ancora", "preoccupata", "Domani dimenticherò tutto", "Battito accelerato"),
    ],
    "andrea": [
        ("carico di lavoro", "Ho continuato a lavorare dopo cena", "svuotato", "Non posso staccare finché resta qualcosa", "Spalle rigide"),
        ("serata a casa", "Ho rinunciato alla passeggiata", "stanco", "Non ho energia per altro", None),
        ("carico di lavoro", "Ho saltato il pranzo per una consegna", "sotto pressione", "Devo rispondere subito a tutto", "Testa pesante"),
        ("tempo libero", "Ho fatto una passeggiata di dieci minuti", "titubante", "Anche poco può cambiare la serata", None),
        ("cena con un amico", "Ho accettato un incontro breve", "contento", None, None),
        ("carico di lavoro", "Ho chiuso il portatile alle 20", "teso", "Il resto può aspettare domani", None),
        ("attività fisica", "Ho fatto stretching per quindici minuti", "più presente", None, None),
        ("hobby lasciato da parte", "Ho ripreso la chitarra per venti minuti", "curioso", "Non devo essere produttivo anche qui", None),
        ("carico di lavoro", "Ho fatto una pausa vera a pranzo", "sollevato", None, None),
        ("serata a casa", "Ho lasciato il telefono di lavoro in ingresso", "tranquillo", None, None),
        ("passeggiata", "Sono uscito anche se pioveva leggermente", "soddisfatto", None, None),
        ("cena con un amico", "Sono rimasto più a lungo del previsto", "coinvolto", None, None),
        ("carico di lavoro", "Ho definito un orario di chiusura", "determinato", "Posso riprendere domani", None),
        ("attività fisica", "Ho fatto una sessione leggera", "energico", None, None),
        ("hobby lasciato da parte", "Ho annullato il tempo per la chitarra per una chiamata", "deluso", "È solo una settimana intensa", None),
        ("carico di lavoro", "Ho riaperto il computer dopo cena", "affaticato", "Se non anticipo resterò indietro", "Tensione cervicale"),
        ("urgenza lavorativa", "Ho saltato la passeggiata per chiudere una richiesta", "stanco", "In questi giorni è difficile separare gli spazi", None),
        ("serata a casa", "Ho protetto mezz'ora senza notifiche", "sollevato", "Posso ripartire da una pausa piccola", None),
    ],
}

HW_PLANS = {
    "giulia": ["abc", "thought_record", "cognitive_restructuring", "realistic_thought", "abc", "thought_record", "cognitive_restructuring", "realistic_thought"],
    "luca": ["avoidance_monitoring", "graded_exposure", "thought_record", "realistic_thought", "graded_exposure", "avoidance_monitoring", "realistic_thought"],
    "martina": ["behavioral_activation", "thought_record", "emotion_trigger", "realistic_thought", "behavioral_activation", "thought_record", "emotion_trigger", "realistic_thought"],
    "andrea": ["behavioral_activation", "emotion_trigger", "behavioral_activation", "avoidance_monitoring", "emotion_trigger", "behavioral_activation", "emotion_trigger"],
}

HW_EPISODES = {
    "giulia": ["presentazione in riunione", "email al responsabile", "delega alla collega", "errore nell'allegato", "scadenza del progetto", "intervento in riunione", "presentazione senza leggere le slide"],
    "luca": ["pausa con i colleghi", "caffè al bar", "invito a cena", "conversazione in palestra"],
    "martina": ["piano di studio", "procrastinazione al telefono", "confronto con i colleghi", "simulazione d'esame", "giornata organizzata"],
    "andrea": ["passeggiata breve", "cena con un amico", "riprendere la chitarra", "chiudere il portatile", "attività fisica leggera"],
}

GOALS = {
    "giulia": ("Inviare le email dopo due controlli al massimo", "Delegare una consegna concordando un solo controllo"),
    "luca": ("Proporre una pausa caffè a un collega", "Restare a cena almeno fino al secondo piatto"),
    "martina": ("Svolgere una simulazione completa con tempo definito", "Chiudere lo studio entro le 20 per tre sere"),
    "andrea": ("Proteggere due serate senza riaprire il portatile", "Riprendere la chitarra per venti minuti"),
}


def _answers(template: HomeworkTemplate, episode: str, index: int) -> dict[str, str]:
    phrases = [
        f"Ho osservato: {episode}.",
        "All'inizio mi aspettavo che sarebbe stato difficile.",
        "Ho scelto un passo piccolo e verificabile.",
        "Il disagio era presente, ma sono riuscito/a a restare nel compito.",
        "Alla fine ho notato più margine di quanto prevedessi.",
    ]
    return {prompt: phrases[(index + offset) % len(phrases)] for offset, prompt in enumerate(template.prompts)}


def build_scenario(slug, therapist_id, clock=DemoClock()):
    name, age, desc, anx, stress, assigned, completed, expired, current, archived = SPECS[slug]
    patient = Patient(did(slug, "patient", 0), therapist_id, name, age, clock.anchor - timedelta(days=60), desc)
    stories = CHECKIN_STORIES[slug]
    checks = []
    for i, (trigger, behavior, mood, thought, body) in enumerate(stories):
        checks.append(CheckIn(
            did(slug, "checkin", i), patient.id, clock.days_ago(GAPS[i]), anx[i], stress[i], trigger, behavior,
            mood, min(10, max(anx[i], stress[i])), thought,
            "Posso osservare i fatti e scegliere il prossimo passo." if thought and i % 2 else None,
            body, "Vorrei riprendere questo episodio in seduta." if i in (11, 18) else None,
        ))

    homework = []
    for i, template_slug in enumerate(HW_PLANS[slug]):
        at = clock.days_ago(55 - i * 7)
        status = HomeworkStatus.COMPLETED if i < completed else HomeworkStatus.EXPIRED if i < completed + expired else HomeworkStatus.PENDING
        template = homework_template(template_slug)
        submission = None
        if status == HomeworkStatus.COMPLETED:
            episode = HW_EPISODES[slug][i % len(HW_EPISODES[slug])]
            submission = HomeworkSubmission(did(slug, "submission", i), did(slug, "homework", i), clock.days_ago(52 - i * 7), _answers(template, episode, i))
        homework.append(HomeworkAssignment(did(slug, "homework", i), patient.id, template, at, clock.days_ago(49 - i * 7), status, submission))

    active, achieved = GOALS[slug]
    goals = [
        JourneyGoal(did(slug, "goal", 0), patient.id, active, GoalKind.GOAL, GoalStatus.ACTIVE, clock.days_ago(58), clock.days_ago(5)),
        JourneyGoal(did(slug, "goal", 1), patient.id, achieved, GoalKind.COMMITMENT, GoalStatus.ACHIEVED, clock.days_ago(55), clock.days_ago(18)),
    ]
    shared_text = {
        "giulia": "Vorrei riprendere la settimana della scadenza: ho controllato molto, ma ho comunque delegato una parte.",
        "luca": "Alla cena sono rimasto fino al dolce; ero ancora teso, ma non sono andato via subito.",
        "martina": "Vorrei parlare dell'esame: faccio fatica ad ammettere quanto mi pesa.",
        "andrea": "Questa settimana il carico è aumentato e vorrei ritrovare uno spazio serale senza lavoro.",
    }[slug]
    notes = [
        PatientNote(did(slug, "note", 0), patient.id, shared_text, clock.days_ago(7), clock.days_ago(6)),
        PatientNote(did(slug, "note", 1), patient.id, f"Promemoria personale sul percorso di {name.split()[0].lower()}.", clock.days_ago(4)),
    ]
    bridges = [SessionBridge(did(slug, "bridge", i), patient.id, clock.days_ago(45-i*16), BridgeStatus.ARCHIVED, [], "Temi discussi in seduta", clock.days_ago(43-i*16)) for i in range(archived)]
    items = [] if current == BridgeStatus.DRAFT else [SessionBridgeItem(did(slug, "bridge-item", 0), "note", notes[0].id, "Nota condivisa recente", 10)]
    bridges.append(SessionBridge(did(slug, "bridge", archived), patient.id, clock.days_ago(3), current, items, "Vorrei partire da qui." if items else ""))

    event_specs = [(EventKind.IMPROVEMENT, "Cambiamento nei comportamenti osservato nei check-in", checks[10].id)]
    if slug in ("giulia", "andrea"):
        event_specs.append((EventKind.SETBACK, "Difficoltà recente collegata a un aumento del carico, da riprendere con gradualità", checks[-2].id))
    if slug == "luca":
        event_specs.append((EventKind.STEP_FORWARD, "È rimasto a cena fino al dolce pur provando ansia", checks[14].id))
    if slug == "martina":
        event_specs.extend([
            (EventKind.RECURRING_TRIGGER, "Il contesto studio/esami ricorre nei check-in", checks[-2].id),
            (EventKind.SETBACK, "Stress recente più alto in prossimità dell'esame", checks[-1].id),
        ])
    checks_by_id = {check.id: check for check in checks}
    events = [TimelineEvent(did(slug, "event", i), patient.id, checks_by_id[source].recorded_at, kind, text, source, "derived") for i, (kind, text, source) in enumerate(event_specs)]
    onboarding = PathwayOnboarding(did(slug, "onboarding", 0), patient.id, clock.days_ago(58), desc)
    return [patient, *checks, *homework, *goals, *notes, *bridges, *events, onboarding]
