# Glossario

I termini sono definiti come li usa questo corso. Dove il settore è incoerente,
vince il significato più comune e l'alternativa viene segnalata.

**Agente** — Un sistema che chiama ripetutamente un modello linguistico, lo lascia agire
tramite gli strumenti e rimanda indietro i risultati, finché non si raggiunge una condizione
di stop. Un chatbot con una sola chiamata al modello non è un agente. È il ciclo a renderlo tale.

**Ciclo dell'agente** — Il ciclo *chiamata al modello → chiamata/e agli strumenti → osservazione →
chiamata al modello*. Chiamato anche ciclo ReAct, dal paper del 2022, anche se ogni
implementazione è diversa.

**AGENTS.md** — Una convenzione per un file Markdown nella radice di una repo (o nelle
sottocartelle) che contiene istruzioni per gli agenti di coding. Letto automaticamente da
molti strumenti; la cosa più vicina a uno standard cross-vendor per il contesto dell'agente.

**Allowlist** — L'insieme di comandi, percorsi o strumenti che un agente può usare senza
chiedere. Tutto il resto è negato o richiede l'intervento umano.

**Finestra di contesto** — Il numero massimo di token a cui un modello può prestare attenzione in una
chiamata, contando system prompt, cronologia, risultati degli strumenti e la risposta. Non è memoria;
viene ricalcolata (o messa in cache) a ogni chiamata.

**Compaction** — Sostituire la vecchia conversazione con un riassunto così che l'esecuzione possa
proseguire oltre il limite di contesto. Per definizione introduce perdita, ed è per questo che è una
fonte di bug sottili.

**Eval** — Un test ripetibile del comportamento dell'agente: un task, un ambiente e un
valutatore. L'equivalente dell'unit test per un agente, ma con un soggetto non deterministico.

**Function calling / tool calling** — Il modello che emette una richiesta strutturata
("chiama `read_file` con `{"path": "a.py"}`") che l'harness esegue. Il
modello non esegue mai nulla da solo.

**Hook** — Un gestore definito dall'utente, legato a un evento del ciclo di vita (prima che uno strumento
venga eseguito, dopo una modifica, all'avvio della sessione). Gli hook sono codice, non prompt, quindi
sono deterministici.

**MCP (Model Context Protocol)** — Un protocollo basato su JSON-RPC per esporre
strumenti, risorse e prompt agli agenti tramite un'interfaccia standard, così che un
server funzioni con molti client.

**Prompt injection** — Istruzioni nascoste nel contenuto che l'agente legge (un file,
una pagina web, un risultato di uno strumento) che ne dirottano il comportamento. Il principale problema
di sicurezza irrisolto per gli agenti.

**Divulgazione progressiva** — Caricare solo una piccola descrizione di una skill o di uno
strumento all'inizio, e il suo contenuto completo solo quando serve. La tecnica principale per
tenere grandi insiemi di capacità dentro un budget di contesto.

**Sandbox** — Un confine imposto su ciò che l'agente può toccare: un
container, un worktree, un path jail, un profilo di permessi. L'imposizione è
fuori dal modello.

**Skill** — Una procedura impacchettata e scopribile (di solito una cartella con un
`SKILL.md` e script/risorse opzionali) che un agente carica quando un task
corrisponde alla sua descrizione.

**Subagente** — Un'esecuzione separata dell'agente, di solito con la propria finestra di contesto,
generata da un agente padre per un sotto-task. Restituisce un riassunto, non la sua intera
trascrizione.

**System prompt** — Le istruzioni fornite dall'harness che inquadrano ogni chiamata:
identità, regole, indicazioni sugli strumenti. Nella maggior parte dei prodotti non è modificabile dall'utente, ma è
la prima cosa da capire quando il comportamento sembra sbagliato.

**Token** — Un'unità di testo più piccola della parola. Circa 4 caratteri di inglese, ma il codice
e il testo non inglese sono meno efficienti. Tutti i limiti e i costi sono in token.

**Strumento** — Una capacità esposta al modello come nome, descrizione e
schema JSON. La descrizione è testo di prompt: cambia il comportamento.

**Turno** — Una chiamata al modello più le esecuzioni degli strumenti che ha richiesto. Un task è fatto di molti
turni.

**Worktree** — Un checkout separato di una repo sul proprio branch, che condivide lo
stesso object store. Isolamento economico per esecuzioni parallele degli agenti.
