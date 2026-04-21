Wenn du `uv init` mit uv ausführst, erzeugt es eine **sehr minimalistische `pyproject.toml`** nach modernem Python-Standard (PEP 517/518 + PEP 621).

---

## 📄 Typischer Inhalt nach `uv init`

```toml id="t8kq1m"
[project]
name = "mein-projekt"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.8"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 🧠 Was bedeutet das?

### 📦 `[project]`

Das ist dein eigentlicher Projektblock:

* `name` → Projektname
* `version` → Version deiner App
* `description` → Beschreibung (optional)
* `readme` → README Datei
* `requires-python` → minimale Python-Version
* `dependencies` → deine Pakete (z. B. requests, fastapi)

---

### ⚙️ `[build-system]`

Das sagt Tools wie `pip` oder `uv`, **wie das Projekt gebaut wird**:

```toml id="b8kq2n"
requires = ["hatchling"]
build-backend = "hatchling.build"
```

👉 Standard ist hier:

* **Hatchling**

---

## 📦 Beispiel mit echten Dependencies

Wenn du z. B. später installierst:

```bash id="p9v2lm"
uv add requests fastapi
```

Dann wird es so:

```toml id="k2m9xq"
[project]
name = "mein-projekt"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests",
    "fastapi"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 🧠 Wichtig zu verstehen

* `uv` schreibt **alles in diese eine Datei**
* kein `requirements.txt` mehr nötig
* Locking passiert separat in `uv.lock`

---

## 🔐 Zusätzlich (wenn du `uv sync` nutzt)

Dann kommt noch dazu:

```text id="l8m3qp"
uv.lock
```

👉 das ist:

* exakt reproduzierbare Dependency-Liste
* ähnlich wie `poetry.lock`

---

## 🧾 Fazit

✔ `pyproject.toml` ist bei `uv` sehr schlank
✔ nur Projekt + Build-System
✔ Dependencies kommen automatisch rein
✔ kein pip/requirements Chaos mehr

---

Wenn du willst, kann ich dir als nächstes zeigen:
👉 wie daraus ein echtes Setup mit FastAPI oder Data Engineering Projekt entsteht (inkl. Docker + uv) 👍
