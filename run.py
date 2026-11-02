#!/usr/bin/env python3
"""Runner del corso — funziona senza make.

    python3 run.py test       esegue la suite di test unitari
    python3 run.py labs       esegue ogni script di laboratorio in ordine
    python3 run.py demo       esegue l'agente su questa repo
    python3 run.py capstone   esegue le eval del capstone
    python3 run.py lint       controllo di compilazione di ogni file Python
    python3 run.py clean      rimuove le cache e l'output temporaneo
"""

from __future__ import annotations

import compileall
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable


def test() -> int:
    return subprocess.call([PY, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"], cwd=ROOT)


def labs() -> int:
    scripts = sorted((ROOT / "labs").glob("L*.py"))
    if not scripts:
        print("nessun laboratorio trovato")
        return 1
    for script in scripts:
        print(f"\n── {script.relative_to(ROOT)}")
        code = subprocess.call([PY, str(script)], cwd=ROOT)
        if code != 0:
            print(f"laboratorio fallito: {script} (exit {code})")
            return code
    print(f"\ntutti i {len(scripts)} laboratori passati")
    return 0


def demo() -> int:
    return subprocess.call(
        [PY, "-m", "mini_agent", "elenca i file di questa repo", "--audit", ""], cwd=ROOT
    )


def capstone() -> int:
    return subprocess.call([PY, "-m", "capstone.repo_doctor", "--eval"], cwd=ROOT)


def lint() -> int:
    ok = True
    for folder in ("mini_agent", "labs", "capstone", "tests"):
        target = ROOT / folder
        if target.exists():
            ok = compileall.compile_dir(str(target), quiet=1) and ok
    print("compilazione ok" if ok else "compilazione fallita")
    return 0 if ok else 1


def clean() -> int:
    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)
    for name in (".mini_agent", "sandbox", ".pytest_cache"):
        shutil.rmtree(ROOT / name, ignore_errors=True)
    print("pulito")
    return 0


COMMANDS = {
    "test": test,
    "labs": labs,
    "demo": demo,
    "capstone": capstone,
    "lint": lint,
    "clean": clean,
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print(__doc__)
        return 0
    command = COMMANDS.get(argv[0])
    if command is None:
        print(f"comando sconosciuto: {argv[0]}\n")
        print(__doc__)
        return 2
    return command()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
