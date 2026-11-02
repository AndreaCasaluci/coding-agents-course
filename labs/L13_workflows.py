"""Laboratorio 13 — Flussi di lavoro: one-shot vs esplora-pianifica-esegui-verifica.

Esegui: python3 labs/L13_workflows.py

Obiettivo: eseguire la stessa correzione in due modi e confrontare il diff, i
turni e le prove.
"""

from __future__ import annotations

from _helpers import note, section, temp_ws

from mini_agent import Agent, Message, ToolCall, Workspace, make_fs_tools, tool
from mini_agent.llm import ScriptedLLM

ORIGINAL = """\
from datetime import datetime

FMT = "%Y-%m-%d"

def parse_date(s):
    return datetime.strptime(s, FMT)

def helper():
    return 42
"""


def main() -> None:
    section("SETUP")
    note("Bug: parse_date('') solleva un ValueError poco chiaro da strptime.")
    note("Specifica: deve sollevare ValueError('data vuota'), e helper() deve sopravvivere.")

    with temp_ws("workflow") as tmp:
        ws = Workspace(tmp)
        ws.write("src/dates.py", ORIGINAL)

        @tool
        def run_tests() -> str:
            """Esegue la suite di test."""
            content = ws.read("src/dates.py")
            if "if not s" not in content:
                return "FALLITO tests/test_dates.py::test_empty_string\n  atteso ValueError('data vuota')"
            if "def helper" not in content:
                return "FALLITO tests/test_dates.py::test_helper\n  helper() è sparito"
            return "2 passati in 0,01s"

        tools = make_fs_tools(ws) + [run_tests]

        section("1. ONE-SHOT: 'correggi'")
        # Il modello riscrive tutto il file dalla prima ipotesi. Non ha mai
        # letto il file, quindi non sa che esiste helper().
        oneshot = ScriptedLLM(
            Message("assistant", "Riscrivo la funzione.", [
                ToolCall("c1", "write_file", {
                    "path": "src/dates.py",
                    "content": 'from datetime import datetime\n\nFMT = "%Y-%m-%d"\n\ndef parse_date(s):\n    if not s:\n        raise ValueError("data vuota")\n    return datetime.strptime(s, FMT)\n',
                })
            ]),
            "Corretto parse_date.",
        )
        before = ws.read("src/dates.py")
        result = Agent(oneshot, tools, workspace=ws, max_turns=6).run("correggi il bug della data vuota")
        after = ws.read("src/dates.py")
        print(f"  turni={result.turns} chiamate={result.tool_calls}")
        print(f"  test eseguiti dall'agente? {'run_tests' in result.tool_calls}")
        print(f"  helper() preservato? {'def helper' in after}")
        print(f"  righe: {len(before.splitlines())} -> {len(after.splitlines())}")
        print(f"  verdetto: {result.final}")

        section("2. STRUTTURATO: esplora -> pianifica -> test -> correggi -> verifica")
        ws.write("src/dates.py", ORIGINAL)
        structured = ScriptedLLM(
            Message("assistant", "Prima localizzo la funzione.", [
                ToolCall("c1", "search", {"pattern": "def parse_date"})
            ]),
            Message("assistant", "Leggo tutto il file per vedere cos'altro c'è.", [
                ToolCall("c2", "read_file", {"path": "src/dates.py"})
            ]),
            Message("assistant", "Piano: aggiungo un controllo in cima a parse_date. helper() è indipendente; lo lascio.", [
                ToolCall("c3", "edit_file", {
                    "path": "src/dates.py",
                    "old": "def parse_date(s):\n    return datetime.strptime(s, FMT)",
                    "new": "def parse_date(s):\n    if not s:\n        raise ValueError(\"data vuota\")\n    return datetime.strptime(s, FMT)",
                })
            ]),
            Message("assistant", "Verifico.", [ToolCall("c4", "run_tests", {})]),
            "Aggiunto il controllo per la stringa vuota; i test passano; helper() intatto.",
        )
        before = ws.read("src/dates.py")
        result = Agent(structured, tools, workspace=ws, max_turns=8).run("correggi il bug della data vuota")
        after = ws.read("src/dates.py")
        print(f"  turni={result.turns} chiamate={result.tool_calls}")
        print(f"  test eseguiti dall'agente? {'run_tests' in result.tool_calls}")
        print(f"  helper() preservato? {'def helper' in after}")
        print(f"  righe: {len(before.splitlines())} -> {len(after.splitlines())}")
        print(f"  verdetto: {result.final}")

        section("3. CONFRONTO")
        note("Stesso compito, stessi strumenti, stesso modello. Flusso diverso.")
        note("One-shot: meno turni, nessuna prova, perdita di dati silenziosa.")
        note("Strutturato: 2 turni in più, un piano, un'esecuzione dei test e un risultato verificabile.")
        note("I turni in più costano meno del ciclo di revisione che prevengono.")

        section("4. LA FORMA DELLA SESSIONE")
        note("1. ESPLORA   sola lettura, economico, cattura gli equivoci")
        note("2. PIANIFICA enuncia la modifica e i file, nessuna modifica")
        note("3. ESEGUI    modifiche piccole, una sola questione")
        note("4. VERIFICA  test, tipi, diff")
        note("5. RIPORTA   cosa è cambiato, cosa non è provato")

        section("5. QUANDO PRENDERE IL CONTROLLO")
        note("Stesso tentativo fallito due volte -> lo farà una terza.")
        note("Diff che cresce mentre i test restano rossi -> fermati.")
        note("Modifiche fuori dal perimetro dichiarato -> fermati.")
        note("Non riesci a spiegare la modifica -> fermati.")

    _ = ORIGINAL


if __name__ == "__main__":
    main()
