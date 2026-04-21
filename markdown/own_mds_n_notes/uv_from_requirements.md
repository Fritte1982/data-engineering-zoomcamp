Kurz gesagt: **`uv` nutzt primär `pyproject.toml`, kann aber auch mit `requirements.txt` arbeiten** 👍

---

# 🧠 Die klare Antwort

## ✅ Standard (empfohlen)

👉 **uv arbeitet mit:**

```text
pyproject.toml
uv.lock
```

→ das ist der moderne Weg

---

## ⚠️ Aber: `requirements.txt` geht auch

Du kannst z. B.:

```bash
uv pip install -r requirements.txt
```

👉 dann verhält sich `uv` wie ein schnellerer `pip`

---

# 🔍 Unterschied der beiden Ansätze

## 🟢 Modern (empfohlen)

```bash
uv add requests
```

→ schreibt in:

```toml
[project]
dependencies = ["requests"]
```

👉 Vorteile:

* sauber
* standardisiert (PEP)
* mit Lockfile (`uv.lock`)
* reproduzierbar

---

## 🟡 Klassisch (legacy)

```bash
uv pip install -r requirements.txt
```

👉 Vorteile:

* funktioniert mit alten Projekten

👉 Nachteile:

* kein Lockfile-System wie `uv.lock`
* weniger strukturiert
* schwerer wartbar

---

# 🔄 Migration von requirements.txt

Wenn du ein altes Projekt hast:

```bash
uv add -r requirements.txt
```

👉 Ergebnis:

* alles wird in `pyproject.toml` übernommen
* du bist im modernen Setup

---

# 📦 Export zurück (falls nötig)

```bash
uv export -o requirements.txt
```

👉 z. B. für:

* Docker
* CI/CD
* alte Systeme

---

# 🧠 Empfehlung

| Situation           | Empfehlung            |
| ------------------- | --------------------- |
| neues Projekt       | `pyproject.toml` ✔    |
| bestehendes Projekt | migrieren ✔           |
| nur schnell testen  | `requirements.txt` ok |

---

# 💡 Merksatz

> `requirements.txt` = Vergangenheit
> `pyproject.toml` = Zukunft

---

# 🧾 Fazit

✔ `uv` kann beides
✔ aber ist **für `.toml` gebaut**
👉 nutze `requirements.txt` nur für Kompatibilität

---

Wenn du willst, kann ich dir dein aktuelles Projekt von `requirements.txt` komplett sauber auf `uv` + `pyproject.toml` umstellen 👍
