# AGENTS.md

Istruzioni per gli agenti di coding che lavorano in questa repository.

## Comandi

- Test: `python3 run.py test`
- Tutti i laboratori: `python3 run.py labs`
- Lint (controllo di compilazione): `python3 run.py lint`
- Esegui l'agente: `python3 -m mini_agent "<task>" --root .`

Nessuna dipendenza di terze parti. Python 3.10+.

## Invarianti

- `mini_agent/` è codice didattico: preferisci la chiarezza all'astuzia e tieni i
  moduli abbastanza piccoli da leggerli in una sola seduta.
- Ogni laboratorio (`labs/L*.py`) deve funzionare da solo e uscire con 0.
- Ogni modulo in `lessons/` corrisponde a un laboratorio e a un modulo di `mini_agent`.
- Non aggiungere dipendenze. Il vincolo di sola stdlib fa parte del design.
- I test stanno in `tests/` e usano `unittest`, non pytest.

## Trappole

- `make` non è installato in ogni ambiente. Usa `python3 run.py ...` in
  documentazione e CI.
- I laboratori scrivono nella directory temporanea del sistema operativo, mai nella repo.
- `.gitignore` esclude `sandbox/` e `.mini_agent/`; non committarli.

## Stile

- Ortografia britannica in prosa ("summarise", "behaviour"), coerente con le
  lezioni.
- Diagrammi ASCII, niente box drawing Unicode.
- I commenti del codice spiegano il *perché*, non il *cosa*.
