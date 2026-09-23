"""Fictional first-person answers, matched to the questions in each worksheet."""

from datetime import datetime

from psyhelper.domain.models import HomeworkTemplate


VOICES = {
    "giulia": {
        "emotion": "tesa", "thought": "Se commetto un errore penseranno che non sono capace.",
        "support": "In passato mi è stato chiesto di correggere alcuni dettagli del lavoro.",
        "counter": "Una correzione non è stata un giudizio su tutto il mio lavoro; ho ricevuto anche riscontri positivi.",
        "alternative": "Posso prepararmi con cura e correggere un errore senza dover controllare tutto più volte.",
        "body": "Tensione alle spalle e respiro corto.",
        "question": "Sto valutando questo episodio o immaginando un giudizio su tutta la mia persona?",
        "need": "Distinguere la cura del lavoro dal bisogno di eliminare ogni incertezza.",
        "actions": [
            ("Presentare un punto con una scaletta breve", "Ho esposto il primo punto, poi ho letto il resto per paura di perdere il filo.", "Ho concluso la presentazione. La tensione è rimasta e vorrei capire cosa mi ha fatto tornare alle slide."),
            ("Inviare l'email dopo due revisioni", "Ho fatto due revisioni e poi inviato, lasciando il computer per qualche minuto.", "Ho continuato a pensare alla mail, ma non l'ho riaperta. La risposta del responsabile riguardava il contenuto."),
            ("Lasciare alla collega una parte della consegna", "Ho concordato un controllo finale senza riscrivere il lavoro della collega.", "Il risultato era diverso da come lo avrei fatto io, ma rispettava gli accordi."),
            ("Correggere l'allegato e avvisare", "Ho inviato il file corretto con una spiegazione breve.", "Il problema è stato risolto. Mi sono accorta che continuavo a ripensarci più a lungo degli altri."),
            ("Dividere il lavoro e chiedere supporto", "Ho chiesto aiuto su una parte, ma sono rimasta oltre l'orario per ricontrollare.", "La consegna è partita in tempo. Il controllo ripetuto mi ha tolto tempo al riposo."),
            ("Intervenire senza preparare ogni frase", "Ho fatto una domanda in riunione dopo aver annotato solo il punto principale.", "C'è stata una breve esitazione. Sono riuscita a finire la domanda e ho ricevuto una risposta utile."),
            ("Presentare con tre punti di appoggio", "Ho presentato senza leggere le slide e ho chiesto un chiarimento quando serviva.", "Ero ancora tesa, ma sono rimasta sul contenuto. Vorrei riprovare questa modalità."),
        ],
    },
    "luca": {
        "emotion": "in ansia", "thought": "Se rimango in silenzio sembrerò fuori posto.",
        "support": "A volte fatico a iniziare una conversazione e ci sono state pause.",
        "counter": "Anche gli altri fanno pause; alcune persone mi hanno cercato di nuovo dopo una conversazione breve.",
        "alternative": "Posso partecipare ascoltando e facendo una domanda, anche se mi sento impacciato.",
        "body": "Nodo allo stomaco e spalle rigide.",
        "question": "Devo essere brillante oppure posso semplicemente partecipare?",
        "need": "Darmi il permesso di partecipare senza dover intrattenere tutti.",
        "actions": [
            ("Raggiungere i colleghi durante la pausa", "Ho pensato di raggiungerli, poi sono rimasto alla scrivania e ho guardato il telefono.", "Il disagio è sceso subito, ma dopo mi è dispiaciuto non aver provato. Vorrei concordare un passo più piccolo."),
            ("Restare cinque minuti al bar con un collega", "Sono sceso al bar, ho ordinato un caffè e sono rimasto circa cinque minuti.", "Ho parlato poco e l'ansia era ancora presente. Sono rimasto per il tempo che avevo scelto."),
            ("Accettare un invito a cena", "Ho chiesto chi ci sarebbe stato e ho rimandato la risposta fino alla sera.", "Ho notato che cercavo la certezza di trovarmi bene prima di decidere. Non l'avevo, ma alla fine ho accettato."),
            ("Fare una domanda in palestra", "Ho chiesto un chiarimento sull'esercizio a una persona che vedo spesso.", "Lo scambio è durato poco e mi sono sentito impacciato. La persona ha risposto normalmente."),
        ],
    },
    "martina": {
        "emotion": "preoccupata", "thought": "Sono indietro: se non recupero tutto subito andrà male.",
        "support": "Ci sono capitoli che devo ancora ripassare e in una simulazione ho fatto diversi errori.",
        "counter": "Altri argomenti sono già più chiari; gli errori indicano cosa ripassare, non il risultato dell'esame.",
        "alternative": "Posso scegliere gli argomenti prioritari e valutare una sessione alla volta.",
        "body": "Peso sul petto e tensione al collo.",
        "question": "Quale parte posso affrontare oggi con il tempo e le energie che ho?",
        "need": "Un programma sostenibile con pause e priorità definite.",
        "actions": [
            ("Studiare per due blocchi da venticinque minuti", "Ho completato il primo blocco, fatto una pausa e ripreso il secondo.", "Non ho finito il capitolo, ma ho lavorato su due parti precise senza prolungare la sera."),
            ("Iniziare da una pagina lasciando il telefono lontano", "Ho passato quasi un'ora al telefono prima di aprire il libro.", "Mi sono sentita in colpa e ho cercato di recuperare senza pause. Vorrei riprendere il momento in cui ho rimandato."),
            ("Riconoscere cosa succede quando mi confronto con gli altri", "Ho chiesto ai colleghi a che punto fossero e poi ho controllato il mio programma più volte.", "Dopo il confronto ero più tesa e ho studiato meno. Vorrei provare a tornare a una priorità concreta."),
            ("Usare la simulazione per scegliere cosa ripassare", "Ho svolto metà prova e segnato gli errori senza continuare a ricalcolare il voto.", "La prova non è completa. Ho però individuato due argomenti su cui lavorare."),
            ("Chiudere i libri alle diciannove dopo tre blocchi", "Ho completato due blocchi e spostato il terzo al giorno dopo, poi ho chiuso i libri.", "Mi è rimasta la preoccupazione di essere indietro, ma ho mantenuto il limite che avevo scelto."),
        ],
    },
    "andrea": {
        "emotion": "sotto pressione", "thought": "Non posso staccare finché c'è qualcosa da finire.",
        "support": "Ci sono consegne e richieste aperte; in alcuni giorni è stato necessario riorganizzarsi.",
        "counter": "Non tutte le richieste sono urgenti e in passato alcune hanno potuto aspettare il mattino.",
        "alternative": "Posso concordare le priorità e proteggere una pausa anche se il lavoro non è tutto concluso.",
        "body": "Stanchezza e tensione cervicale.",
        "question": "Questa richiesta è urgente oppure sto anticipando il lavoro di domani?",
        "need": "Ritrovare spazi brevi per il riposo e le attività che mi interessano.",
        "actions": [
            ("Fare una passeggiata di dieci minuti dopo cena", "Sono uscito per dieci minuti anche se non ne avevo molta voglia.", "Al ritorno ero ancora stanco, ma avevo interrotto la serata davanti al computer."),
            ("Notare come sto durante una cena con un amico", "Ho accettato un incontro breve e ho lasciato il telefono nella tasca della giacca.", "All'inizio pensavo al lavoro; durante la cena ho seguito di più la conversazione."),
            ("Riprendere la chitarra per venti minuti", "Ho ripreso un brano conosciuto senza cercare di impararne uno nuovo.", "Ho suonato per circa quindici minuti. Mi è piaciuto tornare a qualcosa che non dovevo consegnare."),
            ("Chiudere il portatile all'orario concordato", "Ho chiuso il portatile, ma l'ho riaperto dopo una notifica.", "Ho risposto a una richiesta che poteva aspettare. Vorrei capire come gestire il momento della notifica."),
            ("Osservare come sto durante un'attività fisica leggera", "Ho fatto una sessione breve di stretching, adattandola alla stanchezza.", "La tensione alle spalle era un po' minore; non è cambiato il carico di lavoro, ma ho fatto una pausa."),
        ],
    },
}


def homework_answers(template: HomeworkTemplate, slug: str, episode: str,
                     index: int, submitted_at: datetime) -> dict[str, str]:
    voice = VOICES[slug]
    plan, action, outcome = voice["actions"][index]
    before = (7, 6, 7, 6, 5, 6, 5)[index]
    after = before if index % 3 == 0 else max(3, before - 1)
    situation = f"Episodio: {episode}."
    answers = {
        "situazione": situation,
        "pensieri_ed_emozioni": f"Mi sentivo {voice['emotion']} ({before}/10). Ho pensato: «{voice['thought']}»",
        "conseguenze": outcome,
        "pensiero_automatico": voice["thought"],
        "emozione_e_intensita": f"{voice['emotion'].capitalize()}, {before}/10.",
        "cosa_e_successo": action + " " + outcome,
        "pensiero": voice["thought"],
        "elementi_a_favore": voice["support"],
        "elementi_alternativi": voice["counter"],
        "nuova_prospettiva": voice["alternative"],
        "passo_scelto": plan + ".",
        "ansia_prima": f"{before}/10.",
        "cosa_ho_fatto": action,
        "ansia_dopo": f"{after}/10. " + outcome,
        "impulso_a_evitare": f"Intensità {before}/10. Avrei voluto rimandare il passo concordato.",
        "scelta_fatta": action,
        "esito": outcome,
        "attivita_programmata": plan + ".",
        "quando": f"Il {submitted_at:%d/%m}, nel momento concordato per l'attività.",
        "energia_prima": f"{4 + index % 3}/10. All'inizio avevo poca voglia di mettermi in movimento.",
        "com_e_andata": action + " " + outcome,
        "evento": situation,
        "emozione": voice["emotion"].capitalize() + ".",
        "intensita": f"{before}/10.",
        "segnali_del_corpo": voice["body"],
        "bisogno_o_azione": voice["need"] + " " + action,
        "momento_scelto": situation,
        "cosa_ho_notato_prima": voice["body"],
        "cosa_ho_notato_dopo": outcome,
        "pensiero_iniziale": voice["thought"],
        "domanda_utile": voice["question"],
        "pensiero_piu_realistico": voice["alternative"],
    }
    return {prompt: answers[prompt] for prompt in template.prompts}
