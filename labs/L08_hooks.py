"""Laboratorio 08 — Hook: osserva, blocca, modifica, fallisci chiuso.

Esegui: python3 labs/L08_hooks.py

Obiettivo: costruire un bus di hook, vedere un rifiuto e un oscuramento, e
vedere un guardrail che va in crash fallire chiuso.
"""

from __future__ import annotations

from _helpers import note, section, temp_ws

from mini_agent import Agent, Message, ToolCall, Workspace, make_fs_tools
from mini_agent.hooks import (
    POST_TOOL,
    PRE_EDIT,
    PRE_TOOL,
    HookBus,
    HookResult,
    deny_paths,
    redact_secrets,
)
from mini_agent.llm import ScriptedLLM


def main() -> None:
    bus = HookBus()

    section("1. OSSERVA")
    events: list[dict] = []
    bus.on(PRE_TOOL, lambda p: (events.append(dict(p)), None)[-1], name="collect")
    bus.emit(PRE_TOOL, {"tool": "read_file", "arguments": {"path": "src/a.py"}})
    bus.emit(PRE_TOOL, {"tool": "write_file", "arguments": {"path": "src/b.py"}})
    print(f"  registrati {len(events)} eventi")
    note("Gli hook di audit sono economici e rispondono dopo a 'cosa ha davvero chiamato?'.")

    section("2. BLOCCA")
    bus.on(PRE_EDIT, deny_paths((".env", ".git", "secrets")), name="protect-paths")
    for path in (".env", ".git/config", "secrets/prod.yaml", "src/app.py"):
        decision = bus.emit(PRE_EDIT, {"tool": "write_file", "path": path})
        print(f"  {path:<20} consentito={decision.allow!s:<5} {decision.reason}")

    section("3. MODIFICA (OSCURA)")
    bus.on(POST_TOOL, redact_secrets(), name="redact")
    dirty = "token=ghp_" + "a" * 24 + " e chiave=sk-" + "b" * 20
    decision = bus.emit(POST_TOOL, {"tool": "read_file", "content": dirty})
    print(f"  prima: {dirty}")
    print(f"  dopo : {decision.payload['content']}")
    note("La modifica cambia ciò che il modello crede di aver visto. Usala per oscurare, con parsimonia.")

    section("4. ORDINE E PRIMO RIFIUTO CHE VINCE")
    order: list[str] = []
    bus2 = HookBus()
    bus2.on(PRE_TOOL, lambda p: (order.append("primo"), None)[-1], name="primo")
    bus2.on(PRE_TOOL, lambda p: HookResult(False, "fermati qui"), name="secondo")
    bus2.on(PRE_TOOL, lambda p: (order.append("terzo"), None)[-1], name="terzo")
    result = bus2.emit(PRE_TOOL, {"tool": "rm_rf"})
    print(f"  eseguiti: {order}, consentito={result.allow}, motivo={result.reason}")
    note("Gli hook successivi non girano dopo un rifiuto.")

    section("5. FALLISCI CHIUSO")
    bus3 = HookBus()
    bus3.on(PRE_TOOL, lambda p: 1 / 0, name="guardrail-rotto")
    result = bus3.emit(PRE_TOOL, {"tool": "write_file"})
    print(f"  consentito={result.allow}, motivo={result.reason}")
    note("Un hook di sicurezza che va in crash nega. Un formatter rotto salta solo la formattazione.")

    section("6. UN'ESECUZIONE COMPLETA CON I GUARDRAIL")
    with temp_ws("hooks") as tmp:
        ws = Workspace(tmp)
        ws.write("src/app.py", "print('ciao')\n")
        bus4 = HookBus()
        bus4.on(PRE_EDIT, deny_paths((".env", ".git")), name="protect-paths")
        bus4.on(POST_TOOL, redact_secrets(), name="redact")

        llm = ScriptedLLM(
            Message("assistant", "Scrivo il file env.", [ToolCall("c1", "write_file", {"path": ".env", "content": "SECRET=1"})]),
            Message("assistant", "Leggo il log.", [ToolCall("c2", "read_file", {"path": "app.log"})]),
            "Bloccato il primo, oscurato il secondo.",
        )
        ws.write("app.log", "chiave=sk-" + "z" * 24 + "\n")
        agent = Agent(llm, make_fs_tools(ws), workspace=ws, hooks=bus4, max_turns=5)
        result = agent.run("scrivi .env poi leggi app.log")
        for message in result.messages[1:]:
            print("   " + message.text().replace("\n", "\n   ")[:200])

        print(f"\n  .env esiste? {ws.resolve('.env').exists()}")
        note("Il rifiuto è arrivato al modello come testo; la scrittura non è mai avvenuta.")
        note("Il segreto nel log è stato ripulito prima che il modello lo vedesse.")

    section("7. GLI HOOK SONO TESTABILI")
    guard = deny_paths((".env",))
    print(f"  nega .env       -> {guard({'path': '.env'}).allow}")
    print(f"  astieniti su src -> {guard({'path': 'src/app.py'})}")
    note("L'astensione (None) conta: un guardrail che restituisce True ingoia le modifiche successive.")


if __name__ == "__main__":
    main()
