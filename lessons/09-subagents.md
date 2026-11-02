# 09 — Subagenti e orchestrazione

> **Obiettivi**
> - Decidere quando un subagente vale il suo costo.
> - Spiegare il compromesso dell'isolamento in entrambe le direzioni.
> - Eseguire lavoro in parallelo senza corrompere il workspace.

## L'economia

Un subagente è **un compressore di contesto con una chiamata di rete in mezzo**.

```
contesto del padre:  12.000 token
esecuzione del figlio: 40.000 token di esplorazione
restituiti:              300 token di conclusione
```

Hai speso 40k token per risparmiare 40k token di contesto del padre. È un
guadagno solo se:

- l'esplorazione è davvero grande (molti file, molti vicoli ciechi),
- la conclusione è compatta e verificabile,
- il padre non ha bisogno delle prove grezze.

Se il padre ha bisogno del diff, dell'output dei test o del ragionamento, fai il
lavoro inline. Un riassunto non si può rileggere.

## Quando delegare

| Delega | Tieni inline |
|---|---|
| "Trova ogni punto di chiamata di X" | "Correggi questa funzione" |
| "Analizza questo modulo per rischi di injection" | "Aggiungi un controllo su null" |
| "Esegui la suite e riporta i fallimenti" | "Fai passare questo test" |
| "Rivedi questo diff per bug" | "Implementa la funzionalità" |
| Indagini indipendenti in sola lettura | Qualsiasi cosa con stato condiviso ed evolutivo |

Il pattern che funziona meglio: **espandi in parallelo per leggere, serializza
per scrivere.**

## Isolamento, in entrambe le direzioni

```
trascrizione padre ──X──► figlio        (nessuna cronologia del padre entra)
trascrizione figlio ──X──► padre        (torna solo il riassunto)
workspace            ─────► condiviso   (le modifiche persistono)
```

Le `X` sono la funzionalità. Il figlio non può fare domande di chiarimento, non
sa cosa il padre ha già escluso e non conosce il tono dell'utente. Quindi il
compito deve essere **autosufficiente**:

```
Male : "Correggi quella cosa di cui abbiamo parlato."
Bene : "Nella repo /work/app, scopri perché `test_checkout` fallisce. Riporta
        causa radice e file:riga, senza modificare nulla."
```

L'ultima clausola conta: senza, un'indagine in sola lettura inizia a modificare.

## Il gioco del telefono

Un subagente restituisce prosa. La prosa perde dettagli. Il padre agisce sulla
versione impoverita.

```
figlio:  "il bug è nella logica di retry in client.py:88"
padre:   "correggi la logica di retry in client.py"
→ il padre modifica il retry sbagliato (ce ne sono tre)
```

Mitigazioni:

- Richiedi **output strutturato**: `file:riga`, identificatori esatti, nomi dei
  test.
- Richiedi che il figlio **citi** le prove, non le parafrasi.
- Rendi il riassunto **verificabile**: il padre rilegge il punto citato.
- Preferisci figli che restituiscono *diff o patch* invece di descrizioni,
  quando possono scrivere.

## Parallelismo e race condition

```python
results = run_parallel(parent, {
    "security": "analizza src/ per injection",
    "tests":    "esegui la suite, riporta i fallimenti",
})
```

È sicuro solo perché entrambi i lavori sono in sola lettura. Se due agenti
scrivono lo stesso file:

```
agente A legge app.py (v1)
agente B legge app.py (v1)
A scrive v2
B scrive v3, basato su v1  → la modifica di A è sparita
```

Opzioni, dalla migliore:

1. **Non parallelizzare le scritture.** Serializza o partiziona per proprietario
   del file.
2. **Worktree.** Un checkout per agente, merge dopo. I conflitti diventano merge
   visibili invece di sovrascritture silenziose.
3. **Lock sui file.** Economici, ma gli agenti ritentano e si bloccano; solo per
   partizioni grossolane.

L'helper `run_parallel` in `mini_agent/subagents.py` lo dice ad alta voce: è
onesto sul fatto di non essere sicuro per le scritture.

## Il pattern della revisione

Il pattern di orchestrazione con più valore in pratica:

```
implementatore (scrive la modifica)
        │
        ▼  diff
revisore (contesto pulito, non conosce l'intento)
        │
        ▼  risultati: file:riga + gravità + suggerimento
implementatore (affronta i risultati)
```

Il valore del revisore viene dal **non sapere perché** la modifica è stata fatta.
Legge il diff a freddo, come farebbe un collega. Un revisore che condivide il
contesto dell'implementatore eredita i suoi punti ciechi.

Due regole:

- Il revisore deve essere **in sola lettura**. Un revisore che può modificare
  "aiuterà" riscrivendo cose.
- Il revisore deve **citare le righe**. "Si potrebbe pulire" è rumore.

## Modello di costo

| Esecuzione | Turni | Contesto/turno | Costo relativo |
|---|---|---|---|
| Esplorazione inline | 20 | cresce fino a 30k | 1,0× |
| Esplorazione con subagente | 25 (figlio) | limitato a 15k | ~0,6× padre + figlio |
| Parallelo in lettura ×3 | 15 ciascuno | 10k ciascuno | ~1,5×, 3× più veloce |

I subagenti non sono gratuiti. Sono un modo per scambiare **denaro e latenza**
con **spazio nel contesto e parallelismo**. Misura prima di adottarli.

## Modalità di fallimento

| Fallimento | Causa | Soluzione |
|---|---|---|
| Il figlio fa il compito sbagliato | Compito ambiguo | Prompt autosufficiente con perimetro |
| Il padre applica male il riassunto | Prosa lossy | Output strutturato + verifica della citazione |
| Lavoro duplicato | Anche il padre ha indagato | Divisione del lavoro esplicita |
| Sovrascrittura silenziosa | Scritture parallele | Serializza o usa worktree |
| Fan-out fuori controllo | Il figlio genera figli | Limite di profondità, budget per figlio |
| Costo esploso | Molti figli, esecuzioni lunghe | Limita numero e turni; logga i token |

## Laboratorio

```bash
python3 labs/L09_subagents.py
```

Eseguirai un padre che delega due indagini in sola lettura, ispezionerai le
trascrizioni dei figli (solo system + user) e confermerai che il contesto del
padre resta piccolo. Poi riprodurrai una race di scrittura e la risolverai
serializzando.

🔬 **Fallo fallire:** fai scrivere lo stesso file a due figli e confronta il
risultato.

## ✅ Verifica

1. Cosa cede un subagente, e cosa compra?
2. Perché il prompt di delega deve essere autosufficiente?
3. Perché il pattern della revisione è più forte con un contesto pulito?
4. Quando la scrittura parallela è sicura?
5. Qual è il fallimento del gioco del telefono e come lo mitighi?

<details>
<summary>Risposte</summary>

1. Cede fedeltà/prove e denaro; compra spazio nel contesto e parallelismo.
2. Il figlio non vede la cronologia del padre e non può fare domande.
3. Non eredita le assunzioni e i punti ciechi dell'implementatore.
4. Solo con file disgiunti o worktree separati; altrimenti serializza.
5. I riassunti perdono dettagli e il padre agisce sulla perdita; richiedi output
   strutturato, citato e verificabile.
</details>
