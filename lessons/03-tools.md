# 03 — Strumenti e function calling

> **Obiettivi**
> - Spiegare con precisione il giro completo del function calling.
> - Scrivere schemi e descrizioni che vengono chiamati correttamente.
> - Progettare una superficie di strumenti abbastanza piccola da poterla
>   scegliere.

## Il giro completo

```
harness                          modello
   │                               │
   │  messaggi + [schemi tool] ───►│
   │                               │  decide: chiama read_file
   │◄── assistant.tool_calls ──────│
   │                               │
   │  esegue read_file(...)        │
   │                               │
   │  messaggio tool (risultato) ─►│
   │                               │  continua a ragionare
```

Il modello emette una *richiesta*. L'harness valida, esegue e aggiunge il
risultato. **Il modello non esegue mai nulla.** Questo è il confine di sicurezza
e il confine di debug: se uno strumento ha fatto qualcosa di sbagliato, l'ha
fatto l'harness.

## Uno strumento è un prompt

```python
@tool
def read_file(path: str, start: int = 1, end: int | None = None) -> str:
    """Legge un file di testo. Opzionalmente legge solo le righe [start, end]."""
    ...
```

diventa:

```json
{
  "name": "read_file",
  "description": "Legge un file di testo. Opzionalmente legge solo le righe [start, end].",
  "parameters": {
    "type": "object",
    "properties": {
      "path":  {"type": "string"},
      "start": {"type": "integer", "default": 1},
      "end":   {"type": "integer", "default": null}
    },
    "required": ["path"]
  }
}
```

La descrizione è **testo di prompt**. "Leggi un file" e "Legge un file di testo.
Opzionalmente legge solo le righe [start, end]. Usalo prima di modificare."
producono comportamenti diversi. Scrivi le descrizioni per il modello, non per il
tuo IDE.

### Regole per gli schemi

| Regola | Perché |
|---|---|
| Parametri piatti | Gli oggetti annidati sono dove i modelli inventano struttura |
| Pochi parametri | Ognuno è un'occasione di sbagliare |
| Enum invece di stringhe libere | `mode: "fast" \| "thorough"` batte `mode: "..."` |
| Default per tutto ciò che è opzionale | Riduce gli errori sui campi obbligatori |
| Nomi che dicono il verbo | `search_code` > `query` |
| Nessun segreto nei default | Gli schemi vengono inviati a una terza parte |

## Dispatch: valida, esegui, contiene

```python
def dispatch(self, name, arguments):
    tool = self.get(name)
    if tool is None:
        return ToolResult(False, f"Unknown tool `{name}`")
    if "__parse_error__" in arguments:
        return ToolResult(False, "Could not parse arguments")
    return tool.run(arguments)          # cattura TypeError ed Exception
```

Tre classi di fallimento, tutte restituite come testo:

1. **Strumento sconosciuto** — il modello ha inventato un nome. Includi l'elenco
   dei disponibili così può recuperare.
2. **Argomenti malformati** — errore di parsing JSON o chiavi sbagliate. Dì
   quali.
3. **Eccezione dello strumento** — la funzione è esplosa. Includi tipo e
   messaggio.

Non lasciare mai che un'eccezione di uno strumento sfugga al ciclo. Il modello
non può correggere un problema che non vede.

## Progettare i risultati

I risultati finiscono direttamente nella finestra di contesto, quindi la loro
dimensione è una scelta di progetto:

- **Tronca a un limite noto** e dillo: `[truncated: 120k chars, showing 40k]`.
- **Pagina per righe** nelle letture; lascia che il modello chieda un intervallo.
- **Sintetizza i comandi rumorosi**: `pytest -q`, non `pytest -vv`, se non stai
  debuggando.
- **Includi la posizione** nei risultati di ricerca (`path:line: testo`) così la
  lettura successiva è mirata.
- **Restituisci testo stabile**, senza codici colore ANSI o barre di
  avanzamento.

Uno strumento che restituisce 50k token per chiamata distrugge la sessione in
quattro turni. È un bug dell'harness, non del modello.

## Effetti collaterali

Marca gli strumenti che cambiano lo stato. L'harness lo usa per permessi, hook e
prompt dell'interfaccia:

```python
@tool(side_effect=True, needs_permission=True)
def write_file(path: str, content: str) -> str: ...
```

Gli strumenti in sola lettura di solito possono girare senza supervisione.
Scritture, cancellazioni, chiamate di rete e comandi shell hanno bisogno di una
politica. Il modulo 12 parla interamente di questa politica.

## Quanti strumenti?

Due pressioni opposte:

- Troppo pochi → il modello non può esprimere il compito.
- Troppi → la precisione di selezione cala, gli schemi mangiano contesto e i
  nomi simili vengono confusi.

Indicazioni pratiche:

- **Sotto i ~20 strumenti** si sta comodi; oltre, raggruppa o carica su richiesta.
- **Evita quasi-duplicati.** `read_file` e `cat_file` verranno confusi.
- **Preferisci uno strumento flessibile** a cinque stretti quando lo spazio dei
  parametri è lo stesso (`search(pattern, glob)` batte `search_py`, `search_js`).
- **Carica insiemi di strumenti per compito** (la divulgazione progressiva del
  modulo 07 vale anche per gli strumenti).

💡 *In pratica* — La maggior parte degli agenti di coding converge su un nucleo
simile: leggi, scrivi, modifica, elenca/glob, grep, esegui comando. Le
differenze stanno nei modelli di permesso e nella formattazione dei risultati,
non nei verbi.

## Lo strumento shell è speciale

Uno strumento shell è il più potente e il più pericoloso che puoi esporre.
Include ogni altro strumento (`cat`, `sed`, `find`, `git`) e ogni attacco
(`rm -rf`, `curl | sh`, `git push --force`).

Se ne esponi uno, l'harness deve:

- eseguirlo in una sandbox o con una allowlist,
- limitare l'output,
- impostare un timeout,
- non passare mai testo del modello attraverso una shell senza quoting.

Il modulo 12 copre i dettagli. Per ora: tratta `run_shell` come un'arma
carica, non come una comodità.

## Laboratorio

```bash
python3 labs/L03_tools.py
```

Ispezionerai gli schemi generati, eseguirai chiamate valide e non valide e vedrai
una descrizione scadente causare la scelta sbagliata in un modello
preimpostato.

🔬 **Fallo fallire:** aggiungi un secondo strumento chiamato `read` che legge
anche i file. Guarda la policy scegliere quello sbagliato.

## ✅ Verifica

1. Chi esegue una chiamata a uno strumento? Cosa emette davvero il modello?
2. Perché gli errori degli strumenti vengono restituiti come messaggi?
3. Elenca tre regole per gli schemi e il fallimento che prevengono.
4. Qual è il costo di uno strumento che restituisce 50k token?
5. Perché uno strumento shell è categoricamente diverso da `read_file`?

<details>
<summary>Risposte</summary>

1. L'harness. Il modello emette un nome + argomenti JSON.
2. Così il modello può adattarsi e l'esecuzione sopravvive.
3. Piatti (annidamento inventato), enum (valori non validi), default (campi
   obbligatori mancanti).
4. Consuma il budget di contesto ed elimina il compito vero.
5. Include tutti gli altri strumenti e tutte le operazioni distruttive; il suo
   raggio d'impatto è l'intera macchina.
</details>
