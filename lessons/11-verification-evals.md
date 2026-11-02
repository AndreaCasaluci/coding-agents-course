# 11 — Verifica ed eval

> **Obiettivi**
> - Costruire una scala di verifica e sapere a che gradino sei.
> - Progettare un'eval che misura i risultati, non le impressioni.
> - Riportare pass@k con onestà.

## L'asimmetria centrale

L'affermazione di successo di un modello è **testo**. Il risultato di un test è
**prova**. Gli agenti sono fluenti nella prima e producono la seconda solo
occasionalmente da soli.

Quindi il compito più prezioso dell'harness non è generare codice. È **creare
segnali di fallimento economici e non ambigui** su cui il ciclo possa agire.

```
il modello dice "fatto"  ──►  è vero?
                                │
                                ├─ nessun segnale  → ti fidi della prosa
                                └─ risultato test  → stai facendo ingegneria
```

## La scala della verifica

Dal più economico e affidabile:

| Gradino | Segnale | Cattura | Non cattura |
|---|---|---|---|
| 1 | parsing / compilazione | errori di sintassi | tutto il resto |
| 2 | linter | stile, bug ovvi | logica |
| 3 | type checker | disallineamenti di interfaccia | comportamento a runtime |
| 4 | test unitari | comportamento specificato | integrazione, buchi nella specifica |
| 5 | integrazione / e2e | cablaggio, I/O reale | prestazioni, UX |
| 6 | revisione manuale del diff | intento, design | scala |

Un agente con i gradini 1–4 nel ciclo si autocorreggerà per la maggior parte
degli errori. Un agente senza nessuno rilascerà codice rotto con sicurezza.

**La cosa a più alto impatto che puoi fare per la qualità dell'agente è rendere
la suite di test veloce ed eseguibile dall'agente.** Non un modello migliore. Una
suite da 2 secondi cambia il comportamento; una da 10 minuti viene saltata.

## L'autorevisione è debole; la revisione esterna no

"Rivedi la tua modifica" produce soprattutto rassicurazione. Il modello si è già
impegnato su un piano e lo razionalizzerà.

Cosa funziona:

- **Esegui qualcosa** che possa contraddirlo (test, typechecker, un secondo
  modello con contesto pulito — modulo 09).
- **Chiedi una revisione del diff con una rubrica**: correttezza, casi limite,
  sicurezza, copertura dei test, scope creep. Categorie specifiche producono
  risultati specifici.
- **Pretendi prove nella risposta**: "incolla il comando e il suo output".

## Anatomia di un'eval

Un'eval è tre cose:

```python
EvalCase(
    name="fix empty-date crash",
    task="parse_date('') va in crash. Correggila senza cambiare la firma.",
    setup=lambda ws: seed_repo(ws),
    check=lambda result, ws: run_tests(ws) or "i test falliscono ancora",
)
```

1. **Compito** — un'istruzione autosufficiente.
2. **Ambiente** — un workspace *nuovo*, inizializzato allo stesso modo ogni
   volta.
3. **Valutatore** — una funzione sul risultato (file, esito dei test), non sulla
   trascrizione.

Quest'ultimo è l'errore più comune. Valutare `"ha chiamato edit_file?"` premia
l'imitazione. Valutare `"passano i test?"` premia il risultato.

## Regole che rendono affidabili le eval

| Regola | Perché |
|---|---|
| Stato nuovo per ogni caso | Altrimenti testi l'ordine di esecuzione |
| Valuta i risultati | Le trascrizioni sono fragili e aggirabili |
| Includi un caso in cui l'agente deve **rifiutare** | Cattura l'eccesso di zelo |
| Includi un caso **no-op** | Cattura le modifiche inutili |
| Fissa modello e impostazioni | Altrimenti il numero non significa nulla |
| Esegui k volte | Il non determinismo rende una singola esecuzione rumore |
| Tieni un set di riserva | Altrimenti fai overfitting dei prompt sull'eval |

## pass@k, e perché un'esecuzione verde mente

Se un agente riesce il 70% delle volte, una singola esecuzione è un lancio di
moneta che il più delle volte esce testa. Riporta:

```
pass@1 = 0,70     pass@3 = 0,97     pass@5 = 0,998
```

Per gli agenti di coding il numero che conta è di solito **pass@1 senza
retry** — è ciò che la tua CI sperimenterà. pass@k con k tentativi è ciò che
sperimenta un umano nel ciclo.

## Eval instabili

Un'eval che passa e fallisce senza modifiche al codice è peggio di nessuna eval:
ti insegna a ignorare i fallimenti.

Cause comuni:

- directory temporanee o porte condivise,
- dipendenza da data/ora,
- chiamate di rete,
- assunzioni sull'ordine,
- temperatura del modello non deterministica,
- un valutatore che dipende dalla trascrizione.

Metti in quarantena i casi instabili, poi correggi l'ambiente. Non fare mai "solo
un retry" in CI senza registrarlo.

## Suite di regressione

La suite di eval cresce dagli incidenti:

```
bug trovato in produzione
  → scrivi un'eval che lo riproduce
  → correggi agente/prompt/strumento
  → l'eval resta per sempre
```

È esattamente come crescono le suite di test, e funziona per lo stesso motivo:
trasforma un fallimento isolato in un guardrail permanente.

## Metriche non vanitose

| Metrica | Cosa ti dice |
|---|---|
| pass@1 su una suite fissa | capacità |
| turni per successo | efficienza |
| token per successo | costo |
| modifiche umane dopo l'agente | divario di qualità |
| tasso di revert | correttezza nel mondo reale |
| tempo al primo diff utile | latenza |
| % di sessioni abbandonate | usabilità |

"Righe di codice generate" non è nella lista. Misura la cosa sbagliata.

## Laboratorio

```bash
python3 labs/L11_evals.py
```

Costruirai una suite di tre casi (una correzione, un no-op, un rifiuto), la
eseguirai contro due modelli preimpostati e vedrai uno passare e uno fallire —
poi calcolerai pass@k su una policy instabile.

🔬 **Fallo fallire:** valuta su `result.tool_calls` invece che sul workspace e
guarda un agente sbagliato ma plausibile passare.

## ✅ Verifica

1. Perché il "fatto" di un modello non è una prova?
2. Nomina la scala della verifica dal più economico al più forte.
3. Perché le eval devono valutare i risultati, non le trascrizioni?
4. Perché un'esecuzione verde non è un risultato?
5. Cosa rende instabile un'eval, e perché è peggio di nessuna eval?

<details>
<summary>Risposte</summary>

1. È testo non verificato; solo le osservazioni dell'ambiente sono prove.
2. Compila → lint → tipi → unit → integrazione → revisione manuale.
3. Le trascrizioni sono fragili e premiano l'imitazione; i risultati misurano
   l'esito.
4. Non determinismo: servono k esecuzioni e un numero pass@k.
5. Stato condiviso, tempo, rete, ordine; ti abitua a ignorare i fallimenti.
</details>
