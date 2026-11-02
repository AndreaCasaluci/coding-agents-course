> 🇬🇧 [English (main)](https://github.com/AndreaCasaluci/coding-agents-course/blob/main/README.md) · 🇮🇹 **Italiano**

# Agenti di coding AI — Un corso intensivo da zero

Un corso pratico e indipendente dai vendor su come funzionano davvero gli agenti di coding AI:
il ciclo, il contesto, gli strumenti, i guardrail e i flussi di lavoro che li rendono
utili invece che pericolosi.

Non serve esperienza pregressa con gli agenti. Un po' di familiarità con Python e Git aiuta.

## Perché esiste

La maggior parte del materiale sugli agenti di coding è o marketing o un manuale per uno
specifico prodotto. Questo corso insegna la *meccanica* — le parti che ogni agente
condivide — così che qualunque strumento tu prenda in mano dopo (Claude Code, Codex, Cursor,
Copilot, Aider, OpenCode, qualcosa che uscirà l'anno prossimo) sia una variante di un
modello che già capisci.

L'idea centrale: **non puoi fare debug di ciò che non sai nominare.** Alla fine saprai
nominare ogni parte in movimento di un'esecuzione dell'agente e indicare quella che
si è rotta.

## Come funziona il corso

```
lessons/       16 moduli, da leggere in ordine
mini_agent/    un harness per agenti giocattolo che costruisci, un modulo alla volta
labs/          uno script eseguibile per modulo
capstone/      un progetto reale che usa tutto
docs/          cheat sheet e lista di letture
tests/         58 test unitari sull'harness
```

Ogni modulo ha la stessa forma:

1. **Obiettivi** — cosa dovresti essere in grado di fare dopo.
2. **Lezione** — il concetto, con diagrammi e le modalità di fallimento.
3. **Laboratorio** — codice eseguibile che dimostra il concetto, non un esempio
   giocattolo che stampa solo "hello".
4. **Verifica** — domande a cui dovresti saper rispondere a memoria.

Il pacchetto `mini_agent/` cresce lungo il corso. Al modulo 15 è un agente piccolo
ma completo: astrazione LLM, registro degli strumenti, filesystem in sandbox,
budget del contesto, caricamento delle istruzioni, skill, hook, subagenti, un
protocollo a forma di MCP e un runner di eval. Non è software di produzione — è
un'implementazione di riferimento *leggibile* di ogni concetto delle lezioni.

## Avvio rapido

```bash
git clone https://github.com/AndreaCasaluci/coding-agents-course.git && cd coding-agents-course

# Nessuna dipendenza. Python 3.10+.
python3 -m mini_agent --help
python3 -m mini_agent "list the files and summarise the repo"

# Esegui ogni laboratorio e test
python3 run.py test
python3 run.py labs
```

`run.py` è un piccolo runner stdlib così non ti serve `make`. Se ce l'hai,
`make test` / `make labs` fanno la stessa cosa.

L'harness include un **modello mock scriptato** così tutto funziona offline
senza chiavi API. Imposta `MINI_AGENT_PROVIDER=openai` e `OPENAI_API_KEY` per
eseguire lo stesso codice contro un modello reale.

## Inizia da qui

1. Leggi [`CURRICULUM.md`](CURRICULUM.md) — la mappa.
2. Apri [`lessons/00-orientation.md`](lessons/00-orientation.md).
3. Spunta le caselle in [`PROGRESS.md`](PROGRESS.md) man mano che procedi.
4. Tieni aperto [`docs/cheatsheet.md`](docs/cheatsheet.md) mentre lavori.

## Regole di base

- **Leggi il codice in `mini_agent/`.** Le lezioni lo spiegano, ma il punto è
  che è abbastanza piccolo da stare tutto in testa.
- **Rompi le cose di proposito.** La maggior parte dei laboratori ha un passo
  "ora fallo fallire". Le modalità di fallimento sono il curriculum.
- **Indipendente dai vendor per design.** I nomi dei prodotti compaiono solo nei box
  "In pratica", e solo per mappare un concetto su strumenti che potresti già usare.

## Stato

Il contenuto del corso è in sviluppo attivo. Vedi `PROGRESS.md`.

## Licenza

MIT — vedi [`LICENSE`](LICENSE).
