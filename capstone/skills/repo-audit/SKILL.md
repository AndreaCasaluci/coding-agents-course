---
name: repo-audit
description: Analizza una repository per test mancanti, cluster di TODO e pattern rischiosi, poi scrive REPORT.md. Usala quando ti viene chiesto di rivedere la salute di una repo, analizzare un codebase o trovare debito tecnico.
---

# Analisi della repository

## Procedura

1. Carica l'inventario dei file: sorgenti sotto `src/`, test sotto `tests/`.
2. Trova i marcatori TODO/FIXME/HACK con `search`. Raggruppali per file.
3. Cerca i pattern rischiosi: `eval(`, `exec(`, `shell=True`, credenziali
   hardcoded.
4. Delega la scansione di sicurezza a un subagente. Chiedi citazioni `file:riga`
   e digli di non modificare nulla.
5. Scrivi `REPORT.md` con esattamente queste sezioni:

   ```
   # Analisi della repo

   ## Riepilogo
   ## Moduli senza test
   ## Cluster di TODO
   ## Pattern rischiosi
   ## Prime 3 correzioni
   ```

6. Se non c'è nulla da segnalare, scrivi "Nessun problema rilevante." in
   Riepilogo e "Nessuno." in ogni sezione elenco.

## Regole

- Scrivi solo `REPORT.md`. Non modificare mai sorgenti, test o configurazione.
- Cita `file:riga` per ogni risultato. Un risultato senza posizione è una voce.
- Tieni il report sotto le 100 righe.
- Non inventare file. Se l'inventario non lo elenca, non esiste.
