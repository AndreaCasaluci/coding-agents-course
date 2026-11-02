# 00 — Orientamento

> **Obiettivi**
> - Definire "agente di coding" in modo abbastanza preciso da poterne discutere.
> - Nominare i cinque componenti che ogni agente possiede.
> - Leggere una trascrizione e dire cosa è successo, in ordine.

## La definizione in una frase

Un agente di coding è **un modello linguistico in un ciclo, con strumenti, dentro
un ambiente, sotto un budget, guidato da un umano.**

Ogni parola conta. Togli il ciclo e hai un chatbot. Togli gli strumenti e hai un
commentatore di codice. Togli l'ambiente e hai un generatore di testo. Togli il
budget e hai un processo fuori controllo. Togli l'umano e hai uno stagista
molto sicuro di sé con accesso root.

## Cosa non è

| Cosa | Perché non è un agente |
|---|---|
| Autocompletamento | Una sola previsione, nessuna azione, nessun ciclo |
| Assistente chat | Parla di codice, non lo esegue né lo modifica |
| "IDE potenziato dall'AI" | È un prodotto; può contenere o meno un agente |
| Motore di workflow | Grafo deterministico; il modello non sceglie il percorso |
| *Framework* per agenti | Una libreria per costruire agenti, non un agente |

La distinzione che conta: **chi decide l'azione successiva?** In un workflow il
grafo l'ha scritto un umano. In un agente il modello sceglie a ogni passo,
entro i limiti fissati dall'harness.

## I cinque componenti

```
            ┌──────────────────────────────────────────┐
            │                  UMANO                   │
            │      compito, approvazioni, revisione    │
            └───────────────────┬──────────────────────┘
                                │
        ┌───────────────────────▼───────────────────────┐
        │                  HARNESS                      │
        │  system prompt · budget di contesto · ciclo · │
        │  permessi · hook · logging                    │
        └───────┬───────────────────────────┬───────────┘
                │                           │
      ┌─────────▼─────────┐       ┌─────────▼─────────┐
      │      MODELLO      │       │    STRUMENTI      │
      │  previsione del   │       │  leggi · modifica │
      │  token successivo │       │  cerca · shell    │
      └───────────────────┘       └─────────┬─────────┘
                                            │
                                  ┌─────────▼─────────┐
                                  │     AMBIENTE      │
                                  │  repo, runtime,   │
                                  │  rete, segreti    │
                                  └───────────────────┘
```

1. **Modello** — funzione senza stato: testo in ingresso, testo in uscita.
   Nessuna memoria tra una chiamata e l'altra.
2. **Harness** — il programma attorno. Possiede il ciclo, la trascrizione, il
   budget e i guardrail. È ciò che configuri davvero.
3. **Strumenti** — l'unico modo che il modello ha di influire sul mondo.
   Descritti in testo.
4. **Ambiente** — la repo, la shell, la suite di test, le credenziali.
5. **Umano** — imposta il compito, approva le azioni rischiose, giudica il
   risultato.

L'harness è la parte sottovalutata. Due prodotti con lo stesso modello possono
comportarsi in modo completamente diverso perché i loro harness sono diversi.
Quando qualcuno dice "il modello X è più bravo a programmare", chiedi con quale
harness.

## Una singola esecuzione, passo per passo

Compito: *"La funzione `parse_date` va in crash su input vuoto. Correggila."*

```
turno 1  modello: devo trovare parse_date.       → search("def parse_date")
         tool   : src/dates.py:41: def parse_date(s):
turno 2  modello: leggo il codice.                → read_file("src/dates.py", 35, 55)
         tool   : [50 righe di codice]
turno 3  modello: aggiungo un controllo.          → edit_file(path, old, new)
         tool   : Edited src/dates.py (1 replacement)
turno 4  modello: verifico.                       → run_tests("tests/test_dates.py")
         tool   : FAILED test_empty_string
turno 5  modello: il test si aspetta ValueError, non None. Correggo il controllo.
                                                  → edit_file(...)
turno 6  modello: verifico di nuovo.              → run_tests(...)
         tool   : 12 passed
turno 7  modello: fatto. Controllo aggiunto, test verdi.
```

Sette chiamate al modello, quattro chiamate agli strumenti, un tentativo
fallito. **Il fallimento è la parte interessante**: è il ciclo, non il modello,
che ha trasformato una prima ipotesi sbagliata in una correzione giusta.

## Perché il ciclo è l'unità di progettazione

Una singola chiamata al modello non può correggere i propri errori. Un ciclo sì,
perché il risultato dello strumento rientra nel contesto e il modello ha una
seconda possibilità. È tutto qui il valore — e anche tutto il rischio, perché un
ciclo che non riconosce il fallimento peggiorerà le cose per venti turni.

Quindi il compito dell'harness è rendere il fallimento **visibile ed economico**:

- errori degli strumenti restituiti come testo, non come eccezioni,
- test come verità di riferimento,
- limiti di turni e di budget,
- una trascrizione che puoi rileggere dopo.

## Dove porta questo corso

I moduli 1–3 danno le primitive: token, il ciclo, gli strumenti. I moduli 4–8
costruiscono la macchina che rende gli agenti usabili: filesystem, gestione del
contesto, istruzioni, skill, hook. I moduli 9–12 coprono scala e sicurezza. I
moduli 13–14 sono pratica e team. Il modulo 15 è un progetto finale in cui ne
costruisci uno.

Tutto è dimostrato in `mini_agent/`, circa 2.000 righe di Python senza
dipendenze. Leggilo insieme alle lezioni.

## Laboratorio

```bash
python3 labs/L00_orientation.py
```

Il laboratorio esegue un agente con risposte preimpostate e stampa la
trascrizione grezza. Il tuo compito è annotarla: quali messaggi vengono dal
modello, quali dagli strumenti e dove è cresciuto il contesto.

## ✅ Verifica

1. Perché un assistente chat che "ti scrive il codice" non è un agente?
2. Nomina i cinque componenti e una modalità di fallimento di ciascuno.
3. Nell'esempio sopra, cosa sarebbe successo senza lo strumento di test?
4. Perché due prodotti con lo stesso modello possono comportarsi diversamente?
5. Qual è il compito dell'harness quando uno strumento fallisce?

<details>
<summary>Risposte</summary>

1. Non agisce. Niente strumenti, niente ciclo, nessuna modifica all'ambiente.
2. Modello (allucinazione, obsolescenza), harness (contesto/limiti sbagliati),
   strumenti (schema errato, effetti collaterali pericolosi), ambiente
   (dipendenze mancanti, segreti), umano (compito vago, approvazione
   automatica).
3. L'agente avrebbe dichiarato successo dopo il turno 3, con una correzione che
   non rispetta la specifica.
4. Harness diversi: prompt, strumenti, gestione del contesto, guardrail.
5. Trasformarlo in un messaggio che il modello può leggere e a cui può reagire,
   senza far cadere l'esecuzione.
</details>
