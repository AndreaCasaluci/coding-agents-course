# 08 — Hook ed eventi del ciclo di vita

> **Obiettivi**
> - Spiegare perché alcuni comportamenti non possono vivere in un prompt.
> - Implementare hook di osservazione, blocco e modifica.
> - Stratificare correttamente hook, permessi e sandbox.

## I prompt sono suggerimenti. Gli hook sono regole.

Puoi scrivere "non modificare mai `.env`" in `AGENTS.md`. Il modello di solito
ubbidirà. "Di solito" non è una proprietà di sicurezza.

Un hook è **codice legato a un evento**. Gira ogni volta, in un ordine
deterministico, e il suo verdetto è imposto dall'harness:

```python
hooks.on(PRE_EDIT, deny_paths((".env", ".git", "secrets")))
```

Non è un suggerimento. È un ramo nel flusso di controllo dell'harness.

Il principio di progetto:

> Se violare la regola è inaccettabile, non deve dipendere dalla cooperazione del
> modello.

## La superficie degli eventi

| Evento | Quando | Uso tipico |
|---|---|---|
| `session_start` | prima della prima chiamata al modello | caricare contesto, banner |
| `user_prompt` | testo del compito, prima di entrare in trascrizione | riscrivere, oscurare, rifiutare |
| `pre_tool` | prima che giri qualsiasi strumento | bloccare, riscrivere argomenti, approvare |
| `post_tool` | dopo qualsiasi strumento | oscurare segreti, troncare, loggare |
| `pre_edit` | prima di scrittura/modifica/cancellazione | proteggere percorsi, imporre stile |
| `post_edit` | dopo una scrittura/modifica riuscita | formattare, typecheck, stage |
| `session_end` | dopo la fine del ciclo | riassunto, metriche, pulizia |

Gli eventi `pre_*` sono **cancelli**. Gli eventi `post_*` sono **filtri ed
effetti collaterali**. Confonderli produce hook che non possono impedire nulla.

## Tre verbi

### Osservare

```python
def audit(handle):
    def hook(payload):
        handle.write(json.dumps(payload) + "\n")
        return None          # None = astensione
    return hook
```

Economico, noioso, inestimabile. Quando un agente fa qualcosa di strano, il log
di audit ti dice cosa ha davvero chiamato.

### Bloccare

```python
def deny_paths(prefixes):
    def hook(payload):
        path = payload["path"]
        if any(path.startswith(p) for p in prefixes):
            return HookResult(allow=False, reason=f"protected: {path}")
        return None
    return hook
```

Il rifiuto diventa un messaggio `DENIED: …`. Il modello lo vede e può scegliere
un'altra strada. Bloccare non significa far cadere tutto.

### Modificare

```python
def redact(payload):
    cleaned = SECRET_RX.sub("[REDACTED]", payload["content"])
    if cleaned != payload["content"]:
        return HookResult(payload={**payload, "content": cleaned})
    return None
```

La modifica è potente e pericolosa. Riscrivere gli *argomenti* di uno strumento
cambia ciò che il modello ha chiesto; riscriverne il *risultato* cambia ciò che
crede sia successo. Preferisci bloccare piuttosto che riscrivere in silenzio — il
modello può ragionare su "negato", non su una bugia.

## Fallire chiusi

```python
try:
    result = hook(payload)
except Exception as exc:
    return HookResult(False, f"hook raised {exc}")
```

Se un hook di sicurezza va in crash, il default sicuro è *negare*. L'harness qui
lo fa. Nota il compromesso: un hook difettoso può fermare tutto il lavoro. Di
solito è il compromesso giusto per un guardrail, e quello sbagliato per un
formatter — quindi tieni la formattazione in `post_edit`, dove un fallimento non
può bloccare una scrittura.

## Hook che scriverai davvero

| Hook | Evento | Effetto |
|---|---|---|
| Proteggi `.env`, `.git`, `secrets/` | `pre_edit` | blocca |
| Oscura chiavi API nell'output | `post_tool` | modifica |
| Auto-formatta dopo la modifica | `post_edit` | effetto collaterale |
| Esegui il typecheck dopo la modifica | `post_edit` | effetto collaterale; mostra errori |
| Richiedi approvazione per `git push` | `pre_tool` | blocca finché un umano approva |
| Blocca `rm -rf`, `--force`, `DROP TABLE` | `pre_tool` | blocca |
| Accoda ogni chiamata a un log JSONL | `pre_tool` | osserva |
| Impedisci diff oltre una dimensione | `pre_edit` | blocca |
| Aggiungi un trailer di co-autore al commit | `post_edit` | modifica |

## Hook, permessi e sandbox

Sono tre livelli della stessa difesa, con forza crescente:

```
┌─────────────────────────────────────────────┐
│ istruzione    "per favore non farlo"  debole│
├─────────────────────────────────────────────┤
│ hook          politica deterministica       │
├─────────────────────────────────────────────┤
│ permesso      allowlist / approvazione / modi│
├─────────────────────────────────────────────┤
│ sandbox       imposizione a livello OS      │  più forte
└─────────────────────────────────────────────┘
```

- Un **hook** vede eventi strutturati e può ragionare sull'intento ("questo
  percorso è protetto?", "questo comando contiene `--force`?"). Gira
  in-process, quindi un processo agente compromesso può aggirarlo.
- Un **sistema di permessi** decide se una *classe* di azione è consentita:
  modalità sola lettura, comandi in allowlist, approvazione per strumento.
- Una **sandbox** impone a livello di sistema operativo: niente rete, mount in
  sola lettura, un container senza accesso all'host. Regge anche se l'agente è
  completamente ostile.

Usa tutti e tre. Hook per politica e osservabilità, permessi per capacità
grossolane, sandbox per il raggio d'impatto.

## Testare gli hook

Gli hook sono codice, quindi testali come codice:

```python
def test_deny_env():
    hook = deny_paths((".env",))
    assert hook({"path": ".env"}).allow is False
    assert hook({"path": "src/app.py"}) is None
```

Due proprietà da verificare per ogni guardrail:

1. Nega ciò che deve negare.
2. Si **astiene** su tutto il resto — un guardrail che restituisce
   `HookResult(True)` per payload non correlati ingoierà in silenzio le modifiche
   di altri hook.

## Laboratorio

```bash
python3 labs/L08_hooks.py
```

Costruirai un bus con un hook di audit, un guardrail sui percorsi e un oscuratore
di segreti, poi vedrai una scrittura su `.env` negata, una chiave ripulita
dall'output e un hook che va in crash fallire chiuso.

🔬 **Fallo fallire:** fai restituire al guardrail `HookResult(True)` invece di
`None` per percorsi non correlati e guarda una modifica successiva venire
scartata.

## ✅ Verifica

1. Perché "non modificare mai `.env`" non può vivere solo in `AGENTS.md`?
2. Qual è la differenza tra eventi `pre_*` e `post_*`?
3. Perché preferire il blocco alla riscrittura silenziosa di un risultato?
4. Perché un guardrail deve fallire chiuso, mentre un formatter no?
5. Cosa aggiunge una sandbox che un hook non può dare?

<details>
<summary>Risposte</summary>

1. I prompt sono probabilistici; gli hook sono flusso di controllo imposto.
2. I `pre_*` possono impedire; i `post_*` possono solo filtrare o reagire.
3. Il modello può ragionare su "negato"; una riscrittura silenziosa gli dà una
   falsa immagine del mondo.
4. Un guardrail rotto non deve aprire il cancello; un formatter rotto salta solo
   la formattazione.
5. L'imposizione fuori dal processo dell'agente, che sopravvive a un agente
   compromesso o ostile.
</details>
