# 15 — Progetto finale: costruisci e difendi un agente

> **Obiettivi**
> - Costruire un agente piccolo ma reale che usa ogni concetto del corso.
> - Dimostrarlo con le eval, non con la prosa.
> - Scrivere una retrospettiva che nomina cosa cambieresti.

## Il brief

Costruisci **`repo_doctor`**: un agente che analizza una repository e produce un
report sullo stato di salute, azionabile.

Deve:

1. **Usare strumenti** per ispezionare una repo (file, ricerca, test).
2. **Caricare una skill** che definisce la procedura di analisi.
3. **Imporre una regola con un hook** che un prompt non potrebbe garantire.
4. **Delegare** almeno un'indagine a un subagente.
5. **Passare una suite di eval** di almeno cinque casi, incluso uno in cui deve
   *non* agire.
6. **Girare headless**, con limiti di turni e token, producendo un file di
   report.

È deliberatamente piccolo. Il punto è la copertura dei concetti, non la scala.

## Perché questo progetto

Un'analisi della repo è:

- **prevalentemente in lettura**, quindi il raggio d'impatto è piccolo,
- **verificabile**, perché il report si può controllare contro la repo,
- **multi-passo**, quindi esercita contesto e delega,
- **reale**, nel senso che useresti davvero l'output.

## Traguardi

### M1 — Brief e vincoli (30 min)

Scrivi `capstone/BRIEF.md`:

```markdown
## Obiettivo
Analizza una repo e scrivi REPORT.md con: pattern rischiosi, test mancanti,
dipendenze obsolete e una lista delle prime 3 correzioni.

## Non-obiettivi
Nessuna modifica al codice. Nessuna rete. Nessuna installazione di dipendenze.

## Vincoli
Workspace in sola lettura. Massimo 12 turni. Report sotto le 100 righe.
```

I non-obiettivi sono la sezione più importante. Sono ciò che impedisce all'agente
di "sistemare" le cose di propria iniziativa.

### M2 — Eval prima dell'agente (1 h)

Scrivi cinque casi in `capstone/evals.py` **prima** dell'implementazione:

| Caso | Setup | Atteso |
|---|---|---|
| `finds_missing_tests` | modulo senza file di test | il report lo nomina |
| `finds_todo_cluster` | tre `TODO` in un file | il report li raggruppa |
| `respects_read_only` | una repo qualsiasi | zero file modificati |
| `no_false_alarm` | repo pulita | il report dice "nessun problema rilevante" |
| `reports_structure` | repo annidata | il report ha le sezioni richieste |

La valutazione è sul contenuto del report e sullo stato del workspace, mai sulla
trascrizione.

### M3 — Superficie degli strumenti (1 h)

Parti da `make_fs_tools`. Aggiungi solo ciò che serve all'analisi:

- `list_files`, `read_file`, `search` (già presenti),
- `run_tests` (comando in allowlist, output limitato),
- `write_report` (l'unica scrittura, su un solo percorso).

Nota cosa **non** hai aggiunto: `delete_file`, `run_shell`. L'analisi non ne ha
bisogno, quindi sono superficie d'attacco gratuita.

### M4 — Skill (45 min)

`capstone/skills/repo-audit/SKILL.md`:

```markdown
---
name: repo-audit
description: Analizza una repository per test mancanti, cluster di TODO,
  pattern rischiosi e configurazione obsoleta. Usala quando ti viene chiesto
  di rivedere la salute di una repo.
---

1. Elenca la struttura di primo livello. Identifica linguaggio e layout dei test.
2. Trova i file di test. Confrontali con i moduli sorgente. Elenca i moduli non testati.
3. Cerca TODO/FIXME/HACK. Raggruppa per file.
4. Cerca pattern rischiosi: eval, exec, shell=True, segreti hardcoded.
5. Scrivi REPORT.md con: Summary, Untested modules, TODO clusters,
   Risky patterns, Top 3 fixes.
Non modificare nessun file tranne REPORT.md.
```

L'ultima riga è una regola, non una garanzia — ed è per questo che esiste M5.

### M5 — Hook (45 min)

Imponi ciò che la skill si limita a chiedere:

```python
hooks.on(PRE_EDIT, deny_paths(("src", "tests", ".git", ".env")))
```

Solo `REPORT.md` è scrivibile. Un prompt dice "non modificare"; un hook lo rende
impossibile.

Bonus: un hook `post_tool` che oscura qualsiasi cosa corrisponda a un pattern di
segreto, e un log di audit su `pre_tool`.

### M6 — Subagente (45 min)

Delega la scansione di sicurezza:

```python
security = run_subagent(parent, "security",
    "Analizza questa repo per eval/exec/shell=True/segreti hardcoded. "
    "Riporta file:riga per ogni risultato. Non modificare nulla.")
```

Il padre riceve un riassunto, non 30k token di output di grep. Verifica le
citazioni leggendone una.

### M7 — Esegui e passa le eval (1 h)

```bash
python3 -m capstone.repo_doctor --eval
```

Itera sulla **skill e sul prompt**, non sul valutatore. Se ti accorgi di
indebolire un controllo per farlo passare, fermati: il controllo ti sta dicendo
qualcosa.

### M8 — Retrospettiva (30 min)

`capstone/RETRO.md`:

- Cosa ha sbagliato l'agente che ti ha sorpreso?
- Quale controllo l'ha catturato: test, hook, budget o revisione?
- Cosa cambieresti nel testo del compito?
- Cosa ti ha comprato il subagente, in token?
- Cosa è ancora non provato?

## Rubrica

| Criterio | Peso | Prova |
|---|---|---|
| La superficie degli strumenti è minima e giustificata | 15% | codice + non-obiettivi del BRIEF |
| La skill cambia davvero il comportamento | 15% | la trascrizione mostra `load_skill` |
| Un hook impone una regola | 20% | una modifica negata nella trascrizione |
| Il subagente è usato in modo appropriato | 15% | trascrizione del figlio + riassunto |
| Le eval sono sui risultati e passano | 20% | output di `--eval` |
| La retrospettiva è onesta e specifica | 15% | RETRO.md |

Un progetto che passa le eval ma ha una superficie di 12 strumenti con
`run_shell` vale meno di uno con quattro strumenti e un brief chiaro.

## Obiettivi extra

- Aggiungi un **subagente revisore** con contesto pulito che critica il report.
- Aggiungi un **pass@3** per il caso più instabile.
- Aggiungi un caso di **esaurimento del budget**: una repo così grande che
  l'agente deve comprimere, e il report deve restare coerente.
- Eseguilo in CI su un programma contro una repo vera e confronta i report.

## Domande di difesa

Dovresti saper rispondere senza appunti:

1. Perché `run_shell` è assente, e cosa ti servirebbe prima di includerlo?
2. Quale eval catturerebbe una regressione in cui l'agente inizia a modificare
   `src/`?
3. Quanto costa il subagente, e cosa hai risparmiato?
4. Da dove potrebbe entrare una prompt injection in questo sistema, e cosa limita
   il danno?
5. Se il report è sbagliato, come lo scopriresti?

Se non sai rispondere a 4 e 5, rileggi i moduli 11 e 12.
