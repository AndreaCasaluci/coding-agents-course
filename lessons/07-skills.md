# 07 — Skill

> **Obiettivi**
> - Spiegare la divulgazione progressiva e perché è l'idea centrale.
> - Scrivere un `SKILL.md` la cui descrizione fa davvero scattare il caricamento.
> - Scegliere tra skill, strumento e istruzione.

## L'esplosione delle capacità

Un agente che sa fare 50 cose non può tenere 50 procedure nel contesto.
Quaranta skill da ~800 token ciascuna sono 32k token di istruzioni — l'intero
budget speso su capacità che il compito non richiede. La qualità cala, il costo
sale.

La soluzione non è un riassunto migliore. È **non caricare ciò che non serve**.

## Divulgazione progressiva

```
L1  catalogo: nome + descrizione in una riga    ~50 token/skill, sempre caricato
     │
     ├─ il compito corrisponde alla descrizione?
     ▼
L2  corpo dello SKILL.md: la procedura          ~500–2.000 token, caricato su richiesta
     │
     ├─ la procedura richiede un template o uno script?
     ▼
L3  risorse: file, script, esempi               illimitato, letto/eseguito su richiesta
```

Dieci skill costano ~500 token a L1. Solo quella che usi costa il suo corpo
intero. È una riduzione di 60× del costo fisso e — cosa più importante — mantiene
il contesto concentrato.

È esattamente come lavori già: sai quali runbook esistono, ne apri uno quando
l'incidente corrisponde.

## Anatomia di una skill

```
skills/
  release-notes/
    SKILL.md          ← obbligatorio
    template.md       ← risorsa opzionale
    collect.py        ← script opzionale
```

```markdown
---
name: release-notes
description: Scrive le note di rilascio dalla cronologia git. Usala quando ti
  viene chiesto di preparare una release, un changelog o "cosa è cambiato da vX".
---

# Note di rilascio

1. Determina l'intervallo: `git log --oneline <ultimo-tag>..HEAD`.
2. Raggruppa i commit: funzionalità, correzioni, breaking change, manutenzione.
3. Scarta i merge commit e i bump di versione.
4. Segui `template.md` alla lettera. Ogni voce sotto i 100 caratteri.
5. Se c'è un breaking change, mettilo per primo e marcalo **BREAKING**.
```

Due campi nel frontmatter contano:

- **`name`** — identificatore stabile, uguale alla cartella.
- **`description`** — **l'innesco**. È testo di prompt, ed è l'unica cosa che il
  modello vede prima di decidere se caricare la skill.

## La descrizione è tutto

Una skill che non si carica mai è peso morto; una skill che si carica per tutto è
veleno per il contesto.

| Descrizione scadente | Perché |
|---|---|
| "Aiuta con le release" | Vaga; compete con tutto |
| "Una skill per fare le note di rilascio" | Ripete il nome, non aggiunge innesco |
| "Note di rilascio, changelog, bump di versione, tag, release GitHub, semver, git log, messaggi di commit, …" | Minestra di parole chiave; si carica troppo spesso |

| Descrizione buona | Perché |
|---|---|
| "Scrive le note di rilascio dalla cronologia git. Usala quando ti viene chiesto di preparare una release, un changelog o 'cosa è cambiato da vX'." | Dice *cosa* e *quando*, con le parole dell'utente |

Formula: **cosa produce + quando usarla + le frasi che direbbe un utente.**

## Skill, strumenti, istruzioni

| | Istruzione (`AGENTS.md`) | Skill | Strumento |
|---|---|---|---|
| Caricamento | sempre | su richiesta | schema sempre, risultato alla chiamata |
| Contiene | regole, comandi, trappole | una procedura | un'azione |
| Cambia | come si comporta il modello | cosa sa fare il modello | cosa può fare il modello |
| Costo | piccolo, fisso | medio, quando usata | schema sempre + risultato |
| Esempio | "esegui `make test`" | "come scrivere una migrazione" | `read_file` |

Un test utile: se si può *fare*, è uno strumento. Se è una *procedura*, è una
skill. Se è un *vincolo*, è un'istruzione.

## Script e risorse

Le skill possono includere codice. Due pattern:

**Risorsa** — un template che il modello legge e compila:

```markdown
Segui `template.md`. Non inventare sezioni.
```

**Script** — un passo deterministico che il modello non deve ri-derivare:

```
skills/
  db-migration/
    SKILL.md
    new_migration.py     ← genera un file correttamente nominato e datato
```

```markdown
Esegui `python3 skills/db-migration/new_migration.py <nome>`.
Non creare il file a mano — il formato del timestamp conta.
```

È lo stesso principio degli hook: **il lavoro deterministico appartiene al codice,
non a un prompt.** Una skill può portare il codice e le istruzioni per usarlo.

⚠️ Lo script di una skill è codice eseguito. Tratta la cartella di una skill di
terze parti come una dipendenza di terze parti.

## Modalità di fallimento

| Fallimento | Causa | Soluzione |
|---|---|---|
| La skill non si carica mai | Descrizione vaga | Riscrivi l'innesco nella lingua dell'utente |
| Si carica per tutto | Descrizione troppo ampia | Aggiungi "Usala quando…" e delimita |
| Si carica ma viene ignorata | Il corpo è prosa, non passi | Passi numerati, comandi concreti |
| Contraddice `AGENTS.md` | Due fonti di verità | Eliminane una; le regole stanno nelle istruzioni |
| Sono 3.000 token di contesto | Nessuna divulgazione progressiva interna | Sposta i dettagli nelle risorse (L3) |
| Il modello ri-deriva invece di eseguire lo script | Non glielo hai detto | "Esegui X. Non fare Y a mano." |

## Checklist di scrittura

- [ ] Il nome corrisponde alla cartella, minuscolo, con trattini.
- [ ] La descrizione dice output + frasi di innesco, sotto i ~200 caratteri.
- [ ] Il corpo è a passi numerati, non un saggio.
- [ ] Ogni comando è copiabile e corretto.
- [ ] I dettagli stanno nelle risorse, non nel corpo.
- [ ] Nessuna regola duplicata da `AGENTS.md`.
- [ ] Testata: si carica per il compito previsto e *non* per uno vicino?

## Laboratorio

```bash
python3 labs/L07_skills.py
```

Creerai due skill, ispezionerai il costo del catalogo a L1, ne caricherai una a
L2, leggerai una risorsa a L3 e vedrai una descrizione vaga non corrispondere,
mentre una specifica sì.

🔬 **Fallo fallire:** dai a due skill descrizioni quasi identiche e guarda il
matcher scegliere arbitrariamente.

## ✅ Verifica

1. Quale problema risolve la divulgazione progressiva, in termini di token?
2. Quali sono i tre livelli di divulgazione?
3. Cosa rende buona o cattiva una descrizione?
4. Skill, strumento o istruzione: "non toccare mai `legacy/`"?
5. Perché spedire uno script con una skill invece di descrivere i passi?

<details>
<summary>Risposte</summary>

1. Il costo fisso del contesto: N skill costano ~50 token ciascuna invece di
   ~800.
2. Riga di catalogo, corpo completo, risorse/script.
3. Buona: output + quando + frasi dell'utente. Cattiva: vaga o minestra di
   parole chiave.
4. Istruzione.
5. Il lavoro deterministico (nomi, timestamp, formattazione) non va ri-derivato
   da un modello probabilistico.
</details>
