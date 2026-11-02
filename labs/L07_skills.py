"""Laboratorio 07 — Skill e divulgazione progressiva.

Esegui: python3 labs/L07_skills.py

Obiettivo: misurare il costo di N skill a ogni livello di divulgazione e vedere
come la descrizione decida se una skill si carica.
"""

from __future__ import annotations

from pathlib import Path

from _helpers import note, section, temp_ws

from mini_agent.context import estimate_tokens
from mini_agent.skills import SkillLibrary

SKILLS = {
    "release-notes": (
        "Scrive le note di rilascio dalla cronologia git. Usala quando ti viene "
        "chiesto di preparare una release, un changelog o 'cosa è cambiato da vX'.",
        """\
# Note di rilascio

1. Ottieni l'intervallo: `git log --oneline <ultimo-tag>..HEAD`.
2. Raggruppa: funzionalità, correzioni, breaking change, manutenzione.
3. Scarta i merge commit e i bump di versione.
4. Segui `template.md`. Voci sotto i 100 caratteri.
5. Se c'è un breaking change, mettilo per primo e marcalo **BREAKING**.
""",
    ),
    "db-migration": (
        "Crea e rivedi una migrazione del database. Usala quando serve una "
        "modifica allo schema o quando ti viene chiesto di alembic.",
        """\
# Migrazione del database

1. Genera: `python3 skills/db-migration/new_migration.py <nome>`.
2. Non scrivere a mano l'id di revisione; il formato del timestamp conta.
3. Aggiungi un percorso di downgrade. Se è irreversibile, dillo nella docstring.
4. Esegui `make test` — la suite azzera il DB a ogni test.
""",
    ),
    "incident-runbook": (
        "Gestisci un incidente in produzione: valuta il raggio d'impatto, mitiga, "
        "poi scrivi la cronologia. Usala quando vieni paginato o ti chiedono di un guasto.",
        """\
# Runbook degli incidenti

1. Dichiara la gravità e apri un canale per l'incidente.
2. Prima mitiga (rollback, feature flag), poi diagnostica.
3. Registra i timestamp mentre vai; la cronologia è il deliverable.
4. Post-incidente: revisione senza colpe entro 48h.
""",
    ),
}


def build(root: Path) -> None:
    for name, (description, body) in SKILLS.items():
        folder = root / "skills" / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n---\n\n{body}")
    (root / "skills" / "release-notes" / "template.md").write_text("# vX.Y.Z\n\n## Funzionalità\n- \n")


def main() -> None:
    with temp_ws("skills") as tmp:
        root = Path(tmp)
        build(root)
        library = SkillLibrary.discover(root / "skills")

        section("1. IL CATALOGO (L1)")
        catalog = library.catalog()
        print(catalog)
        print(f"\n  {len(library)} skill, catalogo = {estimate_tokens(catalog)} token")
        note("Questo sta nel system prompt, sempre, per ogni skill che possiedi.")

        section("2. IL COSTO DI CARICARE TUTTO (L2)")
        everything = "\n\n".join(library.load(name) for name in library.skills)
        print(f"  tutti i corpi   = {estimate_tokens(everything):>5} token")
        print(f"  solo catalogo   = {estimate_tokens(catalog):>5} token")
        print(f"  rapporto        = {estimate_tokens(everything) / estimate_tokens(catalog):.0f}x")
        note("Con 10–20 skill, caricare tutti i corpi consumerebbe l'intero budget.")

        section("3. CARICANE UNA (L2)")
        print(library.load("db-migration")[:400])

        section("4. LEGGI UNA RISORSA (L3)")
        print(library.skills["release-notes"].read_resource("template.md"))

        section("5. LA DESCRIZIONE È L'INNESCO")
        tasks = [
            "prepara il changelog per la v2.1",
            "serve una nuova colonna su users",
            "il sito è giù, paginato alle 03:12",
            "rifattorizza il modulo checkout",
        ]
        for task in tasks:
            matches = library.match(task)
            chosen = matches[0].name if matches else "(nessuna)"
            print(f"  {task!r:<46} -> {chosen}")

        section("6. QUANDO LE DESCRIZIONI VANNO MALE")
        from mini_agent.skills import Skill

        bad = SkillLibrary([
            Skill(name="helper", description="Aiuta con le cose", body="…", path=root)
        ])
        for task in tasks:
            matches = bad.match(task)
            print(f"  {task!r:<46} -> {matches[0].name if matches else '(non si carica mai)'}")
        note("Una descrizione vaga è una skill che non si carica mai. Peso morto.")

        section("7. SKILL VS STRUMENTO VS ISTRUZIONE")
        note("istruzione: un vincolo, sempre caricato  ('esegui make test')")
        note("skill      : una procedura, caricata su richiesta ('come scrivere una migrazione')")
        note("strumento : un'azione, schema sempre, risultato alla chiamata ('read_file')")


if __name__ == "__main__":
    main()
