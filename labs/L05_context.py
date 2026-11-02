"""Laboratorio 05 — Ingegneria del contesto: budget, taglio, compressione.

Esegui: python3 labs/L05_context.py

Obiettivo: vedere una trascrizione andare in overflow, capire cosa tiene il
taglio e vedere esattamente cosa perde la compressione.
"""

from __future__ import annotations

from _helpers import note, section

from mini_agent.context import (
    ContextBudget,
    estimate_tokens,
    summarize_naive,
    transcript_tokens,
)
from mini_agent.messages import Message, ToolCall


def build() -> list[Message]:
    messages = [Message("system", "Sei un agente di coding. " * 40)]
    messages.append(Message("user", "Correggi il crash su data vuota. Non cambiare la firma."))
    for i in range(8):
        messages.append(
            Message("assistant", f"Esploro l'ipotesi {i}. " + "ragionamento " * 60,
                    [ToolCall(f"c{i}", "read_file", {"path": f"src/module_{i}.py"})])
        )
        messages.append(
            Message("tool", f"# module_{i}.py\n" + "def f():\n    pass\n" * 80,
                    tool_call_id=f"c{i}", name="read_file")
        )
        messages.append(Message("assistant", f"Ipotesi {i} scartata: il bug non è qui. " * 20))
    messages.append(Message("user", "Promemoria: il test si aspetta ValueError, non None."))
    return messages


def main() -> None:
    messages = build()
    total = transcript_tokens(messages)

    section("1. RENDICONTAZIONE")
    parts = {
        "system prompt": [m for m in messages if m.role == "system"],
        "messaggi utente": [m for m in messages if m.role == "user"],
        "testo assistente": [m for m in messages if m.role == "assistant"],
        "risultati tool": [m for m in messages if m.role == "tool"],
    }
    for label, subset in parts.items():
        print(f"  {label:<18} {transcript_tokens(subset):>6} token")
    print(f"  {'TOTALE':<18} {total:>6} token")
    note("Dominano i risultati degli strumenti. Nelle sessioni vere è quasi sempre così.")

    section("2. UN BUDGET CHE NON ENTRA")
    budget = ContextBudget(max_tokens=4_000, reserve=800)
    print(f"  finestra={budget.max_tokens} riserva={budget.reserve} utilizzabile={budget.usable}")
    print(f"  trascrizione={total} entra={budget.fits(messages)}")
    note(f"uso: {budget.usage(messages):.0%} del budget utilizzabile")

    section("3. TAGLIO AI CONFINI DEL TURNO")
    trimmed = budget.enforce(messages)
    print(f"  messaggi {len(messages)} -> {len(trimmed)}, token {total} -> {transcript_tokens(trimmed)}")
    print(f"  primo tenuto: [{trimmed[1].role}] {trimmed[1].content[:100]}")
    print(f"  ultimo tenuto: [{trimmed[-1].role}] {trimmed[-1].content[:100]}")
    note("Il taglio elimina turni interi. Un risultato non sopravvive mai senza la sua chiamata.")

    section("4. COSA HA PERSO IL TAGLIO")
    kept_text = " ".join(m.content for m in trimmed)
    for probe in ("Non cambiare la firma", "ipotesi 0", "ipotesi 5"):
        print(f"  {'tenuto' if probe in kept_text else 'PERSO':<7} {probe!r}")
    note("Il vincolo originale potrebbe essere sparito. Ecco perché sta nel system prompt.")

    section("5. COMPRESSIONE INVECE")
    compacted = budget.enforce(messages, compact=summarize_naive)
    print(f"  token {total} -> {transcript_tokens(compacted)}")
    summary = next(m for m in compacted if "compacted" in m.content)
    print("  riassunto:")
    for line in summary.content.splitlines()[:8]:
        print("   ", line)
    note("Tenuto: cosa è stato chiesto, quali strumenti hanno girato. Perso: contenuti, motivi.")

    section("6. IL COMPROMESSO")
    note("Taglio: economico, nessuna chiamata extra, perde dettagli in silenzio.")
    note("Compressione: una chiamata extra, tiene la forma, perde comunque dettagli — ma lo dice.")
    note("Entrambi sono peggio del non andare in overflow. Cerca in modo mirato; leggi intervalli.")

    section("7. STABILITÀ DEL PREFISSO (CACHING)")
    base = [Message("system", "Sei un agente di coding. " * 200), Message("user", "compito")]
    extended = base + [Message("assistant", "sto lavorando " * 100)]
    print(f"  token del prefisso        : {transcript_tokens(base)}")
    print(f"  dopo aver accodato un turno: {transcript_tokens(extended)}")
    note("Il prefisso è identico byte per byte, quindi un provider può cacharlo.")
    note("Riscrivere il system prompt a ogni turno invalida la cache e costa a prezzo pieno.")


if __name__ == "__main__":
    main()
