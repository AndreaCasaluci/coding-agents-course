# 06 — Istruzioni e file di regole

> **Obiettivi**
> - Scrivere un `AGENTS.md` che cambia davvero il comportamento.
> - Ragionare sulla precedenza quando le istruzioni sono in conflitto.
> - Evitare i tre anti-pattern che rendono inutile un file di istruzioni.

## Il problema

Ogni sessione parte da freddo. Senza un file di istruzioni persistente, riscrivi
lo stesso contesto: come eseguire i test, quali directory sono congelate, cosa non
toccare. Sono token sprecati e comportamento incoerente.

La convenzione emersa è `AGENTS.md`: Markdown semplice nella radice della repo,
letto automaticamente, versionato con il codice.

## Cosa ci deve davvero stare

Tre categorie, e nient'altro:

### 1. Comandi non intuibili

```markdown
## Comandi
- Test: `make test`          (avvia un container Postgres)
- Singolo test: `pytest tests/test_x.py::test_y`
- Lint: `ruff check . && mypy src`
- Genera i proto: `make proto`  (non modificare a mano i *_pb2.py)
```

Il modello può indovinare `pytest`. Non può indovinare che la suite richiede un
database, né che i file generati non vanno modificati.

### 2. Invarianti non ovvi

```markdown
## Invarianti
- Mai fare commit su `main`; crea prima un branch.
- Le modifiche all'API pubblica richiedono una voce in `CHANGELOG.md`.
- Il denaro è in centesimi interi. Mai usare float per la valuta.
- Ogni accesso al DB passa da `db/repo.py`.
```

Sono le regole che, se violate, costano un ciclo di revisione o un incidente in
produzione.

### 3. Trappole che costano tempo reale

```markdown
## Trappole
- `legacy/` è congelata. Non fare refactoring, anche se sembra sbagliata.
- La suite di test dipende dall'ordine; eseguila intera, non file per file.
- `config/defaults.yaml` è generato da `config/schema.py`.
```

## Cosa non ci deve stare

| Anti-pattern | Perché fallisce |
|---|---|
| Un saggio sullo stile ("scrivi codice pulito") | Troppo vago per cambiare una decisione |
| Duplicare il README | Obsoleto appena cambia; due fonti di verità |
| Un documento di architettura da 500 righe | Mangia il budget; le regole sepolte vengono ignorate |
| Ogni regola che ti viene in mente | Diluizione: la regola importante è ora 1 su 80 |
| Regole aspirazionali che nessuno segue | Insegna al modello che le regole sono facoltative |

Un buon `AGENTS.md` ha **30–80 righe**. Se è più lungo, la maggior parte
appartiene a documentazione che l'agente può leggere su richiesta, o a una skill.

## Precedenza

I sistemi reali hanno livelli:

```
istruzioni utente         (~/.config/agent/AGENTS.md)   personali, non committate
        ▲ sovrascritte da
AGENTS.md nella radice                                  a livello di progetto
        ▲ sovrascritte da
AGENTS.md in sottodirectory                             limitate a un sottoalbero
        ▲ sovrascritte da
il compito / messaggio utente attuale                   solo questa sessione
```

Due regole:

1. **Vince il più vicino.** Un `backend/AGENTS.md` sovrascrive la radice per il
   lavoro sotto `backend/`.
2. **Il specifico batte il generale.** "Qui usa i tab" batte "usa gli spazi" se è
   più locale.

L'ambiguità è il nemico. Se due file sono in disaccordo e nessuno è chiaramente
più locale, il modello ne sceglierà uno a caso e tu non saprai quale.

## Le istruzioni negative sono deboli

```
Non usare print.                     ← il modello potrebbe comunque aggiungerlo
Usa il logger in `obs/log.py`.       ← azionabile
```

Un divieto dice al modello cosa non fare, ma non cosa fare al suo posto. Abbina
ogni "non" a un "fai", altrimenti riempirà il vuoto con un'ipotesi.

Debole: "Non rompere la build."
Forte: "Prima di finire, esegui `make check` e incolla il risultato."

## Rendile verificabili

Un'istruzione che non puoi verificare è un desiderio. Preferisci regole la cui
violazione è visibile:

- "Esegui `make test` prima di dichiarare finito" → controlla la trascrizione.
- "Non modificare mai `legacy/`" → un hook può imporlo (modulo 08).
- "Usa centesimi interi" → una regola di lint o un test può imporlo.

La progressione è: **istruzione → hook → test → sistema di tipi**. Sposta una
regola più in basso in questa scala appena conta davvero.

## Delimitare per directory

Le repo grandi traggono beneficio da istruzioni per directory:

```
AGENTS.md                      # a livello di repo: comandi, invarianti
backend/AGENTS.md              # convenzioni Django, politica migrazioni
frontend/AGENTS.md             # pattern dei componenti, regole di stato
infra/AGENTS.md                # mai applicare terraform senza un plan
```

`discover()` in `mini_agent/instructions.py` risale dalla radice del workspace
fino alla directory di lavoro, così il modello legge generale → specifico.

💡 *In pratica* — Gli strumenti differiscono per nome del file e regole di
scoperta (alcuni leggono `AGENTS.md`, altri hanno i propri file, altri entrambi).
Il concetto è identico: un file Markdown versionato, stratificato per directory,
caricato nel system prompt.

## Laboratorio

```bash
python3 labs/L06_instructions.py
```

Costruirai una piccola repo con file di istruzioni nella radice e in una
sottodirectory, li vedrai renderizzati in ordine di precedenza e vedrai
un'istruzione vaga non cambiare il comportamento di un modello preimpostato,
mentre una specifica riesce.

🔬 **Fallo fallire:** scrivi due istruzioni in conflitto allo stesso livello e
guarda quale segue il modello. Poi risolvi rendendone una più specifica.

## ✅ Verifica

1. Quali tre categorie appartengono a `AGENTS.md`?
2. Perché "scrivi codice pulito" è un'istruzione inutile?
3. Qual è la regola di precedenza tra file radice e sottodirectory?
4. Perché le istruzioni negative sono deboli, e qual è la soluzione?
5. Qual è la scala dall'istruzione all'imposizione?

<details>
<summary>Risposte</summary>

1. Comandi non intuibili, invarianti non ovvi, trappole che costano tempo.
2. Non cambia nessuna decisione concreta; non può essere violata in modo visibile.
3. Vince il file più vicino per il lavoro nel suo sottoalbero.
4. Dicono cosa non fare, non cosa fare; abbinale a un'alternativa positiva.
5. Istruzione → hook → test → sistema di tipi.
</details>
