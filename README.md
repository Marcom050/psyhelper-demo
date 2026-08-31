# PsyHelper Demo

Demo Streamlit con aree professionista e paziente collegate sugli stessi quattro percorsi interamente fittizi. Mostra dati e cambiamenti descrittivi, senza formulare diagnosi o proporre terapia automatizzata.

## Architettura

- `psyhelper/domain`: modelli tipizzati ed enum.
- `psyhelper/services`: regole pure per Homework, privacy, Bridge, obiettivi, progress e report.
- `psyhelper/repository`: repository SQLite semplice, separato dalla UI.
- `psyhelper/demo`: clock, scenari, seed e reset deterministici.
- `psyhelper/ui/therapist`: area professionista.
- `psyhelper/ui/patient`: area personale, check-in, attività, percorso, note private e Session Bridge.
- `psyhelper/ui/shell.py`: shell condivisa e cambio vista demo, senza autenticazione reale.

## Avvio

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m psyhelper.demo.seed
streamlit run app.py
```

Il database locale è creato in `data/psyhelper-demo.sqlite3` (ignorato da Git).

## Reset e test

```bash
python -m psyhelper.demo.reset
pytest
python -m compileall app.py psyhelper
```

Seed e reset ricostruiscono lo stesso stato usando la data ancora `2026-08-31` e UUID5 riproducibili.
