# 05 — Ingegneria del contesto

> **Obiettivi**
> - Rendicontare ogni token di una chiamata.
> - Scegliere tra stuffing, retrieval e compressione.
> - Spiegare perché più contesto spesso rende gli agenti peggiori.

## Il budget, concretamente

```
utilizzabile = finestra - riserva_per_la_risposta
```

Con un budget di 32k e una riserva di 4k, hai 28k da spendere. Un turno tipico:

| Voce | Token |
|---|---|
| system prompt | 800 |
| AGENTS.md | 1.200 |
| 6 schemi di strumenti | 900 |
| trascrizione finora | 12.000 |
| ultimo risultato di uno strumento | 8.000 |
| **totale** | **22.900** |
| rimanenti | 5.100 |

Il numero da tenere d'occhio è l'ultimo. Quando si avvicina a zero, il prossimo
risultato viene troncato o il turno viene tagliato — e il modello inizia a
"dimenticare" cose. Non c'è niente di sbagliato nel modello: è finito il budget.

## Tre strategie

### 1. Stuffing (riempire)

Metti nel prompt tutto ciò che è rilevante. Funziona quando il corpus è piccolo e
stabile (un singolo file, una specifica breve). Fallisce alla scala di una repo, e
peggiora la qualità prima ancora di fallire del tutto.

### 2. Retrieval (recupero)

Recupera solo ciò che serve al compito, su richiesta. È ciò che ti danno gli
strumenti: `search` poi `read_file(start, end)` invece di `read_file(tutto)`.

La qualità del recupero domina la qualità dell'agente. Un agente che fa bene
grep batte un modello più intelligente che legge il file sbagliato.

### 3. Compressione

Quando la cronologia supera il budget, sostituisci i turni vecchi con un
riassunto.

```
[system]
[riassunto dei turni 1–14: esplorato il modulo dates, trovato parse_date a
 src/dates.py:41, aggiunto un controllo, test_empty_string ancora rosso]
[turno 15 …]
```

La compressione è **lossy per definizione**. Cosa sopravvive dipende da cosa ha
tenuto il riassuntore. Vittime tipiche: il contenuto esatto dei file, il motivo
per cui un'ipotesi è stata scartata, le parole originali dell'utente.

L'harness qui marca esplicitamente le parti compresse, così il modello sa di
lavorare su un riassunto:

```python
Message("user", "[compacted earlier conversation — summary, not verbatim]\n...")
```

Senza quel marcatore, il modello tratta il riassunto come verità e smette di
rileggere il file.

## Cosa deve stare nella finestra

Ordine di priorità, dal più alto:

1. **Il compito attuale**, verbatim.
2. **Le regole che non devono essere violate** (system prompt, istruzioni).
3. **Il codice da modificare**, il più ristretto possibile.
4. **Le prove**: output dei test, messaggi di errore, risultati di ricerca.
5. **La conversazione recente**, gli ultimi turni.
6. **Il contesto di sfondo**: note di architettura, convenzioni.

E cosa non deve starci:

- elenchi completi di directory quando basta un glob,
- interi lockfile, bundle minificati, blob base64,
- log di esecuzioni riuscite,
- istruzioni duplicate in tre posti,
- il lungo ragionamento del modello di dieci turni fa.

## Degrado del contesto

I modelli non prestano attenzione in modo uniforme su una finestra lunga. In
pratica:

- il materiale all'inizio e alla fine viene richiamato meglio di quello al
  centro,
- il contenuto irrilevante degrada misurabilmente il ragionamento,
- contesti molto lunghi aumentano latenza e costo in modo superlineare.

Quindi la regola controintuitiva: **un contesto più piccolo e ben scelto produce
di solito un output migliore di uno più grande e completo.** Se la qualità cala
dopo che hai aggiunto documentazione, togli la documentazione.

## Caching del prompt

I provider possono cachare un prefisso stabile (system prompt + strumenti +
cronologia iniziale) e farlo pagare meno. Due implicazioni di progetto:

- **Tieni stabile il prefisso.** Cambiare il system prompt o l'ordine degli
  strumenti a ogni turno invalida la cache.
- **Accoda, non riscrivere.** Una cronologia che solo cresce è compatibile con
  la cache; un riordino aggressivo no.

È una leva sul costo, non sulla qualità, ma cambia molto l'economia delle
sessioni lunghe.

## L'ingegneria del contesto è il lavoro

La maggior parte del lavoro "rendi l'agente più intelligente" è in realtà:

| Sintomo | Vera soluzione |
|---|---|
| Legge i file sbagliati | Strumento di ricerca migliore, descrizioni migliori |
| Dimentica i vincoli | Spostali nel system prompt / AGENTS.md |
| Ripete tentativi falliti | Tieni i fallimenti nel contesto; non tagliarli per primi |
| Si confonde in una repo grande | Delimita il workspace; aggiungi un AGENTS.md nella sottodirectory |
| Lento e costoso | Sessioni nuove; compressione; risultati più piccoli |

Nota che nessuna di queste è "usa un modello più grande".

## La scorciatoia del subagente

La tecnica di contesto più efficace spesso è *non inviare affatto il contesto*.
Avvia un subagente con una finestra pulita, lascialo bruciare 40k token di
esplorazione e riporta indietro un riassunto da 300 token. Scambi fedeltà per
budget. Il modulo 09 spiega quando conviene.

## Laboratorio

```bash
python3 labs/L05_context.py
```

Costruirai una trascrizione che va in overflow, la vedrai troncata al confine di
un turno, poi vedrai la compressione sostituire la parte eliminata con un
riassunto — e esattamente quali informazioni spariscono.

🔬 **Fallo fallire:** imposta `reserve=0` e guarda la risposta del modello venire
compressa fino a sparire.

## ✅ Verifica

1. Perché il costo cresce in modo superlineare con i turni?
2. Quando lo stuffing è meglio del retrieval?
3. Cosa si perde tipicamente nella compressione?
4. Perché marcare un riassunto come riassunto?
5. Perché aggiungere documentazione può peggiorare un agente?

<details>
<summary>Risposte</summary>

1. Ogni turno reinvia una trascrizione che è cresciuta.
2. Con corpus piccoli e stabili — un file, una specifica breve.
3. Contenuti esatti, ipotesi scartate, parole originali.
4. Altrimenti il modello lo tratta come verità verbatim e smette di rileggere.
5. Degrado del contesto: il materiale irrilevante diluisce l'attenzione e
   aumenta il costo.
</details>
