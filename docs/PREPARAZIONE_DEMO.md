# PsyHelper · preparazione della dimostrazione

Questa app mostra quattro percorsi interamente fittizi. Le azioni di check-in,
compilazione degli homework, condivisione delle note e preparazione del Bridge
aggiornano realmente il database della demo e sono visibili nell'altra vista.
La data di riferimento resta il 31 agosto 2026, indicata nelle impostazioni:
le scadenze non cambiano mentre si prova o si presenta lo scenario.

## Come spiegare le due versioni

«PsyHelper è il prototipo in cui ho sviluppato le funzionalità del progetto.
Per questo incontro ho preparato una versione dimostrativa separata, con
un'interfaccia ripensata e percorsi completamente fittizi. Ci permette di
esplorare alcuni flussi principali dal punto di vista del paziente e del
professionista e di discuterne l'utilità.»

| Aspetto | PsyHelper Beta | PsyHelper Demo |
| --- | --- | --- |
| Scopo | Prototipo più esteso, con componenti sperimentali e operative | Dimostrazione interattiva di alcuni flussi principali |
| Accesso | Profili e autenticazione | Selettore delle due viste, senza autenticazione reale |
| Dati | Gestione dei dati degli account configurati nella beta | Quattro percorsi inventati e ripristinabili |
| Interfaccia | Interfaccia della beta | Interfaccia dedicata alla presentazione e al confronto sull'esperienza d'uso |
| Flussi comuni | Diario/check-in, homework, note condivise, percorso, Bridge e riepiloghi | Implementazione separata dei flussi presenti nella demo |
| Stato tecnico | Stack più esteso, servizi e configurazioni propri | Streamlit e database SQLite dell'installazione demo |

Le due versioni non condividono il database né tutto il codice. La demo non
dimostra equivalenza funzionale completa, integrazione con Unobravo, efficacia
clinica o idoneità all'impiego con dati reali. Gli scenari contengono testi
narrativi predisposti; i confronti numerici e i contesti ricorrenti sono
descrittivi e non usano un LLM.

## Un percorso principale: Luca Ferri

1. **Panoramica → Luca → Oggi.** Mostrare il passo della cena, i check-in e gli
   homework. Un cambiamento nei comportamenti può essere interessante anche
   quando la persona riferisce ancora ansia.
2. **Homework → Assegna attività.** Scegliere “Respiro 3 minuti” e una scadenza
   successiva alla data dello scenario.
3. **Vedi come paziente.** La persona resta Luca. Aprire l'attività appena
   assegnata, compilare le tre risposte e salvarla. È una simulazione, non
   una prescrizione clinica agli interlocutori.
4. **Area privata.** Creare una nota fittizia. Far vedere che rimane privata
   finché si sceglie di condividerla; usare la conferma di condivisione.
5. **Prepara la seduta.** Selezionare la nota e l'attività completata, scegliere
   una priorità e preparare il Bridge.
6. **Vedi come professionista → Prepara seduta.** Ritrovare il contenuto del
   Bridge, le risposte e la nota condivisa.
7. **Segna come discusso → Archivia Bridge.** Tornando nella vista paziente
   è possibile preparare un nuovo Bridge; quello precedente resta nello storico.

Il check-in è un secondo passaggio interattivo possibile: **Come stai oggi? →
Aggiungi un dettaglio (facoltativo)**. Dopo il salvataggio, il nuovo episodio
compare nell'Andamento del professionista.

## Altri percorsi, se utili durante le domande

- **Giulia:** riepilogo già popolato, ansia mediamente più bassa rispetto
  all'inizio, un episodio recente da riprendere e Bridge pronto con tre fonti.
- **Martina:** stress recente più alto, attività scadute e una nota condivisa
  sull'esame. Mostra anche difficoltà e attività non completate.
- **Andrea:** recupero iniziale di alcune attività e una difficoltà recente
  legata al lavoro.

Questi sono esempi inventati per esplorare il prodotto. Non sono risultati
ottenuti con PsyHelper né dati provenienti dai sondaggi.

## Prima di presentare

1. Usare questa versione della demo e installare le dipendenze fissate in
   `requirements.txt`.
2. Dopo l'aggiornamento, ripristinare i dati dalla sidebar e confermare.
3. Provare il percorso di Luca, compreso un intero ciclo di Bridge.
4. Ripristinare ancora i dati quando la prova è conclusa, per ritrovare lo
   scenario iniziale al momento della presentazione.
5. Tenere una breve registrazione o alcune schermate del percorso già provato.

Le viste della demo mostrano il comportamento di condivisione, ma il cambio
ruolo non protegge accessi personali: usare solo contenuti inventati. Più
visitatori della stessa installazione condividono i dati della demo.

## Cosa chiarire durante il confronto

- Il professionista interpreta le informazioni nel contesto della terapia.
- La compilazione non implica che il professionista legga o risponda subito.
- La revoca nasconde la nota dalle viste successive; non annulla quanto già letto.
- Gli homework proposti sono soprattutto di matrice CBT. L'appropriatezza per
  altri orientamenti va discussa con i professionisti.
- Tempi risparmiati, continuità del percorso e riduzione degli abbandoni sono
  benefici da verificare, non risultati dimostrati da questi esempi.

## Verifiche tecniche

```bash
python -m pytest -q
python -m compileall -q app.py psyhelper
```

I test del flusso di presentazione coprono il salvataggio dei dettagli al primo
invio, il passaggio paziente–professionista, la condivisione e la revoca delle
note, e due cicli consecutivi di Bridge senza riutilizzare la bozza precedente.
