"""Laboratorio 00 — Leggere una trascrizione.

Esegui: python3 labs/L00_orientation.py

Obiettivo: vedere un'esecuzione completa dell'agente come dato, e identificare
quali parti vengono dal modello e quali dall'ambiente.
"""

from _helpers import note, section, temp_ws

from mini_agent import Agent, Message, ToolCall, Workspace, make_fs_tools
from mini_agent.context import transcript_tokens
from mini_agent.llm import ScriptedLLM

DATES = '''\
from datetime import datetime

FMT = "%Y-%m-%d"

def parse_date(s):
    return datetime.strptime(s, FMT)
'''


def main() -> None:
    with temp_ws("orientation") as tmp:
        ws = Workspace(tmp)
        ws.write("src/dates.py", DATES)

        # Il modello preimpostato sostituisce uno vero. Ogni Message qui è
        # qualcosa che un modello avrebbe potuto produrre.
        llm = ScriptedLLM(
            Message("assistant", "Localizzo parse_date.", [ToolCall("c1", "search", {"pattern": "def parse_date"})]),
            Message("assistant", "Leggo la funzione.", [ToolCall("c2", "read_file", {"path": "src/dates.py"})]),
            Message(
                "assistant",
                "Un input vuoto farà sollevare a strptime un ValueError poco chiaro. Aggiungo un controllo esplicito.",
                [
                    ToolCall(
                        "c3",
                        "edit_file",
                        {
                            "path": "src/dates.py",
                            "old": "def parse_date(s):\n    return datetime.strptime(s, FMT)",
                            "new": "def parse_date(s):\n    if not s:\n        raise ValueError(\"data vuota\")\n    return datetime.strptime(s, FMT)",
                        },
                    )
                ],
            ),
            "Aggiunto un controllo per la stringa vuota a parse_date.",
        )

        agent = Agent(llm, make_fs_tools(ws), workspace=ws, max_turns=8)
        result = agent.run("parse_date va in crash su input vuoto. Correggila.")

        section("TRASCRIZIONE")
        for i, message in enumerate(result.messages):
            print(f"\n--- messaggio {i} ---")
            print(message.text())

        section("ANNOTAZIONE")
        by_role: dict[str, int] = {}
        for message in result.messages:
            by_role[message.role] = by_role.get(message.role, 0) + 1
        note(f"messaggi per ruolo: {by_role}")
        note(f"chiamate al modello (messaggi assistant): {by_role.get('assistant', 0)}")
        note(f"esecuzioni di strumenti (messaggi tool):  {by_role.get('tool', 0)}")
        note(f"chiamate a strumenti richieste:           {len(result.tool_calls)}")
        note(f"token stimati alla fine:                   {transcript_tokens(result.messages)}")
        note(f"motivo di arresto:                         {result.stopped_reason}")

        section("IL FILE DOPO L'ESECUZIONE")
        print(ws.read("src/dates.py"))

        section("COSA NOTARE")
        note("I messaggi dell'assistente sono ipotesi. I messaggi tool sono osservazioni.")
        note("Il modello non ha eseguito nulla; l'ha fatto l'harness, incollando i risultati.")
        note("L'esecuzione è finita quando un messaggio dell'assistente non aveva chiamate.")
        note("Il numero di turni == messaggi dell'assistente, non chiamate agli strumenti.")


if __name__ == "__main__":
    main()
