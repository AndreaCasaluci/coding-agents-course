# 13 — Flussi di lavoro che funzionano

> **Obiettivi**
> - Strutturare una sessione in modo che l'agente riesca e tu possa verificarlo.
> - Usare TDD e il piano-prima come meccanismi di controllo, non come riti.
> - Sapere quando fermare l'agente e prendere in mano la situazione.

## La forma della sessione

```
1. ESPLORA   leggi, cerca, capisci            (sola lettura)
2. PIANIFICA enuncia la modifica, elenca i file (nessuna modifica)
3. ESEGUI    modifiche piccole, una questione  (scritture)
4. VERIFICA  test, tipi, revisione del diff     (prove)
5. RIPORTA   cosa è cambiato, cosa non è provato (riassunto onesto)
```

La maggior parte delle sessioni fallite salta 1–2 e si precipita al 3. L'agente
modifica il file sbagliato, e ogni turno successivo aggrava l'errore.

### Esplorare e pianificare costano poco

L'esplorazione è in sola lettura, quindi non può rompere nulla. Pianificare costa
un turno e cattura il "ho capito male il compito" prima che diventi un diff da 30
file.

```
"Prima di modificare qualsiasi cosa: trova dove vengono validati i token di
 autenticazione, elenca i file coinvolti e proponi un piano. Non modificare
 ancora."
```

La clausola `non modificare ancora` è ciò che rende un piano tale. Senza, i
modelli iniziano a scrivere mentre spiegano.

💡 *In pratica* — Alcuni strumenti hanno una "modalità piano" esplicita che
blocca meccanicamente le scritture. È strettamente meglio che chiedere per
favore, perché è imposto (modulo 08).

## Il TDD è un sistema di controllo per l'agente

Il test-driven development viene di solito venduto come pratica di design. Per gli
agenti è qualcosa di più utile: **una specifica che il ciclo può controllare.**

```
1. Scrivi il test che fallisce (o fallo scrivere, poi rivedilo).
2. Eseguilo. Conferma che fallisca per il motivo giusto.
3. Implementa finché non passa.
4. Esegui tutta la suite.
5. Rifattorizza con la suite verde.
```

Perché funziona così bene con gli agenti:

- Il test è un **bersaglio fisso**. Il modello non può ridefinire il successo a
  metà esecuzione.
- L'output del fallimento è **prova**, che rientra nel ciclo.
- Il test sopravvive alla sessione e protegge le modifiche future.

La modalità di fallimento: l'agente scrive un test che asserisce la propria
implementazione. Rivedi prima il test, o scrivilo tu. Un test scritto dopo il
codice verifica che il codice faccia ciò che fa.

## Diff piccoli, una sola questione

| Dimensione del diff | Realtà della revisione |
|---|---|
| < 50 righe | leggi con attenzione |
| 50–300 | scorrri, ti fidi dei test |
| 300–1.000 | timbro |
| > 1.000 | "mi sembra ok" |

Gli agenti producono volentieri diff da 2.000 righe. Non è produttività, è debito
di revisione. Delimita il compito:

```
"Modifica solo src/auth/session.py. Non toccare test o configurazione."
```

Il perimetro è un controllo a livello di prompt; hook e permessi sono
l'imposizione (modulo 12).

## Igiene del contesto

- **Un compito per sessione.** Una sessione che scivola da "correggi il login" a
  "aggiorna anche React" ha un contesto contaminato e un diff non revisionabile.
- **Ricomincia dopo un ciclo di fallimenti.** Se l'agente ha fallito tre volte,
  la trascrizione ora contiene tre ipotesi fallite, e condizionano il tentativo
  successivo. Sessione nuova, compito scritto meglio.
- **Comprimi deliberatamente.** Riassumi ciò che hai imparato nel nuovo compito
  invece di trascinarti tutta la cronologia.
- **Tieni pulito l'albero di lavoro** prima di iniziare, così `git diff`
  significa qualcosa.

## Quando prendere il controllo

Ferma l'agente quando:

- ha fatto **lo stesso tentativo fallito due volte** (lo farà una terza),
- il diff **cresce senza che i test passino**,
- sta **modificando file fuori dal perimetro dichiarato**,
- sta **litigando con il test** invece di correggere il codice,
- non riesci a spiegare la modifica che ha appena fatto.

Prendere il controllo non è un fallimento. Il punto è il throughput, e un umano
che corregge un bug da 5 righe è spesso più veloce di un quarto tentativo
dell'agente.

## Igiene dei commit

Gli agenti rendono i commit facili e quindi tentanti da fare male.

- **Una modifica logica per commit.**
- **Il messaggio spiega il perché**, non solo il cosa (il diff mostra il cosa).
- **Mai committare segreti**; controlla `git diff --cached` prima di committare.
- **Non lasciare che l'agente committi su `main`**; crea prima un branch.
- **Rivedi prima di committare**, non dopo il push.

Una convenzione utile: l'agente prepara lo stage e propone un messaggio; l'umano
committa. Tiene l'umano nel ciclo nel punto in cui gli errori diventano
permanenti.

## La checklist di revisione

Quando rivedi il diff di un agente, chiedi in quest'ordine:

1. **Perimetro** — tocca solo ciò che è stato chiesto?
2. **Correttezza** — c'è un test, e testa la cosa giusta?
3. **Casi limite** — vuoto, null, grande, concorrente, non autorizzato.
4. **Gestione degli errori** — ingoia i fallimenti?
5. **Sicurezza** — nuovi input, nuovi percorsi, nuove chiamate di rete?
6. **Stile** — coerente con il codice circostante (meno importante).

Le prime due catturano la maggior parte dei problemi reali. Lo stile è dove i
revisori passano più tempo.

## Anti-pattern

| Anti-pattern | Sintomo | Soluzione |
|---|---|---|
| Sviluppo a sensazione | "sembra giusto", niente test | pretendi prove |
| Accumulo di prompt | compito da 200 righe | pianifica prima, dividi il compito |
| Accumulo di contesto | una sessione per un'intera giornata | sessione nuova per compito |
| Timbro | diff da 1.000 righe approvato in 2 minuti | limita la dimensione |
| L'agente committa tutto | cronologia rumorosa | committa l'umano |
| Riprova finché è verde | test instabile nascosto | correggi il test |
| "Ha detto che funziona" | nessuna verifica | eseguilo tu |

## Laboratorio

```bash
python3 labs/L13_workflows.py
```

Eseguirai lo stesso compito di correzione in due modi: un prompt unico "correggi",
e il ciclo esplora → pianifica → test → correggi → verifica. Confronterai
trascrizioni, dimensione del diff e numero di turni.

🔬 **Fallo fallire:** dai all'agente un compito che tocca tre questioni e guarda
il diff diventare non revisionabile.

## ✅ Verifica

1. Perché esplorare e pianificare sono le fasi più economiche?
2. Perché il TDD funziona meglio con gli agenti che con gli umani?
3. Qual è la modalità di fallimento dei test scritti dall'agente?
4. Quando devi fermare l'agente e prendere il controllo?
5. Perché rivedere prima di committare invece che dopo il push?

<details>
<summary>Risposte</summary>

1. Sono in sola lettura, quindi non possono rompere nulla, e catturano gli
   equivoci prima che diventino diff grandi.
2. Il test è un bersaglio fisso e il suo output di fallimento è una prova su cui
   il ciclo può agire.
3. Il test asserisce l'implementazione invece del requisito.
4. Fallimento identico ripetuto, diff che cresce con i test rossi, scope creep o
   una modifica che non sai spiegare.
5. I commit sono economici da correggere prima di esistere e costosi dopo essere
   stati condivisi.
</details>
