"""Laboratorio 06 — File di istruzioni e precedenza.

Esegui: python3 labs/L06_instructions.py

Obiettivo: vedere la scoperta di AGENTS.md, la precedenza e la differenza tra
un'istruzione vaga e una specifica.
"""

from __future__ import annotations

from pathlib import Path

from _helpers import note, section, temp_ws

from mini_agent import Agent, Message, Workspace, discover, make_fs_tools
from mini_agent.llm import PolicyLLM

ROOT_MD = """\
# AGENTS.md

## Comandi
- Test: `make test`   (avvia un container Postgres)
- Lint: `ruff check .`

## Invarianti
- Mai fare commit su `main`.
- Il denaro è in centesimi interi. Niente float.

## Trappole
- `legacy/` è congelata. Non fare refactoring.
"""

BACKEND_MD = """\
# backend/AGENTS.md

- Le migrazioni passano da `alembic revision`, mai scritte a mano.
- Il DB di test viene azzerato a ogni test; non condividere fixture tra moduli.
"""


def main() -> None:
    with temp_ws("instructions") as tmp:
        root = Path(tmp)
        (root / "AGENTS.md").write_text(ROOT_MD)
        (root / "backend").mkdir()
        (root / "backend" / "AGENTS.md").write_text(BACKEND_MD)
        (root / "src").mkdir()

        section("1. SCOPERTA DALLA RADICE")
        found = discover(root)
        for item in found.items:
            print(f"  {item.scope:<7} {item.path.relative_to(root)}")

        section("2. SCOPERTA DA UNA SOTTODIRECTORY")
        found_sub = discover(root, start=root / "backend")
        for item in found_sub.items:
            print(f"  {item.scope:<7} {item.path.relative_to(root)}")
        note("Prima la radice, poi il file più vicino. Lo specifico sovrascrive il generale.")

        section("3. COSA RICEVE DAVVERO IL MODELLO")
        agent = Agent(
            PolicyLLM(lambda m, t: Message("assistant", "ok")),
            make_fs_tools(Workspace(root)),
            workspace=Workspace(root),
            instructions=found_sub,
        )
        prompt = agent.system_prompt()
        start = prompt.find("# Project instructions")
        print(prompt[start:start + 700])
        note("Le istruzioni vengono reinviate a ogni chiamata. Non scorrono via.")

        section("4. VAGA VS SPECIFICA")
        # Un modello giocattolo che ubbidisce solo a regole azionabili.
        def make_policy(rule_text: str):
            def policy(messages, tools):
                system = messages[0].content
                if "Usa il logger in `obs/log.py`" in system:
                    return Message("assistant", "Uso obs.log.logger, non print().")
                if "Non usare print" in system:
                    return Message("assistant", "Eviterò print() … probabilmente.")
                return Message("assistant", "Nessuna regola di logging trovata; uso print() come il codice circostante.")

            return PolicyLLM(policy)

        vague_md = "# AGENTS.md\n\n- Non usare print.\n"
        specific_md = "# AGENTS.md\n\n- Usa il logger in `obs/log.py` (`from obs.log import logger`).\n"

        for label, text in (("vaga", vague_md), ("specifica", specific_md)):
            (root / "AGENTS.md").write_text(text)
            a = Agent(
                make_policy(text),
                make_fs_tools(Workspace(root)),
                workspace=Workspace(root),
                instructions=discover(root),
            )
            result = a.run("aggiungi logging al gestore del checkout")
            print(f"  {label:<10} -> {result.final}")
        note("Un divieto dice cosa non fare. Il modello riempie il vuoto con un'ipotesi.")

        section("5. LA SCALA")
        note("istruzione  → un suggerimento, probabilistico")
        note("hook        → deterministico, in-process")
        note("test        → verificabile, sopravvive alla sessione")
        note("sistema di tipi → imposto dal compilatore")
        note("Sposta una regola più in basso in questa scala quando violarla conta.")

        section("6. LA DIMENSIONE CONTA")
        note(f"AGENTS.md radice   : {len(ROOT_MD.splitlines())} righe")
        note(f"AGENTS.md backend  : {len(BACKEND_MD.splitlines())} righe")
        note("Punta a 30–80 righe in totale. File più lunghi diluiscono le regole che contano.")


if __name__ == "__main__":
    main()
