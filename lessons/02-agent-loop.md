# 02 — Il ciclo dell'agente

> **Obiettivi**
> - Seguire un'esecuzione come macchina a stati.
> - Implementare il ciclo, inclusi terminazione e gestione degli errori.
> - Riconoscere i quattro bug classici del ciclo.

## Anatomia di un turno

```
        ┌────────────────────────────────────────────┐
        │ 1. applica il budget alla trascrizione     │
        │ 2. modello(trascrizione, schemi_tool)      │
        │ 3. aggiungi il messaggio dell'assistente   │
        │ 4. nessuna chiamata agli strumenti → FINE  │
        │ 5. per ogni chiamata:                      │
        │      pre-hook → dispatch → post-hook       │
        │      aggiungi il risultato                 │
        └───────────────────┬────────────────────────┘
                            └──► turno successivo
```

Questo è `Agent.run` in `mini_agent/agent.py`, meno il logging. Vale la pena
leggere il file una volta, lentamente.

## La trascrizione è lo stato

Non c'è memoria nascosta. Lo stato dell'esecuzione è la lista di messaggi:

```python
[
  Message("system", "..."),
  Message("user", "correggi il bug"),
  Message("assistant", "", [ToolCall("c1", "read_file", {...})]),
  Message("tool", "...contenuto del file...", tool_call_id="c1"),
  Message("assistant", "Corretto."),
]
```

Tre invarianti:

1. **Accoppiamento.** Ogni `ToolCall.id` riceve esattamente un messaggio `tool`
   con lo stesso id, subito dopo. Rompilo e l'API risponde 400.
2. **Ordine.** I risultati degli strumenti seguono il messaggio dell'assistente,
   nello stesso ordine.
3. **Ruoli.** `system` per primo, poi `user`/`assistant` alternati, con messaggi
   `tool` solo dopo una chiamata dell'assistente.

La maggior parte dei bug "l'agente è rotto" è un invariante violato, non un
modello scadente.

## Terminazione

Un agente ha bisogno di almeno quattro uscite:

| Uscita | Innesco | Risultato |
|---|---|---|
| `completed` | l'assistente risponde senza chiamate | successo |
| `max_turns` | contatore dei turni al limite | parziale, da rivedere |
| `error` | modello/trasporto solleva un'eccezione | fallimento con messaggio |
| `budget` | la trascrizione non entra | fallimento o compressione forzata |

`max_turns` non è un lusso. I modelli si incastrano in cicli di tentativi —
chiamano lo stesso strumento fallito con gli stessi argomenti, per sempre. Un
limite trasforma una bolletta infinita in una trascrizione da esaminare.

```python
for turns in range(1, max_turns + 1):
    ...
else:
    stopped = "max_turns"
```

Nota il `for/else`: l'`else` scatta solo se non c'è stato `break`, cioè se il
modello non ha mai finito. È esattamente la semantica che vuoi.

## Contenimento dei fallimenti

Il ciclo deve sopravvivere a:

- **Errori degli strumenti** → restituiti come messaggio `tool`, così il modello
  può adattarsi.
- **Azioni negate** → restituite come `DENIED: motivo`, così il modello può
  scegliere un'altra strada invece di cadere.
- **Errori del modello** → catturati in `RunResult.error`, trascrizione
  conservata.
- **Argomenti malformati** → rifiutati dal dispatch, riportati come testo.

```python
result = tools.dispatch(call.name, args)   # non solleva mai
```

Confronta con la versione ingenua, `getattr(tools, name)(**args)`, che
trasforma un argomento sbagliato in una sessione morta.

## I quattro bug classici del ciclo

**1. La chiamata orfana.** Tagli la cronologia e finisci tra una chiamata
dell'assistente e il suo risultato. Soluzione: taglia ai confini del turno
(vedi `ContextBudget.enforce`).

**2. Il tentativo silenzioso.** Uno strumento fallisce; l'harness ingoia l'errore
e restituisce una stringa vuota. Il modello vede "successo", ripete la stessa
azione e bruci 20 turni. Soluzione: gli errori sono messaggi, sempre.

**3. Il ciclo illimitato.** Nessun limite di turni, nessun budget. Soluzione:
entrambi, sempre.

**4. La risposta finale perduta.** L'ultimo turno contiene sia una chiamata a uno
strumento sia della prosa; restituisci la prosa prima che arrivi il risultato.
Soluzione: un'esecuzione è completa solo quando una risposta *non* ha chiamate
agli strumenti.

## ReAct, in breve

Il paper ReAct del 2022 ha formalizzato l'alternanza *ragiona → agisci →
osserva*. Gli agenti moderni sono ReAct con strumenti migliori, ma l'etichetta
compare ancora in paper e annunci di lavoro. Ciò che conta in pratica:

- Il testo di ragionamento prima di una chiamata migliora la scelta dello
  strumento.
- Il testo di ragionamento **non** è verificato. "Ho controllato i test" può
  essere una bugia; solo il risultato dello strumento è una prova.

Questa asimmetria — il ragionamento è chiacchiera a buon mercato, i risultati
degli strumenti sono prove — è il cuore del modulo 11.

## Osservabilità

Ogni turno dovrebbe emettere eventi strutturati. L'harness qui emette
`turn_start`, `tool`, `tool_denied`, `edit_denied`, `turn_end`, `session_end`.
Non ti serve una dashboard il primo giorno; ti servono una trascrizione e un log
che puoi cercare quando qualcosa va storto alle 17.

```python
agent = Agent(..., on_event=lambda e, p: print(e, p))
```

## Laboratorio

```bash
python3 labs/L02_loop.py
```

Il laboratorio esegue quattro scenari: un compito pulito in due turni, un errore
di uno strumento da cui il modello si riprende, un modello bloccato in un ciclo
di tentativi che colpisce `max_turns` e un'azione negata. Leggi ogni
trascrizione.

🔬 **Fallo fallire:** elimina il `break` quando non ci sono chiamate agli
strumenti e guarda il modello preimpostato esaurirsi. Poi togli il limite di
turni e guarda che non si ferma mai.

## ✅ Verifica

1. Quali sono i tre invarianti della trascrizione e cosa si rompe violando
   ciascuno?
2. Perché restituire gli errori degli strumenti come messaggi invece di
   sollevarli?
3. Quando un'esecuzione è "completa"?
4. Perché il ciclo applica il budget *prima* della chiamata al modello?
5. Qual è la differenza tra testo di ragionamento e prova?

<details>
<summary>Risposte</summary>

1. Accoppiamento (API 400), ordine (API 400 / modello confuso), ruoli (API 400).
2. Così il modello può adattarsi; un'eccezione uccide l'esecuzione e perde il
   lavoro.
3. Quando un messaggio dell'assistente non ha chiamate agli strumenti.
4. L'overflow è irrecuperabile a chiamata iniziata; troncare dopo è troppo tardi.
5. Il ragionamento è testo non verificato; i risultati degli strumenti sono
   osservazioni dell'ambiente.
</details>
