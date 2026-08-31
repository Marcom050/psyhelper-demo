# PsyHelper Demo

Demo professionale Streamlit con quattro percorsi terapeutici interamente fittizi. Mostra dati e cambiamenti descrittivi, senza formulare diagnosi.

## Architettura

- `psyhelper/domain`: modelli tipizzati ed enum.
- `psyhelper/services`: regole pure per Homework, privacy, Bridge, obiettivi, progress e report.
- `psyhelper/repository`: repository SQLite semplice, separato dalla UI.
- `psyhelper/demo`: clock, scenari, seed e reset deterministici.
- `psyhelper/ui`: shell Streamlit minimale.

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
