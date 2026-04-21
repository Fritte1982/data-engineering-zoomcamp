Hier ist eine **anfängerfreundliche Einführung zu Python mit `uv`** – kompakt, praxisnah und ohne unnötigen Ballast.

---

# 🐍 Python mit uv – Einsteiger-Guide

## 📌 Was ist `uv` überhaupt?

`uv` ist ein modernes Tool für Python, das mehrere Dinge gleichzeitig ersetzt:

* Paketmanager (wie `pip`)
* Virtual Environments (wie `venv`)
* Projektmanager (ähnlich wie Poetry)

👉 Ziel: **Python-Projekte einfacher, schneller und sauberer verwalten**

---

## 🚀 Installation

### Linux / macOS

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Danach prüfen:

```bash
uv --version
```

---

## 📁 Neues Projekt erstellen

```bash
uv init mein-projekt
cd mein-projekt
```

👉 Das erzeugt u.a.:

* `pyproject.toml` (Projekt-Konfiguration)
* `.venv/` (virtuelle Umgebung)

---

## ▶️ Python-Code ausführen

```bash
uv run main.py
```

👉 `uv` kümmert sich automatisch um:

* virtuelle Umgebung
* richtige Python-Version

---

## 📦 Pakete installieren

```bash
uv add requests
```

👉 Beispiel: HTTP-Bibliothek **Requests**

Das passiert dabei:

* Paket wird installiert
* in `pyproject.toml` eingetragen

---

## 🔄 Pakete entfernen

```bash
uv remove requests
```

---

## 📜 Abhängigkeiten synchronisieren

Wenn du ein Projekt klonst:

```bash
uv sync
```

👉 Installiert alles aus der Konfiguration

---

## 🧪 Virtuelle Umgebung (automatisch!)

Normalerweise mit Python:

* `python -m venv`
* `source venv/bin/activate`

👉 Mit `uv` brauchst du das **nicht mehr manuell**

---

## 🐍 Python-Version festlegen

```bash
uv python install 3.12
uv python pin 3.12
```

👉 Projekt nutzt dann genau diese Version

---

## 📂 Beispielprojekt

### main.py

```python id="exv0ap"
import requests

r = requests.get("https://api.github.com")
print(r.status_code)
```

### Ausführen

```bash
uv run main.py
```

---

## 🔁 Vergleich klassisch vs. uv

| Aufgabe        | Klassisch (`pip`) | mit `uv`    |
| -------------- | ----------------- | ----------- |
| venv erstellen | `python -m venv`  | automatisch |
| aktivieren     | `source ...`      | entfällt    |
| installieren   | `pip install`     | `uv add`    |
| ausführen      | `python`          | `uv run`    |

---

## 💡 Best Practices

* Immer `uv add` statt `pip install`
* Projektordner sauber halten
* `pyproject.toml` versionieren (Git!)

---

## 🧾 Fazit

👉 `uv` macht Python deutlich einfacher für Anfänger:

* weniger Setup
* weniger Fehler
* schnellere Workflows

---

Wenn du willst, kann ich dir als nächsten Schritt zeigen:

* wie du ein kleines Web-API baust (z.B. mit FastAPI)
* oder ein reales Mini-Projekt mit `uv` Schritt für Schritt 👨‍💻
