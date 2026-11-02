"""Laboratorio 01 — Token e budget di contesto.

Esegui: python3 labs/L01_tokens.py

Obiettivo: costruire intuizione su quanto in fretta si riempie un contesto, e
vedere un budget rifiutare e troncare una trascrizione.
"""

from __future__ import annotations

import json

from _helpers import ROOT, note, section

from mini_agent.context import ContextBudget, estimate_tokens, transcript_tokens
from mini_agent.llm import ScriptedLLM
from mini_agent.messages import Message

PROSE = (
    "Un agente è un modello linguistico in un ciclo con strumenti dentro un "
    "ambiente. L'harness possiede la trascrizione, il budget e i guardrail. "
) * 20


def main() -> None:
    section("1. CARATTERI PER TOKEN, PER TIPO DI CONTENUTO")
    samples = {
        "prosa": PROSE,
        "python": (ROOT / "mini_agent" / "agent.py").read_text(),
        "json (schemi strumenti)": json.dumps([{"name": "read_file", "description": "Legge un file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}}]),
    }
    for label, text in samples.items():
        tokens = estimate_tokens(text)
        print(f"  {label:<24} {len(text):>7} caratteri  {tokens:>7} token  {len(text) / tokens:>5.2f} car/token")

    note("Codice e JSON sono più densi della prosa. I budget si spendono più in fretta di quanto pensi.")

    section("2. QUANTO COSTA UN TURNO")
    system = Message("system", "Sei un agente di coding. " * 60)
    tool_result = Message("tool", "def parse_date(s):\n    return ...\n" * 300, tool_call_id="c1", name="read_file")
    print(f"  system prompt : {transcript_tokens([system]):>6} token")
    print(f"  una lettura   : {transcript_tokens([tool_result]):>6} token")
    note("Un file da 300 righe è qualche migliaio di token. Venti così sono una sessione.")

    section("3. UNA TRASCRIZIONE CHE NON ENTRA")
    messages = [Message("system", "Sei un agente di coding.")]
    for i in range(12):
        messages.append(Message("user", f"compito {i}: " + "esplora la repo " * 40))
        messages.append(Message("assistant", "sto lavorando " * 80))
    before = transcript_tokens(messages)
    budget = ContextBudget(max_tokens=2_000, reserve=400)
    print(f"  budget        : {budget.max_tokens} (utilizzabile {budget.usable})")
    print(f"  prima         : {before} token, entra={budget.fits(messages)}")

    trimmed = budget.enforce(messages)
    after = transcript_tokens(trimmed)
    print(f"  dopo il taglio: {after} token, entra={budget.fits(trimmed)}")
    print(f"  messaggi      : {len(messages)} -> {len(trimmed)}")
    note(f"ruolo del primo messaggio tenuto: {trimmed[1].role!r} (mai 'tool' — orfanerebbe una chiamata)")

    section("4. COMPRESSIONE INVECE DEL TAGLIO")
    from mini_agent.context import summarize_naive

    compacted = budget.enforce(messages, compact=summarize_naive)
    print(f"  compresso     : {transcript_tokens(compacted)} token")
    for message in compacted[:2]:
        print(f"  [{message.role}] {message.content[:220]}")
    note("Il riassunto tiene cosa è stato chiesto e quali strumenti hanno girato.")
    note("Perde il contenuto esatto dei file e i motivi per cui le ipotesi sono state scartate.")

    section("5. LA CURVA DEI COSTI")
    note("Ogni turno reinvia l'intera trascrizione, che è cresciuta nel turno precedente.")
    for turns in (5, 10, 20, 40):
        avg = 1_500 + turns * 400
        total = sum(avg for _ in range(turns))
        print(f"  {turns:>2} turni, ~{avg:>5} token/turno -> ~{total:>7} token inviati in totale")
    note("Quasi quadratico. Tre sessioni da 10 turni costano molto meno di una da 30.")


if __name__ == "__main__":
    # Import tenuto in alto per i lettori; usato nella sezione 4.
    _ = ScriptedLLM
    main()
