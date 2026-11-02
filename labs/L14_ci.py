"""Laboratorio 14 — CI headless: budget, revisione in sola lettura e report.

Esegui: python3 labs/L14_ci.py

Obiettivo: eseguire l'harness come farebbe la CI — nessun umano, limiti rigidi,
output leggibile dalla macchina — poi vedere il livello dei permessi rifiutare
un push.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from _helpers import note, section, temp_ws

from mini_agent import Agent, Message, ToolCall, Workspace, make_fs_tools, tool
from mini_agent.context import ContextBudget
from mini_agent.hooks import PRE_TOOL, HookBus, HookResult
from mini_agent.llm import PolicyLLM


@dataclass
class JobResult:
    ok: bool
    report: dict
    turns: int
    tokens: int
    stopped: str


def review_policy(messages, tools):
    """Un sostituto deterministico di un modello revisore."""
    last = messages[-1]
    if last.role == "tool":
        findings = []
        if "eval(" in last.content:
            findings.append({"severity": "high", "file": "src/unsafe.py", "line": 2, "issue": "eval su input"})
        return Message("assistant", json.dumps({"findings": findings, "summary": "revisione completata"}))
    return Message("assistant", "Leggo il file rischioso.", [
        ToolCall("c1", "read_file", {"path": "src/unsafe.py"})
    ])


def run_ci_job(ws: Workspace, max_turns: int = 6, budget_tokens: int = 8_000) -> JobResult:
    agent = Agent(
        PolicyLLM(review_policy),
        make_fs_tools(ws),
        workspace=ws,
        budget=ContextBudget(max_tokens=budget_tokens),
        max_turns=max_turns,
    )
    result = agent.run("rivedi src/unsafe.py e restituisci i risultati in JSON")
    try:
        report = json.loads(result.final)
    except json.JSONDecodeError:
        report = {"findings": [], "summary": result.final, "parse_error": True}
    return JobResult(result.ok, report, result.turns, result.tokens, result.stopped_reason)


def main() -> None:
    with temp_ws("ci") as tmp:
        ws = Workspace(tmp)
        ws.write("src/unsafe.py", "def run(x):\n    return eval(x)\n")
        ws.write("src/app.py", "def main():\n    return 0\n")

        section("1. JOB DI REVISIONE IN SOLA LETTURA")
        job = run_ci_job(ws)
        print(json.dumps(
            {"ok": job.ok, "turns": job.turns, "tokens": job.tokens, "stopped": job.stopped},
            indent=2,
        ))
        print(json.dumps(job.report, indent=2))
        note("L'output leggibile dalla macchina è il deliverable. La prosa è per gli umani.")

        section("2. LIMITI RIGIDI")
        tiny = run_ci_job(ws, max_turns=1)
        print(f"  max_turns=1 -> stop={tiny.stopped} turni={tiny.turns}")
        note("Un job limitato fallisce in modo pulito invece di bruciare il budget della CI.")
        note("Limiti di budget e turni sono configurazione, non suggerimenti.")

        section("3. IL REVISORE NON DEVE SCRIVERE")
        read_only_ws = Workspace(tmp, read_only=True)
        @tool(side_effect=True, needs_permission=True)
        def write_file_attempt(path: str, content: str) -> str:
            """Una scrittura che non dovrebbe mai essere raggiungibile in revisione."""
            return read_only_ws.write(path, content)

        agent = Agent(
            PolicyLLM(lambda m, t: Message("assistant", "provo", [
                ToolCall("c1", "write_file_attempt", {"path": "fixed.py", "content": "x"})
            ]) if m[-1].role != "tool" else Message("assistant", "negato, mi fermo")),
            [write_file_attempt],
            workspace=read_only_ws,
            max_turns=3,
        )
        result = agent.run("correggi il risultato")
        print(f"  trascrizione: {[m.text()[:60] for m in result.messages[1:]]}")
        note("La modalità sola lettura è imposta dal workspace, non dal prompt.")

        section("4. MODALITÀ SCRITTURA: IL PUSH VIENE NEGATO")
        hooks = HookBus()
        hooks.on(
            PRE_TOOL,
            lambda p: HookResult(False, "git push richiede approvazione umana")
            if p["tool"] == "run_shell" and "push" in str(p["arguments"])
            else None,
            name="no-push",
        )

        @tool(side_effect=True, needs_permission=True)
        def run_shell(command: str) -> str:
            """Esegue un comando shell."""
            return f"eseguito: {command}"

        agent = Agent(
            PolicyLLM(lambda m, t: Message("assistant", "faccio il push", [
                ToolCall("c1", "run_shell", {"command": "git push origin main"})
            ]) if m[-1].role != "tool" else Message("assistant", "push negato, mi fermo")),
            [run_shell],
            workspace=ws,
            hooks=hooks,
            max_turns=3,
        )
        result = agent.run("fai il push della correzione")
        print(f"  trascrizione: {[m.text()[:70] for m in result.messages[1:]]}")
        note("Le scritture vanno su un branch; i push richiedono un umano. Codificalo in un hook.")

        section("5. COSA AUTOMATIZZARE PRIMA")
        note("1. commenti di revisione sui diff (sola lettura)")
        note("2. triage delle issue / etichette")
        note("3. correzioni di lint e tipi (stretto, verificabile)")
        note("4. aggiornamento delle dipendenze (protetto dai test)")
        note("5. sviluppo di funzionalità (per ultimo, con un umano nel ciclo)")

        section("6. METRICHE CHE REGGONO IL CONFRONTO")
        note("tasso di accettazione, tasso di revert, tasso di modifiche umane")
        note("tempo di ciclo, costo per PR integrata, difetti sfuggiti")
        note("non: righe generate, sessioni avviate, tempo risparmiato autodichiarato")


if __name__ == "__main__":
    main()
