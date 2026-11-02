# 01 — LLM, token, contesto

> **Obiettivi**
> - Spiegare cosa fa davvero un modello a ogni chiamata.
> - Convertire tra testo, token e costo.
> - Prevedere quali compiti falliranno per il contesto, non per l'intelligenza.

## Cosa fa il modello

Un modello linguistico è una funzione:

```
token_in → distribuzione di probabilità sul token successivo
```

Tutto il resto è impalcatura. Non ha memoria, non ha stato, non può eseguire
codice e non sa cosa è successo nella chiamata precedente se quella chiamata non
è nel testo che gli invii.

Tre conseguenze che sentirai ogni giorno:

1. **Assenza di stato.** La "conversazione" è un'illusione. Ogni chiamata
   reinvia l'intera trascrizione. La memoria è l'harness.
2. **Campionamento.** Senza temperatura 0, lo stesso prompt può produrre output
   diversi. Anche a 0 i provider non sono perfettamente riproducibili.
3. **Nessuna esecuzione.** Quando un modello "esegue un test", ha emesso una
   richiesta strutturata. Qualcos'altro ha eseguito il test e ha incollato il
   risultato.

## I token

Un token è un pezzo di parola. Regole pratiche:

| Contenuto | Caratteri/token approx. |
|---|---|
| Prosa inglese | ~4 |
| Python / TypeScript | ~3 |
| JSON, minificato | ~2,5 |
| Base64, hash, JS minificato | ~1,5–2 |
| Scritture non latine | ~1–2 |

Quindi un file Python da 1.000 righe vale circa 10–15k token. Un
`package-lock.json` può valere 100k+ token da solo. **Ecco perché "leggi tutta la
repo" non funziona**, e perché un singolo `cat` distratto può chiudere una
sessione.

Conta, non indovinare:

```python
from mini_agent.context import estimate_tokens
estimate_tokens(open("mini_agent/agent.py").read())
```

## La finestra di contesto

La finestra contiene *tutto* per una singola chiamata:

```
┌──────────────────────────────────────────────────┐
│ system prompt            ~500–3.000 token        │
│ file di istruzioni       ~200–5.000 token        │
│ schemi degli strumenti   ~100–500 token per tool │
│ cronologia conversazione cresce a ogni turno     │
│ risultati degli tool     il solito colpevole     │
│ (riservato) risposta     ~1.000–8.000 token      │
└──────────────────────────────────────────────────┘
```

Due fatti che sorprendono:

- **Gli schemi degli strumenti contano.** Quaranta strumenti sono qualche
  migliaio di token prima ancora di dire qualcosa, spesi a ogni singola
  chiamata.
- **La risposta ha bisogno di spazio.** Se riempi la finestra, il modello non ha
  dove rispondere. Da qui `ContextBudget.reserve`.

### Degrado del contesto

Finestre più grandi non significano che devi usarle tutte. I modelli prestano
attenzione in modo non uniforme: il materiale al centro di un contesto lungo
viene richiamato peggio di quello all'inizio o alla fine, e il contenuto
irrilevante peggiora misurabilmente il ragionamento. Una finestra da 200k
riempita con 180k token di log spesso rende *peggio* di una da 20k con i 5k
giusti.

Tratta la finestra come la RAM nel 1995: preziosa, e il lavoro dell'harness è
decidere cosa resta residente.

## Perché gli agenti falliscono, in termini di modello

| Sintomo | Meccanismo |
|---|---|
| "Ha inventato un file che non esiste" | Continuazione plausibile, nessuna verifica |
| "Ha dimenticato l'istruzione di 40 turni fa" | L'istruzione è uscita dal contesto o è sepolta |
| "Continuava a modificare la stessa riga" | Lettura obsoleta: la sua copia del file è vecchia |
| "Ha ignorato il fallimento del test" | Il testo del fallimento era troncato o sepolto |
| "È peggiorato dopo che ho aggiunto documentazione" | Degrado del contesto: materiale irrilevante diluisce l'attenzione |
| "È lento e costoso" | Ogni turno reinvia tutto; il costo è quadratico nei turni |

Quest'ultimo merita di essere interiorizzato. Costo per turno ≈ (dimensione del
contesto) × (prezzo per token). Dato che il contesto cresce a ogni turno, **una
sessione da 30 turni costa molto più di tre sessioni da 10 turni**. Le sessioni
nuove sono un'ottimizzazione di costo, non solo un'abitudine igienica.

## Determinismo e temperatura

- `temperature=0` riduce la varianza; non la elimina.
- Gli agenti di coding di solito girano vicino a 0 per le modifiche, più alti
  per il brainstorming.
- Il non determinismo è il motivo per cui **le eval hanno bisogno di
  ripetizioni** (modulo 11). Una singola esecuzione verde non dimostra quasi
  nulla.

## Cosa significa per come scrivi i prompt

Dato che il modello vede solo la trascrizione:

- Dì il vincolo *adesso*, non "come dicevo prima".
- Metti le regole critiche nel system prompt o in un file di istruzioni, dove
  vengono reinviate a ogni chiamata — non al turno 3 della chat.
- Preferisci mostrare il codice rilevante invece di descriverlo. I token spesi
  sul file vero battono i token spesi in prosa sul file.
- Quando la qualità cala, la prima ipotesi è il **contesto**, non la capacità.

## Laboratorio

```bash
python3 labs/L01_tokens.py
```

Misurerai i token reali di prosa, codice e JSON, poi vedrai un budget rifiutare
una trascrizione e troncarla.

## ✅ Verifica

1. Perché il costo di un agente cresce più che linearmente con i turni?
2. Una repo da 4.000 righe. Puoi metterla in una finestra da 128k? Dovresti?
3. Cosa significa "senza stato" per come scrivi i messaggi di seguito?
4. Perché temperatura 0 non garantisce la riproducibilità?
5. Nomina due cose che consumano contesto prima che l'utente dica qualcosa.

<details>
<summary>Risposte</summary>

1. Ogni turno reinvia la trascrizione completa, che è cresciuta.
2. Più o meno sì (forse 40–60k token), ma no: degrado, costo e latenza.
3. Ripeti ciò che conta; il modello non ha memoria fuori dalla trascrizione.
4. Non determinismo di hardware/kernel, batching, cambi del provider.
5. System prompt, file di istruzioni, schemi degli strumenti.
</details>
