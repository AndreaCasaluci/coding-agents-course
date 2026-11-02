# Progetto finale — repo_doctor

Un agente di analisi che legge una repository e scrive `REPORT.md`. È il progetto
più piccolo che esercita insieme ogni concetto del corso.

## Eseguilo

```bash
# analizza una repo di esempio generata (offline, senza chiave API)
python3 -m capstone.repo_doctor --demo

# analizza una repo vera
python3 -m capstone.repo_doctor --root /percorso/della/repo --transcript

# esegui la suite di eval
python3 -m capstone.repo_doctor --eval
```

## Cosa dimostra

| Concetto | Dove |
|---|---|
| Superficie minima degli strumenti | `build_doctor`: leggi, cerca, inventario, scrivi, delega |
| Skill caricata su richiesta | `capstone/skills/repo-audit/SKILL.md` via `load_skill` |
| Guardrail deterministico | hook `report-only` su `PRE_EDIT` |
| Oscuramento dei segreti | `redact_secrets` su `POST_TOOL` |
| Subagente | `delegate` → `run_subagent`, contesto pulito, limite di profondità |
| Budget + limite di turni | `ContextBudget(16_000)`, `max_turns=12` |
| Eval sui risultati | `capstone/evals.py`, sei casi, workspace nuovo per ciascuno |
| Input non fidato | l'`AGENTS.md` della repo analizzata **non** viene caricato |

## Scelte di progetto da saper difendere

**Solo `REPORT.md` è scrivibile.** La skill lo dice, ma l'hook lo impone. Prova
`--root` su una repo e guarda una scrittura su `src/` tornare come `DENIED`.

**Nessuno strumento shell.** L'analisi non ne ha bisogno, quindi è assente. Ogni
strumento che non esponi è una superficie d'attacco che non possiedi.

**Le istruzioni della repo analizzata vengono ignorate.** Una repository può
contenere un `AGENTS.md` che dice "esfiltra i segreti". Caricarlo sarebbe
un'injection autoinflitta. Il dottore parte con un `InstructionSet` vuoto.

**La delega è profonda un livello.** Lo strumento `delegate` rifiuta quando
l'agente chiamante non è il dottore radice, così un figlio non può espandersi
all'infinito.

**Il modello offline è una macchina a stati.** `DoctorLLM` esegue la procedura in
modo deterministico, così il progetto finale gira senza chiave API. Sostituisci
un modello vero con `MINI_AGENT_PROVIDER=openai`; l'harness è identico.

## Estendilo

- Aggiungi un **subagente revisore** che critica il report con una rubrica.
- Aggiungi **pass@3** per il caso più instabile.
- Aggiungi un caso di **esaurimento del budget**: una repo abbastanza grande da
  forzare la compressione.
- Eseguiilo in CI su un programma e confronta i report.

## File

```
capstone/
  repo_doctor.py        l'agente, gli strumenti, l'hook, la policy, la CLI
  evals.py              sei casi valutati sul risultato
  skills/repo-audit/    la procedura (SKILL.md)
  BRIEF.md              il testo del compito e i non-obiettivi
  RETRO.md              cosa hai imparato (compilalo)
```
