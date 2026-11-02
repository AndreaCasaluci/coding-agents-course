# 14 — Team, CI, misurazione

> **Obiettivi**
> - Eseguire agenti in modalità headless in CI senza dare loro le chiavi della
>   produzione.
> - Calibrare la fiducia invece di presumerla.
> - Scegliere metriche che sopravvivono a una revisione del CFO.

## Due modalità d'uso

| Modalità | Umano presente | Uso tipico |
|---|---|---|
| **Interattiva** | sì | esplorazione, refactoring, debug |
| **Headless** | no | controlli CI, triage delle issue, manutenzione programmata |

L'headless è dove sta l'ingegneria interessante, perché nessuno è lì per dire
"aspetta, non farlo". Ogni guardrail del modulo 12 deve essere meccanico.

## Agenti headless in CI

```
pull_request
   │
   ├─ lint / typecheck / test          (deterministico, veloce)
   ├─ agente: rivedi il diff           (sola lettura, commenta)
   ├─ agente: correggi i lint          (scrittura, su un branch, no push su main)
   └─ revisione umana                  (autorità finale)
```

Regole che tengono la cosa sana:

1. **Sola lettura per default.** Un agente revisore non riceve un token di
   scrittura.
2. **Le scritture vanno su un branch**, mai sul branch base.
3. **Nessun segreto nell'ambiente** a meno che il compito non ne abbia davvero
   bisogno, e allora delimitato e a breve scadenza.
4. **Fissa modello e versione del prompt.** Altrimenti la build verde di ieri non
   significa nulla.
5. **Limiti di budget.** Un tetto di token/dollari per esecuzione, imposto
   dall'harness.
6. **Timeout.** Per turno e per job.
7. **Fallback deterministico.** Se l'agente fallisce, la pipeline deve comunque
   produrre un risultato utile (es. "revisione non disponibile").

### Cosa automatizzare prima

In ordine di valore:

1. **Commenti di revisione sui diff** — sola lettura, rischio basso, valore
   immediato.
2. **Triage delle issue / etichette** — rischio basso, volume alto.
3. **Correzione di errori di lint e tipi** — stretto, verificabile.
4. **Aggiornamento delle dipendenze** — meccanico, protetto dai test.
5. **Sviluppo di funzionalità** — per ultimo, e solo con un umano nel ciclo.

Non iniziare dal 5.

## Calibrare la fiducia

La fiducia non è binaria. È una proprietà per compito:

```
rischio = raggio d'impatto × reversibilità × verificabilità
```

| Compito | Raggio | Reversibile | Verificabile | Fiducia |
|---|---|---|---|---|
| Rinominare una variabile | piccolo | sì | sì | alta |
| Aggiungere un test | piccolo | sì | sì | alta |
| Correggere un bug | medio | sì | sì | media |
| Rifattorizzare un modulo | medio | sì | media | media |
| Cambiare uno schema DB | grande | no | difficile | bassa |
| Toccare auth / pagamenti | grande | no | difficile | molto bassa |
| Fare deploy | enorme | no | no | nessuna |

L'errore che fanno i team è applicare un unico livello di fiducia a tutto.

## Metriche

Misura i risultati, non l'attività:

| Metrica | Definizione | Perché conta |
|---|---|---|
| **Tasso di accettazione** | % di diff dell'agente integrati senza modifiche | segnale vs rumore |
| **Tasso di revert** | % ripristinati entro 30 giorni | correttezza reale |
| **Tasso di modifiche umane** | righe cambiate da umani dopo l'agente | divario di qualità |
| **Tempo di ciclo** | issue → PR integrata | l'obiettivo vero |
| **Costo per PR integrata** | token + infrastruttura / PR integrate | economia unitaria |
| **Difetti sfuggiti** | bug riconducibili a modifiche dell'agente | rischio |

Evita:

- righe di codice generate (premia la verbosità),
- numero di sessioni dell'agente (premia l'uso),
- "tempo risparmiato" autodichiarato senza una baseline.

### Un esperimento di baseline economico

Prima del rollout, misura una settimana senza agenti: tempo di ciclo delle PR,
commenti di revisione per PR, tasso di revert. Poi misura di nuovo. Senza una
baseline, ogni numero è una storia.

## Il carico di revisione

Il costo nascosto non sono i token; è l'**attenzione della revisione**.

Un diff di 400 righe prodotto da un agente richiede ~30–60 minuti per una
revisione decente. Se l'agente ne produce cinque al giorno, hai creato un lavoro
a tempo pieno di revisione. Ecco perché **diff piccoli e perimetro stretto non
sono preferenze di stile — sono l'economia dell'intera pratica.**

Mitigazioni:

- limita la dimensione del diff nelle istruzioni e imponilo con un hook,
- pretendi i test nella stessa PR,
- instrada le modifiche banali su un percorso di revisione più veloce,
- fai spiegare all'agente il *perché*, così il revisore può scorrere il *cosa*.

## Politica: cosa possono toccare gli agenti

Scrivila, perché "usa il buon senso" produce rischi incoerenti:

```markdown
## Politica per gli agenti

Consentito senza revisione: documentazione, test, correzioni di lint, patch
delle dipendenze.
Consentito con revisione:    codice applicativo, configurazione CI.
Approvazione richiesta:      migrazioni, auth, pagamenti, infrastruttura, segreti.
Mai:                         force-push, deploy, rotazione credenziali, cancellazione dati.
```

Metti la politica in `AGENTS.md` *e* imponi le parti importanti con hook e
permessi. I documenti di politica derivano; gli hook no.

## Inserire un team

1. **`AGENTS.md` condiviso** — comandi, invarianti, trappole. Un file,
   versionato.
2. **Skill condivise** — le procedure che il team ripete (note di rilascio,
   migrazioni, runbook degli incidenti).
3. **Hook condivisi** — proteggi i segreti, formatta alla modifica, logga le
   chiamate.
4. **Una suite di eval iniziale** — cinque casi che codificano "com'è il buon
   lavoro".
5. **Una checklist di revisione** — così gli umani rivedono le stesse cose ogni
   volta.
6. **Una dashboard dei costi** — così la spesa è visibile prima che qualcuno la
   chieda.

L'ordine conta: prima il contesto, poi la capacità, poi i guardrail, poi la
misurazione.

## Governance, in breve

Domande che emergono quando gli agenti toccano sistemi reali:

- **Chi è responsabile del commit di un agente?** L'umano che l'ha integrato.
- **I commit degli agenti sono etichettati?** Dovrebbero esserlo, per
  l'auditabilità.
- **La trascrizione viene conservata?** Se sì, dove e per quanto? Può contenere
  codice e segreti.
- **Un provider può addestrare sui dati?** Controlla il contratto, non il
  marketing.
- **Qual è il piano di rollback?** Lo stesso degli umani: revert, feature flag,
  redeploy.

## Laboratorio

```bash
python3 labs/L14_ci.py
```

Eseguirai l'harness in un job CI simulato: modalità revisione in sola lettura, un
budget di token, un limite di turni e un report leggibile dalla macchina. Poi
passerai alla modalità scrittura e vedrai il livello dei permessi rifiutare il
push su `main`.

🔬 **Fallo fallire:** togli il limite di budget ed esegui una policy che entra in
ciclo; guarda il job colpire il timeout invece di fallire in modo pulito.

## ✅ Verifica

1. Quali sono le due modalità d'uso, e quale richiede guardrail più forti?
2. Perché un revisore in CI deve essere in sola lettura?
3. Cosa rende rischioso un compito, nella formula della fiducia?
4. Perché "righe di codice" è una metrica scadente?
5. Perché il carico di revisione è il vero costo dell'adozione?

<details>
<summary>Risposte</summary>

1. Interattiva e headless; l'headless richiede guardrail meccanici perché nessun
   umano sta guardando.
2. Non può correggere accidentalmente cose, e una revisione compromessa non può
   modificare il codice che revisiona.
3. Raggio d'impatto grande, irreversibile, difficile da verificare.
4. Premia la verbosità e misura l'attività, non i risultati.
5. Ogni diff dell'agente consuma attenzione umana di revisione, la risorsa più
   scarsa del ciclo.
</details>
