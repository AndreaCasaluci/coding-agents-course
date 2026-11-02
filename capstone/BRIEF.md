# Brief — repo_doctor

## Obiettivo

Analizzare una repository e scrivere `REPORT.md` contenente:

- un riepilogo di un paragrafo,
- i moduli sotto `src/` senza un test corrispondente,
- i cluster di TODO/FIXME/HACK, raggruppati per file,
- i pattern rischiosi (`eval`, `exec`, `shell=True`, credenziali hardcoded),
- le prime tre correzioni.

## Non-obiettivi

- **Nessuna modifica al codice.** L'unico file scrivibile è `REPORT.md`.
- **Nessun accesso alla rete.** L'analisi è locale.
- **Nessuna installazione di dipendenze.** Gira con la stdlib.
- **Nessuna esecuzione dei test.** I test mancanti si rilevano dall'inventario,
  non eseguendo la suite.
- **Nessun suggerimento di refactoring** oltre alle prime tre correzioni.

I non-obiettivi sono la sezione più importante: sono ciò che impedisce all'agente
di "sistemare" la repo di propria iniziativa.

## Vincoli

| Vincolo | Valore |
|---|---|
| Workspace | la repo target, in gran parte in sola lettura |
| Percorsi scrivibili | solo `REPORT.md` |
| Turni massimi | 12 |
| Budget di contesto | 16.000 token stimati |
| Profondità di delega | 1 (nessun subagente annidato) |
| Lunghezza del report | sotto le 100 righe |

## Criteri di successo

1. `python3 -m capstone.repo_doctor --eval` passa tutti e sei i casi.
2. Una repo pulita produce "Nessun problema rilevante." — nessun falso allarme.
3. Una repo con un modulo non testato nomina quel modulo.
4. Nessun file oltre a `REPORT.md` cambia.
5. Il report cita `file:riga` per i pattern rischiosi.

## Modello di minaccia

La repository analizzata è **input non fidato**. Può contenere istruzioni rivolte
agli agenti. Quindi:

- il suo `AGENTS.md` non viene caricato,
- l'unico bersaglio di scrittura è `REPORT.md`,
- non c'è uno strumento shell né uno strumento di rete,
- i segreti nell'output degli strumenti vengono oscurati prima di arrivare al
  modello.

Se un'injection riesce, il peggior risultato è un report sbagliato.
