# Tradurre e mantenere questo branch

Il branch `main` è la fonte di verità, in inglese. Il branch `it` è la versione
italiana completa. Questo documento spiega come restano allineati.

## Cosa è tradotto

- Tutti i file Markdown: lezioni, README, curriculum, glossario, cheat sheet,
  documentazione del progetto finale, `SKILL.md`.
- I laboratori: intestazioni, note, commenti e messaggi stampati.
- Il codice di `mini_agent/`: docstring e commenti principali, messaggi
  rivolti all'utente, system prompt dell'agente, help della CLI.
- Il progetto finale: contenuto di `REPORT.md`, eval, messaggi.

## Cosa resta in inglese, di proposito

Queste stringhe sono un contratto tra harness, test e modelli. Tradurle
romperebbe i test o cambierebbe il protocollo:

- il prefisso `DENIED:` nei risultati negati;
- il marcatore `[compacted earlier conversation — summary, not verbatim]`;
- i nomi dei ruoli (`system`, `user`, `assistant`, `tool`);
- i metodi JSON-RPC e i nomi dei campi;
- i nomi di strumenti, funzioni, classi, moduli e file;
- i comandi, i flag della CLI e le variabili d'ambiente.

I nomi dei prodotti e dei paper restano in originale.

## Sincronizzare con `main`

Quando `main` cambia:

```bash
git checkout it
git merge main
```

Poi:

1. Risolvi i conflitti **preferendo `main` per il codice e i test** — la logica
   inglese è la verità.
2. Ritraduci solo le parti nuove o modificate. Non ritradurre ciò che non è
   cambiato: genera conflitti inutili al merge successivo.
3. Se `main` ha cambiato una stringa di protocollo, aggiorna anche la
   traduzione dei test corrispondenti.
4. Verifica:

```bash
python3 run.py test
python3 run.py labs
python3 run.py capstone
```

5. Committa con un messaggio che dice cosa è stato sincronizzato:

```
merge main -> it: riallineate lezioni 04-06, nuovi esempi in 11
```

## Regole di stile

Vedi il glossario in [`GLOSSARY.md`](GLOSSARY.md). In breve:

- dai del "tu", imperativo nelle istruzioni;
- termini tecnici consolidati in inglese (harness, hook, skill, prompt, token,
  sandbox, workspace, diff, commit, branch);
- "strumento" per *tool*, ma i nomi dei tool restano inglesi;
- "ciclo dell'agente" per *agent loop*;
- "trascrizione" per *transcript*;
- "verifica" per *checkpoint*.

## Cosa non fare

- Non tradurre identificatori o chiavi JSON.
- Non cambiare la struttura dei file Markdown.
- Non "migliorare" il contenuto durante la traduzione: se vuoi cambiare una
  lezione, fallo prima su `main`.
