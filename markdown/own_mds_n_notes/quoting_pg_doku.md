# PostgreSQL – Identifier maskieren (Spalten-/Tabellennamen vs. Keywords)

## 1. Das Problem

Postgres hat reservierte Wörter (`SELECT`, `GROUP`, `USER`, `ORDER`, `TABLE`,
`WHERE`, ...) und Groß-/Kleinschreibungsregeln, die überraschen können, wenn
ein Spalten- oder Tabellenname zufällig mit einem Keyword kollidiert oder
Großbuchstaben/Sonderzeichen enthält (z. B. beim CSV-Import mit Original-
Headern wie `VendorID`, `User`, `Order Date`).

```sql
-- Fehler: "user" ist reserviertes Keyword
SELECT user FROM accounts;

-- Fehler: Leerzeichen im Spaltennamen
SELECT Order Date FROM sales;
```

**Lösung:** Identifier (Tabellen-, Spalten-, Alias-Namen) mit
**doppelten Anführungszeichen** `"..."` maskieren.

---

## 2. Grundregel: `"..."` für Identifier, `'...'` für Werte

| Zeichen | Bedeutung |
|---|---|
| `"doppelte Anführungszeichen"` | Identifier (Tabelle, Spalte, Alias) |
| `'einfache Anführungszeichen'` | String-**Wert** (Literal) |

```sql
-- Identifier maskiert
SELECT "Order Date" FROM sales;

-- Wert maskiert
SELECT * FROM sales WHERE status = 'shipped';
```

Verwechslung ist einer der häufigsten Anfängerfehler:
```sql
-- FALSCH: 'name' wird als String-Literal "name" interpretiert, nicht als Spalte
SELECT 'name' FROM customers;

-- RICHTIG: Spalte name
SELECT "name" FROM customers;
-- oder ganz ohne Anführungszeichen, wenn name kein Keyword ist und lowercase:
SELECT name FROM customers;
```

---

## 3. Warum überhaupt maskieren? Groß-/Kleinschreibung in Postgres

Postgres faltet **unquotierte** Identifier automatisch auf Kleinbuchstaben:

```sql
CREATE TABLE Kunden (VendorID int);
```
wird intern gespeichert als:
```sql
CREATE TABLE kunden (vendorid int);
```

Das heißt: `SELECT VendorID FROM Kunden;` funktioniert trotzdem, weil beide
Seiten gleich klein geschrieben werden.

**Sobald man beim Erstellen aber Anführungszeichen verwendet, bleibt die
Groß-/Kleinschreibung exakt erhalten** – und muss danach **immer** wieder
exakt so (mit Anführungszeichen) verwendet werden:

```sql
CREATE TABLE "Kunden" ("VendorID" int);

-- Funktioniert:
SELECT "VendorID" FROM "Kunden";

-- Fehler, weil ohne Anführungszeichen automatisch klein gefaltet wird
-- -> Postgres sucht nach der Tabelle "kunden", die es nicht gibt:
SELECT vendorid FROM Kunden;
```

**Praxisrelevanz für dich:** Wenn `pandas.to_sql()` (wie in deinem ETL-
Skript) eine Tabelle mit Original-CSV-Headern wie `VendorID`,
`tpep_pickup_datetime` anlegt, werden diese standardmäßig **mit** Groß-/
Kleinschreibung als quotierte Identifier gespeichert. In `pgcli`/`psql`
musst du sie dann exakt so und in Anführungszeichen ansprechen:

```sql
SELECT "VendorID", "tpep_pickup_datetime" FROM yellow_taxi_data;
```

Prüfen, wie die Spalten tatsächlich im Schema heißen:
```sql
\d yellow_taxi_data
-- oder
SELECT column_name FROM information_schema.columns
WHERE table_name = 'yellow_taxi_data';
```

---

## 4. Reservierte Keywords als Identifier verwenden

Manche Namen sind reservierte SQL-Schlüsselwörter (`user`, `order`, `group`,
`table`, `select`, `limit`, `check`, ...). Ohne Maskierung interpretiert
Postgres sie als Teil der SQL-Syntax, nicht als Namen:

```sql
-- Fehler: "user" wird als Systemfunktion/Keyword erkannt
CREATE TABLE test (user text);

-- Funktioniert mit Anführungszeichen
CREATE TABLE test ("user" text);
SELECT "user" FROM test;
```

Liste aller reservierten Wörter mit Einordnung (reserviert / non-reserviert,
SQL-Standard vs. Postgres-spezifisch) direkt im System abfragbar:
```sql
SELECT * FROM pg_get_keywords() WHERE word = 'user';
```

**Best Practice:** Solche Namen möglichst von vornherein vermeiden
(`username` statt `user`, `order_date` statt `order`) – spart dir dauerhaft
Anführungszeichen-Stress in jedem Query, jedem ORM, jedem Tool.

---

## 5. Sonderzeichen und Leerzeichen im Namen

Identifier mit Leerzeichen, Bindestrichen oder Sonderzeichen **müssen**
maskiert werden:

```sql
CREATE TABLE "sales-2021" (
    "Order Date" date,
    "Total (€)" numeric
);

SELECT "Order Date", "Total (€)" FROM "sales-2021";
```

Ohne Anführungszeichen bricht der Parser an Leerzeichen/Bindestrichen ab
und interpretiert den Rest als eigenständiges Token → Syntaxfehler.

---

## 6. Anführungszeichen *im* Identifier selbst escapen

Falls ein Identifier tatsächlich ein `"` enthalten soll (selten, aber
möglich), wird es verdoppelt:

```sql
CREATE TABLE test ("crazy""name" text);
SELECT "crazy""name" FROM test;
```

Analog werden `'` in String-**Werten** verdoppelt:
```sql
SELECT * FROM customers WHERE name = 'O''Brien';
```

---

## 7. In Python/SQLAlchemy: Identifier korrekt zusammenbauen

Aus deinem `ensure_database_exists()`-Beispiel: Identifier (DB-, Tabellen-,
Spaltennamen) können **nicht** als SQL-Parameter (`:name`-Bindings)
übergeben werden – die verhindern SQL-Injection nur bei **Werten**, nicht
bei Identifiern. Für Identifier bleibt nur kontrollierte String-
Interpolation, am besten mit Anführungszeichen-Absicherung:

```python
from sqlalchemy import text

# Werte: Parameter-Binding verwenden (sicher gegen SQL-Injection)
conn.execute(
    text("SELECT * FROM accounts WHERE status = :status"),
    {"status": "active"}
)

# Identifier: manuell maskieren, Eingabe muss vertrauenswürdig sein
tabelle = "sales-2021"
conn.execute(text(f'SELECT * FROM "{tabelle}"'))
```

SQLAlchemy bietet dafür auch `sqlalchemy.sql.quoted_name` bzw. die
`Identifier`-Hilfsfunktionen von `psycopg` (`psycopg.sql.Identifier`), die
das Maskieren automatisch und sicher übernehmen:

```python
from psycopg import sql

query = sql.SQL("SELECT * FROM {table}").format(
    table=sql.Identifier("sales-2021")
)
```

Das ist die robustere Variante, falls Tabellennamen dynamisch (z. B. aus
CLI-Argumenten wie in deinem Click-Skript) kommen.

---

## 8. Kurz-Referenzkarte (Cheat Sheet)

```sql
-- Identifier vs. Wert
"spalte"    -- Identifier (Tabelle/Spalte/Alias)
'text'      -- String-Wert

-- Groß-/Kleinschreibung
CREATE TABLE Foo (Bar int);      -- intern: foo (bar int) -> ohne "" ansprechen
CREATE TABLE "Foo" ("Bar" int);  -- bleibt Foo/Bar -> IMMER mit "" ansprechen

-- Reservierte Keywords als Name -> maskieren
SELECT "user", "order" FROM "table";

-- Leerzeichen/Sonderzeichen -> maskieren
SELECT "Order Date" FROM "sales-2021";

-- " im Identifier escapen: verdoppeln
"crazy""name"

-- ' im Wert escapen: verdoppeln
'O''Brien'

-- Spaltennamen einer Tabelle nachschlagen
\d tabellenname
-- oder
SELECT column_name FROM information_schema.columns WHERE table_name = 'tabellenname';
```