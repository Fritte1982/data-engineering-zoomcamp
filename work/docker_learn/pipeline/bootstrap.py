import sys
from pathlib import Path

def find_project_root(
    priority_markers=("pyproject.toml", "uv.lock", ".git", "setup.py"),
    fallback_markers=(".venv", "venv", "requirements.txt"),
) -> Path:
    current = Path(__file__).resolve().parent
    dirs = [current, *current.parents]

    # Erst nach den zuverlässigen Markern suchen
    for directory in dirs:
        if any((directory / marker).exists() for marker in priority_markers):
            return directory

    # Erst wenn nichts gefunden wurde, Fallback-Marker probieren
    for directory in dirs:
        if any((directory / marker).exists() for marker in fallback_markers):
            return directory

    raise RuntimeError("Projekt-Root nicht gefunden.")

PROJECT_ROOT = find_project_root()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from work.docker_learn import bootstrap  # jetzt funktioniert's