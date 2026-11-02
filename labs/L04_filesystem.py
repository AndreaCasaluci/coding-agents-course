"""Laboratorio 04 — Il filesystem: prigioni, ancore e obsolescenza.

Esegui: python3 labs/L04_filesystem.py

Obiettivo: riprodurre le evasioni di percorso e i bug da copia obsoleta che
danneggiano le repo vere.
"""

from __future__ import annotations

from _helpers import note, section, temp_ws

from mini_agent import Workspace, WorkspaceError

ORIGINAL = """\
def parse_date(s):
    return datetime.strptime(s, FMT)
"""


def main() -> None:
    with temp_ws("fs") as tmp:
        ws = Workspace(tmp)
        ws.write("src/dates.py", ORIGINAL)

        section("1. LA PRIGIONE DEI PERCORSI")
        for path in ("src/dates.py", "../outside.txt", "/etc/passwd", "src/../../escape.txt"):
            try:
                resolved = ws.resolve(path)
                print(f"  CONSENTITO {path!r:<24} -> {resolved}")
            except WorkspaceError as exc:
                print(f"  BLOCCATO   {path!r:<24} -> {exc}")

        section("2. I SYMLINK VENGONO SEGUITI PRIMA DEL CONTROLLO")
        outside = ws.root.parent / "outside-secret.txt"
        outside.write_text("segreto dell'host")
        (ws.root / "link").symlink_to(outside)
        try:
            ws.read("link")
            print("  CONSENTITO (male)")
        except WorkspaceError as exc:
            print(f"  BLOCCATO   'link' -> {exc}")
        note("resolve() segue il symlink, quindi il contenimento è verificato sul percorso reale.")
        note("Questo è un confine di correttezza, non di sicurezza (modulo 12).")

        section("3. MODIFICA CON ANCORA UNICA")
        ws.write("src/dates.py", "a\nb\nb\n")
        try:
            ws.edit("src/dates.py", "b", "c")
        except WorkspaceError as exc:
            print(f"  AMBIGUO -> {exc}")
        note("Due corrispondenze: l'harness rifiuta invece di indovinare quale.")
        ws.edit("src/dates.py", "b\nb", "b\nc")
        print("  dopo la modifica unica:", ws.read("src/dates.py").split())

        section("4. IL TRONCAMENTO VIENE ANNUNCIATO")
        ws.write("big.log", "riga di log\n" * 5_000)
        out = ws.read("big.log")
        print(f"  restituiti {len(out)} caratteri")
        print("  " + out.splitlines()[-1])
        note("Senza il marcatore il modello crede di aver letto tutto il file.")

        section("5. IL BUG DELLA COPIA OBSOLETA")
        ws.write("src/dates.py", ORIGINAL)
        stale_copy = ws.read("src/dates.py")          # il modello legge v1
        ws.write("src/dates.py", ORIGINAL + "\ndef helper():\n    return 42\n")  # l'utente modifica a v2

        print("  il disco ora ha un helper che il modello non ha visto.")
        ws.write("src/dates.py", stale_copy.replace("return datetime", "if not s:\n        raise ValueError()\n    return datetime"))
        print("  dopo write_file(copia_obsoleta):")
        print("   ", "helper presente?", "def helper" in ws.read("src/dates.py"))
        note("La riscrittura ha distrutto in silenzio la modifica dell'utente. Raggio d'impatto: il file.")

        section("6. LO STESSO ERRORE CON UNA MODIFICA")
        ws.write("src/dates.py", ORIGINAL)
        ws.write("src/dates.py", ORIGINAL + "\ndef helper():\n    return 42\n")
        try:
            ws.edit("src/dates.py", "return datetime.strptime(s, FMT)", "if not s:\n        raise ValueError()\n    return datetime.strptime(s, FMT)")
            print("  modifica applicata; helper presente?", "def helper" in ws.read("src/dates.py"))
        except WorkspaceError as exc:
            print(f"  la modifica è fallita rumorosamente -> {exc}")

        section("7. RIPROVA, CORRETTAMENTE")
        ws.write("src/dates.py", ORIGINAL + "\ndef helper():\n    return 42\n")
        ws.edit("src/dates.py", "def parse_date(s):", "def parse_date(s):\n    if not s:\n        raise ValueError(\"data vuota\")")
        print(ws.read("src/dates.py"))
        note("Ancora piccola, raggio limitato, modifica dell'utente preservata.")


if __name__ == "__main__":
    main()
