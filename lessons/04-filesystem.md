# 04 — Il filesystem come mondo

> **Obiettivi**
> - Spiegare perché gli agenti di coding hanno la forma del filesystem.
> - Progettare una superficie di lettura/ricerca/modifica che sopravviva allo
>   stato obsoleto.
> - Riconoscere le modalità di fallimento di percorsi e patch prima che ti
>   costino un file.

## Perché la repo è l'interfaccia

Un agente che sa leggere, cercare e modificare file può lavorare su qualsiasi
linguaggio, framework e build system — senza un'integrazione dedicata. Il
filesystem è il minimo comun denominatore del lavoro software, e possiede già le
proprietà che servono: durevole, confrontabile con diff, versionato e
ispezionabile.

Per questo il design dominante degli agenti di coding è "una shell con opinioni",
non "un plugin per ogni IDE".

## La superficie canonica

Sei strumenti coprono quasi tutto:

| Strumento | Scopo | Lettura/scrittura |
|---|---|---|
| `list_files(path, depth)` | orientarsi | lettura |
| `read_file(path, start, end)` | ispezionare | lettura |
| `search(pattern, glob)` | localizzare | lettura |
| `write_file(path, content)` | creare / sostituire | scrittura |
| `edit_file(path, old, new)` | modifica chirurgica | scrittura |
| `delete_file(path)` | rimuovere | scrittura |

Nota cosa manca: niente `move`, niente `chmod`, niente `git`. Aggiungili solo
quando il compito lo richiede. Ogni strumento in più è contesto speso e un nuovo
modo di sbagliare.

## Leggere prima di modificare non è opzionale

La conoscenza che il modello ha di un file è una **copia nella trascrizione**.
Quella copia diventa obsoleta nel momento in cui qualcosa tocca il file: un altro
agente, l'utente, un formatter, una build.

```
turno 3: read_file("app.py")      → copia A nel contesto
turno 4: l'utente modifica app.py → il disco ora è B
turno 5: il modello modifica su A → corrompe la modifica dell'utente
```

L'harness non può impedirlo del tutto. Può renderlo *rilevabile*:

- **Modifiche con ancora unica.** `edit_file(old, new)` fallisce se `old` manca
  o compare più di una volta. Una copia obsoleta di solito fallisce
  rumorosamente invece di sovrascrivere in silenzio.
- **Tracciamento lettura-prima-di-scrittura.** Alcuni harness rifiutano una
  modifica a un file non letto in questa sessione, o il cui mtime è cambiato
  dalla lettura.
- **Letture piccole.** Rileggi la regione modificata prima di una seconda
  modifica, non tutto il file.

## Perché le patch battono le riscritture

`write_file` con il contenuto completo è lo strumento più pericoloso del
cassetto:

```
il modello ha una copia obsoleta (200 righe)
write_file(path, contenuto_obsoleto)
→ 3 righe del nuovo lavoro dell'utente sono sparite
```

`edit_file(old, new)` con un'ancora unica:

```
old = "def parse_date(s):\n    return datetime.strptime(s, FMT)"
new = "def parse_date(s):\n    if not s:\n        raise ValueError('empty')\n    return datetime.strptime(s, FMT)"
```

è limitato: o trova esattamente una corrispondenza e applica, oppure fallisce e
spiega perché. Il raggio d'impatto è l'ancora, non il file.

> Regola pratica: **riscrivi solo quando crei un file nuovo.** Per i file
> esistenti, modifica.

## Obsolescenza in pratica

Il ciclo più comune è:

1. Leggi un file da 300 righe (7k token).
2. Fai la modifica #1.
3. Fai la modifica #2 usando il contenuto *pre-modifica* come ancora.
4. La modifica #2 fallisce o, peggio, si applica nel posto sbagliato.

Mitigazioni, in ordine di efficacia:

- **Modifica in una sola chiamata quando possibile** — un unico `old`/`new` che
  copre entrambe le modifiche.
- **Rileggi la regione** tra una modifica e l'altra (economico:
  `start`/`end`).
- **Ancora su stringhe piccole e uniche**, non su intere funzioni.
- **Verifica dopo la modifica**: rileggi la regione o esegui i test.

## La ricerca è il vero superpotere

Un agente con `grep` non ha bisogno della repo nel contesto. Ha bisogno di sapere
*dove guardare*.

Buon output di ricerca:

```
src/dates.py:41: def parse_date(s):
tests/test_dates.py:12: from src.dates import parse_date
```

Cattivo output di ricerca:

```
[7000 righe di corrispondenze]
```

Regole di progetto:

- Limita le corrispondenze (200 bastano) e dì quando hai troncato.
- Includi percorso e numero di riga, così la lettura successiva è un intervallo,
  non un file.
- Supporta un filtro glob (`*.py`) — è lo strumento di precisione più economico
  disponibile.
- Restituisci esplicitamente `(no matches)`. Il silenzio viene letto come
  successo.

## File grandi

Un file generato da 5.000 righe farà saltare il budget con una sola lettura. Lo
strumento deve:

- troncare a un limite di caratteri noto e **dirlo**,
- supportare intervalli di righe,
- non troncare mai in silenzio a metà token senza un marcatore.

`Workspace.read` lo fa con `MAX_READ_CHARS` e un suffisso esplicito
`[truncated: ...]`. Il modello può quindi chiedere un intervallo. Senza il
marcatore, crede di aver visto tutto il file e modifica alla cieca.

## Sicurezza dei percorsi

L'agente fornisce i percorsi come testo. Il testo può evadere:

```
../../etc/passwd
/percorso/assoluto
link → /etc/passwd        (symlink)
a/../../b
```

L'unico controllo affidabile è: **risolvi a un percorso reale, poi verifica il
contenimento**.

```python
real = (root / path).resolve()
if real != root and root not in real.parents:
    raise WorkspaceError(...)
```

Nota che `.resolve()` segue i symlink, quindi il caso del symlink viene
intercettato. Nota anche che questo è un confine di *correttezza*, non di
sicurezza contro un processo ostile — un attaccante determinato con esecuzione
di codice può aggirarlo. L'isolamento vero è un container (modulo 12).

## Git è il tuo pulsante annulla

Prima di una sessione su una repo vera:

```bash
git status          # sappi cosa è già sporco
git switch -c agent/nome-compito
```

Dopo:

```bash
git diff            # l'unico riassunto onesto di cosa è successo
```

Il riassunto in prosa dell'agente è una dichiarazione. `git diff` è una prova.
Rendi la revisione del diff un'abitudine e l'autovalutazione dell'agente diventa
facoltativa.

Per agenti paralleli usa i **worktree** — checkout separati su branch separati
che condividono un unico object store. Isolamento economico, niente stash,
niente conflitti fino al merge.

## Laboratorio

```bash
python3 labs/L04_filesystem.py
```

Il laboratorio dimostra la prigione dei percorsi (inclusa l'evasione tramite
symlink), la modifica con ancora unica, il rifiuto delle corrispondenze ambigue,
il troncamento con marcatore e una corruzione da copia obsoleta che una
riscrittura causa e una modifica previene.

🔬 **Fallo fallire:** commenta il controllo di contenimento in
`Workspace.resolve` ed esegui di nuovo. Guarda `../../etc/passwd` risolversi.

## ✅ Verifica

1. Perché il filesystem è l'interfaccia naturale per un agente di coding?
2. Cosa rende `edit_file(old, new)` più sicuro di `write_file(content)`?
3. Come produce una modifica sbagliata una lettura obsoleta, e cosa la rileva?
4. Perché il troncamento deve essere annunciato?
5. Qual è la differenza tra confine di correttezza e confine di sicurezza qui?

<details>
<summary>Risposte</summary>

1. È universale, durevole, confrontabile con diff e versionato.
2. Il raggio d'impatto è limitato dall'ancora; l'ambiguità fallisce
   rumorosamente.
3. La copia del modello diverge dal disco; il fallimento dell'ancora unica o una
   rilettura lo rilevano.
4. Altrimenti il modello crede di aver visto tutto il file e modifica alla cieca.
5. La prigione dei percorsi previene gli errori; non ferma l'esecuzione di codice
   o un attaccante determinato. Solo l'isolamento lo fa.
</details>
