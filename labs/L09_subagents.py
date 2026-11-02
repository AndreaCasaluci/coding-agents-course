"""Laboratorio 09 — Subagenti: isolamento, costo e race di scrittura.

Esegui: python3 labs/L09_subagents.py

Obiettivo: vedere cosa compra un subagente e cosa costa, poi riprodurre la
classica corruzione da scrittura parallela.
"""

from __future__ import annotations

from _helpers import note, section, temp_ws

from mini_agent import Agent, Message, Workspace, make_fs_tools, run_parallel
from mini_agent.context import transcript_tokens
from mini_agent.llm import PolicyLLM

COUNTER = """\
count = 0

def increment():
    global count
    count += 1
    return count
"""


def main() -> None:
    with temp_ws("subagents") as tmp:
        ws = Workspace(tmp)
        ws.write("src/counter.py", COUNTER)
        ws.write("src/auth.py", "def login(user):\n    return user\n")

        seen: list[str] = []
        seen_roles: list[list[str]] = []

        # Un modello senza stato che fa da sostituto. I figli veri hanno le
        # proprie chiamate al modello.
        def policy(messages, tools):
            task = messages[-1].content
            seen.append(task)
            seen_roles.append([m.role for m in messages])
            if "sicurezza" in task:
                return Message("assistant", "Risultati: src/auth.py:1 login() accetta qualsiasi utente. Nient'altro.")
            if "test" in task:
                return Message("assistant", "Non ci sono file di test in questa repo.")
            return Message("assistant", "ok")

        parent = Agent(PolicyLLM(policy), make_fs_tools(ws), workspace=ws)

        section("1. ESPANDI (SOLA LETTURA)")
        jobs = {
            "security": "analisi di sicurezza: trova problemi di auth. Riporta file:riga. Non modificare.",
            "tests": "analisi dei test: elenca i moduli non testati. Non modificare.",
        }
        results = run_parallel(parent, jobs)

        for name, result in results.items():
            print(f"  [{name}] turni={result.turns} token={result.tokens}")
            print(f"           {result.summary}")

        section("2. COSA TIENE IL PADRE")
        print(f"  compiti visti dal modello: {len(seen)}")
        print(f"  riassunti tenuti dal padre: {sum(len(r.summary) for r in results.values())} caratteri")
        print(f"  token in quei riassunti   : {transcript_tokens([Message('user', r.summary) for r in results.values()])}")
        note("Il padre non vede mai la trascrizione del figlio. È il punto.")
        note("E il costo: non può verificare nulla che il figlio non abbia citato.")

        section("3. IL CONTESTO DEL FIGLIO È PULITO")
        # Ogni figlio è partito da system + user; nessuna cronologia del padre.
        print(f"  ruoli visti dal modello, per chiamata del figlio: {seen_roles[:2]}")
        note("Due messaggi: system + il compito. Nessuna cronologia, nessun turno precedente.")
        note("Un figlio non può fare domande di chiarimento. Il suo compito deve essere autosufficiente.")

        section("4. LA RACE DI SCRITTURA")
        ws.write("src/counter.py", COUNTER)
        a_read = ws.read("src/counter.py")   # l'agente A legge v1
        b_read = ws.read("src/counter.py")   # l'agente B legge v1

        ws.write("src/counter.py", a_read + "\n# modifica di A\n")
        ws.write("src/counter.py", b_read + "\n# modifica di B\n")

        final = ws.read("src/counter.py")
        print(f"  modifica di A presente? {'modifica di A' in final}")
        print(f"  modifica di B presente? {'modifica di B' in final}")
        note("B ha scritto una copia obsoleta. Il lavoro di A è sparito, in silenzio.")

        section("5. SCRITTURE SERIALIZZATE")
        ws.write("src/counter.py", COUNTER)
        # A scrive, poi B rilegge prima di scrivere.
        ws.write("src/counter.py", ws.read("src/counter.py") + "\n# modifica di A\n")
        ws.write("src/counter.py", ws.read("src/counter.py") + "\n# modifica di B\n")
        final = ws.read("src/counter.py")
        print(f"  modifica di A presente? {'modifica di A' in final}")
        print(f"  modifica di B presente? {'modifica di B' in final}")
        note("Serializza le scritture, oppure dai a ogni worker il proprio worktree e fai il merge.")

        section("6. IL PATTERN DELLA REVISIONE")
        note("l'implementatore scrive un diff")
        note("il revisore lo legge a freddo (contesto pulito, sola lettura) e cita file:riga")
        note("l'implementatore affronta i risultati")
        note("Il valore del revisore è non sapere perché la modifica è stata fatta.")

        section("7. QUANDO NON DELEGARE")
        note("Il padre ha bisogno delle prove grezze (diff, output dei test) -> tieni inline.")
        note("Il compito richiede stato condiviso ed evolutivo -> tieni inline.")
        note("Il sotto-compito è una funzione -> la delega costa più di quanto risparmia.")


if __name__ == "__main__":
    main()
