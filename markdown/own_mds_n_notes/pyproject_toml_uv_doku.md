Hier ist eine **praxisnahe Workflow-Doku** für Python-Projekte mit **uv**, `pyproject.toml` und sinnvoller Projektstruktur – so, wie man es heute sauber macht.

---

# 🐍 Python Projekt Workflow mit `uv`

## 🧭 Ziel des Setups

Du bekommst:

* saubere Projektstruktur
* reproduzierbare Dependencies
* kein `pip/venv` Chaos
* schnelle Umgebung mit `uv`

---

# 📁 1. Projektstruktur (Standard)

Empfohlenes Layout:

```text id="struct1"
mein-projekt/
├── pyproject.toml
├── uv.lock
├── .venv/
├── src/
│   └── mein_projekt/
│       ├── __init__.py
│       └── main.py
├── tests/
└── README.md
```

---

## 🧠 Warum `src/`?

👉 verhindert Import-Probleme
👉 trennt Code vom Projekt-Root
👉 Standard in professionellen Python-Projekten

---

# ⚙️ 2. Projekt initialisieren

Im leeren Ordner:

```bash id="init1"
uv init
```

👉 erstellt:

* `pyproject.toml`
* Grundstruktur

---

# 📄 3. pyproject.toml (Zentrale Konfiguration)

Minimal & modern:

```toml id="toml1"
[project]
name = "mein-projekt"
version = "0.1.0"
description = "Mein erstes uv Projekt"
requires-python = ">=3.10"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mein_projekt"]
```

---

## 🧠 Erklärung

### `[project]`

* Name
* Version
* Dependencies (z. B. requests, fastapi)

---

### `[build-system]`

* nutzt **Hatchling**
* Standard für moderne Python Builds

---

### `[tool.hatch.*]`

* sagt, **welcher Code ins Package kommt**
* wichtig für `src/` Layout

---

# 📦 4. Dependencies verwalten

## Paket hinzufügen

```bash id="add1"
uv add requests
```

---

## Paket entfernen

```bash id="rm1"
uv remove requests
```

---

## Alles installieren / syncen

```bash id="sync1"
uv sync
```

👉 erstellt automatisch `.venv/`

---

# 🐍 5. Virtuelle Umgebung

`uv` erstellt automatisch:

```text id="venv1"
.venv/
```

👉 enthält normalen Python Interpreter

Starten musst du NICHT manuell

---

# ▶️ 6. Code ausführen

```bash id="run1"
uv run python src/mein_projekt/main.py
```

oder direkt:

```bash id="run2"
uv run main.py
```

---

# 🧪 7. Beispiel Code

```python id="code1"
def main():
    print("Hallo uv!")

if __name__ == "__main__":
    main()
```

---

# 🔁 8. Typischer Workflow

## 🟢 Neues Projekt

```bash id="wf1"
uv init
uv add requests
uv sync
```

---

## 🟡 Arbeiten

```bash id="wf2"
uv run python src/mein_projekt/main.py
```

---

## 🔴 Reset (wenn kaputt)

```bash id="wf3"
rm -rf .venv uv.lock
uv sync
```

---

# 🧠 9. Best Practices

✔ immer `uv add` statt pip
✔ `src/` Struktur nutzen
✔ `uv.lock` committen
✔ `.venv/` ignorieren (Git)

---

# 🚀 10. Vorteile von uv

* ⚡ extrem schnell
* 🔒 reproduzierbare Builds
* 📦 kein pip/venv Chaos
* 🧩 ein Tool für alles

---

# 🧾 Fazit

Mit `uv` bekommst du:

> Ein modernes Python-Projekt-System ohne Setup-Schmerz.

---

Wenn du willst, kann ich dir als nächsten Schritt eine **perfekte Data-Engineering-Projektstruktur (inkl. Docker + notebooks + uv + tests)** bauen – genau wie in echten Jobs verwendet wird 👍
