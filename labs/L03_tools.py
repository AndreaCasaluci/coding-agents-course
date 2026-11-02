"""Laboratorio 03 — Strumenti: schemi, dispatch e descrizioni.

Esegui: python3 labs/L03_tools.py

Obiettivo: vedere il JSON esatto che riceve il modello, osservare ogni modalità
di fallimento del dispatch e vedere come una descrizione cambia la scelta dello
strumento.
"""

from __future__ import annotations

import json
import re

from _helpers import note, section, temp_ws

from mini_agent import ToolRegistry, Workspace, make_fs_tools, tool
from mini_agent.messages import Message


@tool(side_effect=True, needs_permission=True)
def deploy(env: str = "staging") -> str:
    """Rilascia il branch corrente in un ambiente."""
    return f"rilasciato in {env}"


@tool(side_effect=True, needs_permission=True)
def rollback(service: str) -> str:
    """Riporta un servizio alla release precedente."""
    return f"{service} ripristinato"


def pick(task: str, registry: ToolRegistry) -> str:
    """Un 'modello' giocattolo: confronta le parole del compito con nome + descrizione."""
    words = {w for w in re.findall(r"[a-z]{4,}", task.lower())}
    best, score = "(nessuno)", 0
    for t in registry:
        haystack = f"{t.name} {t.description}".lower()
        s = sum(1 for w in words if w in haystack)
        if s > score:
            best, score = t.name, s
    return best


def main() -> None:
    with temp_ws("tools") as tmp:
        ws = Workspace(tmp)
        registry = ToolRegistry(make_fs_tools(ws)).add(deploy, rollback)

        section("1. LO SCHEMA CHE VEDE IL MODELLO")
        print(json.dumps(registry.get("read_file").schema(), indent=2))
        note("La descrizione è testo di prompt. Scrivila per il modello, non per l'autocompletamento.")

        section("2. NUMERO DI STRUMENTI E COSTO IN CONTESTO")
        from mini_agent.context import estimate_tokens

        payload = json.dumps(registry.schemas())
        print(f"  {len(registry)} strumenti -> {estimate_tokens(payload)} token stimati, a ogni chiamata")
        note("Gli strumenti non sono gratuiti. Un registro grande è una tassa permanente sul contesto.")

        section("3. MODALITÀ DI FALLIMENTO DEL DISPATCH")
        cases = [
            ("strumento sconosciuto", "does_not_exist", {}),
            ("argomento mancante", "read_file", {}),
            ("tipo sbagliato / chiave extra", "read_file", {"path": "a.py", "bogus": 1}),
            ("JSON malformato", "read_file", {"__parse_error__": "{not json"}),
        ]
        for label, name, args in cases:
            result = registry.dispatch(name, args)
            print(f"  {label:<32} ok={result.ok!s:<5} {result.content[:90]}")

        section("4. UNO STRUMENTO CHE SOLLEVA UN'ECCEZIONE")
        @tool
        def divide(a: int, b: int) -> float:
            """Divide a per b."""
            return a / b

        result = ToolRegistry([divide]).dispatch("divide", {"a": 1, "b": 0})
        note(f"ok={result.ok} content={result.content!r}")
        note("Il ciclo sopravvive. Il modello vede l'errore e può adattarsi.")

        section("5. LE DESCRIZIONI GUIDANO LA SCELTA")
        vague = ToolRegistry([
            tool(name="query", description="Interroga cose")(lambda text: text),
            tool(name="fetch", description="Recupera cose")(lambda text: text),
        ])
        specific = ToolRegistry([
            tool(name="search_code", description="Cerca nei file sorgente con una regex. Usalo per trovare definizioni e punti di chiamata.")(lambda text: text),
            tool(name="fetch_url", description="Scarica una pagina web via HTTP. Usalo per documentazione esterna.")(lambda text: text),
        ])
        task = "cerca la definizione di parse_date nel codice"
        print(f"  compito: {task!r}")
        print(f"  descrizioni vaghe    -> {pick(task, vague)}")
        print(f"  descrizioni specifiche -> {pick(task, specific)}")
        note("Stesso modello, stesso compito. Ha fatto tutto la descrizione.")

        section("6. GLI EFFETTI COLLATERALI SI DICHIARANO, NON SI INDOVINANO")
        for name in ("read_file", "write_file", "delete_file", "deploy"):
            t = registry.get(name)
            print(f"  {name:<14} side_effect={t.side_effect!s:<5} needs_permission={t.needs_permission}")
        note("L'harness usa questi metadati per l'approvazione; il modello non li vede mai.")


if __name__ == "__main__":
    _ = Message
    main()
