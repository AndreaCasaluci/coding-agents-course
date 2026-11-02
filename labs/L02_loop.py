"""Laboratorio 02 — Il ciclo: terminazione, recupero e rifiuto.

Esegui: python3 labs/L02_loop.py

Quattro scenari, ognuno un'esecuzione completa. Leggi la trascrizione, non solo
il riassunto.
"""

from _helpers import note, section, temp_ws

from mini_agent import Agent, Message, ToolCall, Workspace, make_fs_tools
from mini_agent.hooks import PRE_TOOL, HookBus, HookResult
from mini_agent.llm import PolicyLLM, ScriptedLLM


def show(result) -> None:
    for message in result.messages[1:]:
        print("   " + message.text().replace("\n", "\n   ")[:400])
    note(f"stop={result.stopped_reason} turni={result.turns} chiamate={result.tool_calls}")


def main() -> None:
    with temp_ws("loop") as tmp:
        ws = Workspace(tmp)
        ws.write("app.py", "def add(a, b):\n    return a + b\n")
        tools = make_fs_tools(ws)

        section("SCENARIO 1 — compito pulito in due turni")
        llm = ScriptedLLM(
            Message("assistant", "Leggo prima il file.", [ToolCall("c1", "read_file", {"path": "app.py"})]),
            "La funzione è corretta.",
        )
        show(Agent(llm, tools, workspace=ws, max_turns=5).run("Controlla app.py"))

        section("SCENARIO 2 — errore di uno strumento, il modello si riprende")
        llm = ScriptedLLM(
            Message("assistant", "Leggo il test.", [ToolCall("c1", "read_file", {"path": "test_app.py"})]),
            Message("assistant", "Nessun file di test. Elenco invece.", [ToolCall("c2", "list_files", {"path": "."})]),
            "Non c'è un file di test; solo app.py.",
        )
        show(Agent(llm, tools, workspace=ws, max_turns=6).run("Leggi test_app.py"))

        section("SCENARIO 3 — un modello che non si ferma mai")
        # Questa policy chiama sempre uno strumento, come un modello in retry.
        def stuck(messages, schemas):
            return Message("assistant", "Riprovo.", [ToolCall("x", "list_files", {"path": "."})])

        result = Agent(PolicyLLM(stuck), tools, workspace=ws, max_turns=4).run("ciclo")
        show(result)
        note("Senza max_turns questo girerebbe fino all'arrivo della fattura.")

        section("SCENARIO 4 — un hook nega un'azione")
        hooks = HookBus()
        hooks.on(PRE_TOOL, lambda p: HookResult(False, "scritture disabilitate in questa sessione"), name="no-writes")
        llm = ScriptedLLM(
            Message("assistant", "Scrivo un file.", [ToolCall("c1", "write_file", {"path": "new.py", "content": "x"})]),
            "Capito — qui non posso scrivere.",
        )
        result = Agent(llm, tools, workspace=ws, hooks=hooks, max_turns=5).run("crea new.py")
        show(result)
        note("Il rifiuto è un messaggio, non un crash. Il modello può scegliere un'altra strada.")

        section("COSA NOTARE")
        note("Un'esecuzione è completa solo quando una risposta non ha chiamate agli strumenti.")
        note("Errori degli strumenti e rifiuti rientrano nel ciclo come testo.")
        note("max_turns è la differenza tra una sessione brutta e una costosa.")


if __name__ == "__main__":
    main()
