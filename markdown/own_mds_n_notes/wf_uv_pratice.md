Hier ist eine **kompakte, praxisnahe Doku für den Workflow mit `uv`** – von Init über Dependencies bis Ausführen 🚀
(ideal für tägliche Nutzung, z. B. Data Engineering Projekte)

---

# 🐍 Workflow mit uv

---

# 🧭 1. Projekt erstellen

## Mit bestimmter Python-Version

```bash
uv init --python=3.14
```

👉 Das passiert:

* Projekt wird initialisiert
* Python **3.14** wird genutzt (falls nötig installiert)
* `pyproject.toml` wird erzeugt

---

## 📄 Ergebnis: `pyproject.toml`

Typischer Inhalt:

```toml
[project]
name = "mein-projekt"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 🧠 Wichtig

👉 Der entscheidende Teil ist:

```toml
requires-python = ">=3.14"
```

→ `uv` weiß: **dieses Projekt braucht Python 3.14**

---

# 📦 2. Dependencies hinzufügen

```bash
uv add requests
```

👉 Ergebnis in `pyproject.toml`:

```toml
dependencies = [
    "requests"
]
```

---

## Mehrere Pakete

```bash
uv add pandas numpy
```

---

## Entfernen

```bash
uv remove requests
```

---

# 🔄 3. Umgebung synchronisieren

```bash
uv sync
```

👉 macht automatisch:

* `.venv/` erstellen
* alle Dependencies installieren
* `uv.lock` erzeugen

---

## 📁 Danach hast du:

```text
mein-projekt/
├── pyproject.toml
├── uv.lock
├── .venv/
```

---

# ▶️ 4. Code ausführen

## Standard

```bash
uv run python main.py
```

---

## Mit Argumenten

```bash
uv run python pipeline.py 10
```

---

## Shortcut (wenn Script direkt ist)

```bash
uv run pipeline.py
```

---

## 🧠 Was passiert intern?

`uv run`:

* nutzt `.venv`
* stellt sicher, dass alles installiert ist
* startet richtigen Interpreter

---

# 🐍 5. Python-Version verwalten

## Version installieren

```bash
uv python install 3.14
```

---

## Version im Projekt festlegen

```bash
uv python pin 3.14
```

👉 sorgt dafür, dass immer diese Version genutzt wird

---

# 🔁 6. Typischer Workflow

## 🟢 Neues Projekt

```bash
uv init --python=3.14
uv add requests pandas
uv sync
```

---

## 🟡 Arbeiten

```bash
uv run python main.py
```

---

## 🔴 Reset bei Problemen

```bash
rm -rf .venv uv.lock
uv sync
```

(PowerShell: `Remove-Item -Recurse -Force .venv, uv.lock`)

---

# 🧠 7. Best Practices

✔ immer `uv add` statt `pip install`
✔ `uv run` statt `python`
✔ `uv.lock` committen
✔ `.venv/` NICHT committen

---

# ⚠️ 8. Häufige Fehler

### ❌ `python script.py`

→ falsches Environment

### ❌ eigenes `venv` + uv mischen

→ Chaos

### ❌ `.venv` manuell aktivieren

→ unnötig

---

# 💡 9. Mental Model

👉 Mit `uv` arbeitest du so:

| Aufgabe            | Befehl    |
| ------------------ | --------- |
| Projekt erstellen  | `uv init` |
| Paket installieren | `uv add`  |
| alles installieren | `uv sync` |
| Code starten       | `uv run`  |

---

# 🧾 Fazit

Mit uv bekommst du:

* sauberes Python-Setup
* reproduzierbare Projekte
* weniger Fehler
* schnelleren Workflow ⚡

---

Wenn du willst, kann ich dir als nächsten Schritt zeigen:

👉 **uv + Docker + Data Engineering Pipeline Setup (realistisch wie im Job)**
