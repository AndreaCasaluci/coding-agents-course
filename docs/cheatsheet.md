# Cheat sheet

Una pagina. Stampala.

## Il ciclo

```
budget → model(transcript, tools) → messaggio assistant
      → nessuna chiamata a strumenti? FINE
      → per ogni chiamata: pre-hook → dispatch → post-hook → messaggio tool
      → ripeti
```

Invarianti: gli id delle chiamate agli strumenti sono accoppiati, i risultati seguono in ordine,
un'esecuzione è conclusa solo quando una risposta non contiene chiamate agli strumenti.

## I cinque componenti

| Componente | Possiede | Fallimento |
|---|---|---|
| Modello | il prossimo token | allucinazione, obsolescenza |
| Harness | ciclo, contesto, limiti | trimming sbagliato, fuga incontrollata |
| Strumenti | azioni | schema errato, raggio d'impatto |
| Ambiente | repo, runtime, segreti | dipendenze mancanti, fughe |
| Umano | task, approvazione, revisione | task vago, timbro automatico |

## Budget del contesto

```
usable = window − reserve_for_reply
```

Spendilo in questo ordine: task → regole → codice mirato → evidenze → turni recenti →
contesto di sfondo. Tutto il resto è retrieval o una skill.

- Il costo cresce circa in modo quadratico con i turni (ogni turno rimanda la trascrizione).
- La compaction introduce perdita; segna i riassunti come riassunti.
- Un contesto più piccolo e pertinente batte un contesto più grande e completo.

## Progettazione degli strumenti

- Parametri piatti, pochi, enum invece di stringhe.
- Le descrizioni sono testo di prompt: di' *cosa* e *quando*.
- Gli errori sono messaggi, mai eccezioni.
- Tronca con un marcatore; pagina le letture.
- Dichiara gli effetti collaterali; tieni la superficie sotto ~20.

## Istruzioni / skill / strumenti

| | Caricato | Contiene | Esempio |
|---|---|---|---|
| `AGENTS.md` | sempre | vincoli | "esegui `make test`" |
| Skill | su richiesta | procedura | "come scrivere una migrazione" |
| Strumento | schema sempre | azione | `read_file` |

Formula della descrizione per le skill: **output + quando usarla + frasi dell'utente.**

## Hook

| Evento | Può |
|---|---|
| `pre_tool` | bloccare, riscrivere gli argomenti |
| `post_tool` | oscurare, troncare |
| `pre_edit` | bloccare un percorso |
| `post_edit` | formattare, typecheck |
| `session_start/end` | setup, metriche |

- Un prompt è un suggerimento; un hook è una regola.
- Fallisci in modo chiuso per le protezioni.
- Restituisci `None` per astenerti, non `True`.
- Livelli: istruzione < hook < permesso < sandbox.

## Subagenti

- Scambio: fedeltà + denaro → margine di contesto + parallelismo.
- L'enunciato del task deve essere autosufficiente.
- Restituisci riassunti strutturati e con citazioni, non prosa.
- Fai fan-out per la lettura; serializza per la scrittura.
- Pattern del revisore: contesto fresco, sola lettura, cita `file:line`.

## MCP

- JSON-RPC 2.0 su stdio o HTTP.
- `initialize` → `tools/list` → `tools/call`.
- Strumenti (modello), risorse (app), prompt (utente).
- Un server è un programma che stai consegnando al tuo agente.
- Le notifiche non hanno `id` e non hanno risposta.

## Scala di verifica

```
compile → lint → types → unit → integration → revisione manuale
```

Il "fatto" di un modello è testo. Il risultato di un test è evidenza.

## Eval

- Task + ambiente fresco + valutatore dell'esito.
- Valuta il workspace, non la trascrizione.
- Includi un caso di rifiuto e un caso no-op.
- Riporta pass@k; un'unica esecuzione è rumore.
- Ogni incidente diventa un caso permanente.

## Sicurezza

- Minacce: errore, injection, supply chain, esfiltrazione.
- L'injection non si risolve con un prompt; istruzioni e dati condividono un canale.
- Rendi il successo poco interessante: niente segreti, niente rete, niente shell.
- Nega per default gli effetti collaterali; approvazione per push, delete, install, deploy.
- Path jail = correttezza. Container = sicurezza.

## Flusso di lavoro

```
esplora → pianifica → esegui → verifica → riporta
```

- Pianifica prima di modificare; leggi prima di scrivere.
- TDD: il test è un bersaglio fisso e il suo fallimento è evidenza.
- Una sola preoccupazione per sessione; sessione nuova dopo tre fallimenti.
- Limita la dimensione del diff; rivedi prima del commit; il commit lo fa l'umano.
- Fermati quando: stesso fallimento due volte, il diff cresce mentre è rosso, scope creep, o non
  sai spiegare la modifica.

## Metriche

Tasso di accettazione, tasso di revert, tasso di modifiche umane, cycle time, costo per PR mergiata,
difetti sfuggiti. Non righe generate.

## Quando qualcosa va storto

1. Ferma la sessione.
2. Conserva la trascrizione.
3. Leggi il diff, non il riassunto.
4. Torna a uno stato noto.
5. Scrivi un'eval che lo riproduce.
6. Aggiungi un controllo al livello più basso che lo avrebbe prevenuto.
