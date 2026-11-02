# Lista di letture

Fonti canoniche, in ordine approssimativo di utilità. I link puntano al materiale primario;
i post di blog sono inclusi solo dove hanno nominato un problema meglio del paper.

## Protocolli e convenzioni

- **Model Context Protocol** — <https://modelcontextprotocol.io>
  La specifica e il modello primitivo (strumenti / risorse / prompt).
- **AGENTS.md** — <https://agents.md>
  La convenzione cross-vendor per il file di istruzioni.
- **JSON-RPC 2.0** — <https://www.jsonrpc.org/specification>
  Breve, e ti servirà per leggere le tracce MCP.

## Agenti

- **ReAct: Synergizing Reasoning and Acting in Language Models** (Yao et al.,
  2022) — <https://arxiv.org/abs/2210.03629>
  Da dove viene il ciclo ragiona/agisci/osserva.
- **Building Effective Agents** (Anthropic) —
  <https://www.anthropic.com/research/building-effective-agents>
  Flussi di lavoro contro agenti, e perché la cosa più semplice che funziona di solito vince.
- **Lost in the Middle** (Liu et al., 2023) — <https://arxiv.org/abs/2307.03172>
  La base empirica del "degrado del contesto".

## Sicurezza

- **OWASP Top 10 for LLM Applications** —
  <https://owasp.org/www-project-top-10-for-large-language-model-applications/>
  Prompt injection, agenzia eccessiva, supply chain.
- **Simon Willison's prompt injection tag** —
  <https://simonwillison.net/tags/prompt-injection/>
  Il miglior registro continuo di cosa si rompe davvero, e perché i prompt non lo risolvono.
- **The lethal trifecta** (dati privati + contenuto non fidato + comunicazione
  esterna) — il modello mentale per il rischio di esfiltrazione.

## Valutazione

- **pass@k** — il paper HumanEval (Chen et al., 2021) ha introdotto la metrica;
  l'idea si generalizza a qualunque agente non deterministico.
- **SWE-bench** — <https://www.swebench.com>
  Il benchmark di riferimento per gli agenti di coding a livello di repo; leggi il formato del task
  anche se non lo eseguirai mai.
- **Il tuo registro degli incidenti** — la suite di eval di maggior valore che avrai mai.

## Pratica

- **Google's "Code Review" guide** —
  <https://google.github.io/eng-practices/review/>
  Scritta per umani, si applica direttamente alla revisione dei diff degli agenti.
- **Git worktrees** — <https://git-scm.com/docs/git-worktree>
  La primitiva di isolamento più economica per agenti paralleli.

## Una nota sull'obsolescenza

La documentazione dei prodotti cambia ogni mese; i concetti qui sopra no. Se una lezione
e la documentazione di un vendor sono in disaccordo sulla *configurazione*, fidati del vendor. Se sono
in disaccordo sul *meccanismo*, fidati del meccanismo — e controlla la traccia.
