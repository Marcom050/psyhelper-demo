from psyhelper.domain.models import HomeworkTemplate


HOMEWORK_CATALOG: dict[str, HomeworkTemplate] = {
    "abc": HomeworkTemplate("hw-template-abc", "ABC", ("situazione", "pensieri_ed_emozioni", "conseguenze")),
    "thought_record": HomeworkTemplate("hw-template-thought-record", "Registro dei pensieri", ("situazione", "pensiero_automatico", "emozione_e_intensita", "cosa_e_successo")),
    "cognitive_restructuring": HomeworkTemplate("hw-template-cognitive-restructuring", "Ristrutturazione cognitiva", ("pensiero", "elementi_a_favore", "elementi_alternativi", "nuova_prospettiva")),
    "graded_exposure": HomeworkTemplate("hw-template-graded-exposure", "Esposizione graduale", ("passo_scelto", "ansia_prima", "cosa_ho_fatto", "ansia_dopo")),
    "avoidance_monitoring": HomeworkTemplate("hw-template-avoidance-monitoring", "Monitoraggio dell'evitamento", ("situazione", "impulso_a_evitare", "scelta_fatta", "esito")),
    "behavioral_activation": HomeworkTemplate("hw-template-behavioral-activation", "Behavioral activation", ("attivita_programmata", "quando", "energia_prima", "com_e_andata")),
    "emotion_trigger": HomeworkTemplate("hw-template-emotion-trigger", "Scheda emozioni/trigger", ("evento", "emozione", "intensita", "segnali_del_corpo", "bisogno_o_azione")),
    "three_minute_breathing": HomeworkTemplate("hw-template-three-minute-breathing", "Respiro 3 minuti", ("momento_scelto", "cosa_ho_notato_prima", "cosa_ho_notato_dopo")),
    "realistic_thought": HomeworkTemplate("hw-template-realistic-thought", "Pensiero più realistico", ("pensiero_iniziale", "domanda_utile", "pensiero_piu_realistico")),
}


def homework_template(slug: str) -> HomeworkTemplate:
    """Return a fresh snapshot so an assignment preserves its assigned wording."""
    template = HOMEWORK_CATALOG[slug]
    return HomeworkTemplate(template.id, template.title, tuple(template.prompts))
