# Curriculum

Sedici moduli. Circa 1–3 ore ciascuno, laboratorio incluso. I moduli 0–3 sono le
fondamenta; 4–8 sono il macchinario; 9–14 sono la pratica professionale; 15 è
il capstone.

## Parte I — Fondamenta

| # | Modulo | Domanda centrale | Laboratorio |
|---|--------|---------------|-----|
| 00 | [Orientamento](lessons/00-orientation.md) | Che cos'è *esattamente* un agente di coding? | `labs/L00_orientation.py` |
| 01 | [LLM, token, contesto](lessons/01-llms-tokens-context.md) | Quali sono i vincoli reali del modello? | `labs/L01_tokens.py` |
| 02 | [Il ciclo dell'agente](lessons/02-agent-loop.md) | Come fa un singolo turno a diventare un task? | `labs/L02_loop.py` |
| 03 | [Strumenti e function calling](lessons/03-tools.md) | Come fa un modello a *fare* qualcosa? | `labs/L03_tools.py` |

## Parte II — Il macchinario

| # | Modulo | Domanda centrale | Laboratorio |
|---|--------|---------------|-----|
| 04 | [Il filesystem come mondo](lessons/04-filesystem.md) | Perché gli agenti vivono in una repo? | `labs/L04_filesystem.py` |
| 05 | [Ingegneria del contesto](lessons/05-context-engineering.md) | Cosa dovrebbe stare nella finestra, e cosa no? | `labs/L05_context.py` |
| 06 | [Istruzioni e file di regole](lessons/06-instructions.md) | Come guidi un agente senza riscriverti ogni volta? | `labs/L06_instructions.py` |
| 07 | [Skill](lessons/07-skills.md) | Come trasmetti competenza a un agente su richiesta? | `labs/L07_skills.py` |
| 08 | [Hook ed eventi del ciclo di vita](lessons/08-hooks.md) | Come rendi deterministico il comportamento? | `labs/L08_hooks.py` |

## Parte III — Scala e sicurezza

| # | Modulo | Domanda centrale | Laboratorio |
|---|--------|---------------|-----|
| 09 | [Subagenti e orchestrazione](lessons/09-subagents.md) | Come parallelizzi senza perdere il filo? | `labs/L09_subagents.py` |
| 10 | [MCP e interoperabilità](lessons/10-mcp.md) | Come diventano portabili gli strumenti? | `labs/L10_mcp.py` |
| 11 | [Verifica ed eval](lessons/11-verification-evals.md) | Come sai che l'agente aveva ragione? | `labs/L11_evals.py` |
| 12 | [Sicurezza, permessi, sandboxing](lessons/12-safety.md) | Come delimiti il raggio d'impatto? | `labs/L12_safety.py` |

## Parte IV — Pratica

| # | Modulo | Domanda centrale | Laboratorio |
|---|--------|---------------|-----|
| 13 | [Flussi di lavoro che funzionano](lessons/13-workflows.md) | Com'è una buona sessione con l'agente? | `labs/L13_workflows.py` |
| 14 | [Team, CI, misurazione](lessons/14-teams-ci.md) | Come sopravvive questo al contatto con un team? | `labs/L14_ci.py` |
| 15 | [Capstone](lessons/15-capstone.md) | Sai costruirne e difenderne uno reale? | `capstone/` |

## Risultati di apprendimento

Alla fine dovresti essere in grado di:

- Spiegare un'esecuzione dell'agente come una sequenza di chiamate al modello, chiamate
  agli strumenti e mutazioni del contesto — e localizzare un fallimento in quella sequenza.
- Scrivere lo schema di uno strumento e un dispatcher, e ragionare sulle sue modalità di fallimento.
- Progettare un file di istruzioni e una skill che cambiano davvero il comportamento del modello.
- Implementare un hook che blocca un'azione non sicura in modo deterministico.
- Decidere quando un subagente vale il suo costo, e quando è solo perdita di contesto.
- Spiegare cosa standardizza MCP e dove si trova il suo confine di fiducia.
- Costruire una suite di eval che intercetta le regressioni invece di adulare il modello.
- Eseguire una sessione con l'agente su una repo reale senza romperla.

## Ritmo

- **Sprint nel weekend:** moduli 0–3, 5, 8, 12. Capirai gli agenti e
  i loro rischi, non li costruirai.
- **Due settimane:** tutto tranne il capstone.
- **Corso completo:** tutti e sedici, capstone incluso. Consigliato.

## Convenzioni usate nelle lezioni

- `💡 In pratica` — come questo concetto compare negli strumenti reali. Puoi saltarlo.
- `⚠️ Modalità di fallimento` — il modo specifico in cui questo va storto.
- `🔬 Fallo fallire` — un esercizio deliberato per farlo fallire.
- `✅ Verifica` — domande a cui rispondere prima di andare avanti.
