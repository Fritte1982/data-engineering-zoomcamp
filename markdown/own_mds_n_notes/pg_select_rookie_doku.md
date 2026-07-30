# PostgreSQL – SELECT-Querys für Einsteiger

## 1. Grundgerüst

```sql
SELECT spalte1, spalte2
FROM tabelle
WHERE bedingung
GROUP BY spalte
HAVING gruppenbedingung
ORDER BY spalte
LIMIT n;
```

**Reihenfolge im Code = feste Syntax-Reihenfolge.** Die tatsächliche
**Ausführungsreihenfolge** von Postgres weicht davon ab – das ist wichtig,
um zu verstehen, warum manche Dinge (z. B. Spalten-Alias in `WHERE`) nicht
funktionieren:

```
FROM  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT  →  ORDER BY  →  LIMIT
```

`WHERE` läuft also **vor** `SELECT` – deshalb kann man in `WHERE` keinen
Alias verwenden, der erst in `SELECT` definiert wird.

---

## 2. Alle Spalten / bestimmte Spalten

```sql
SELECT * FROM yellow_taxi_data;

SELECT vendorid, tpep_pickup_datetime, fare_amount
FROM yellow_taxi_data;
```

`*` ist praktisch zum Explorieren, in produktivem Code besser explizit
Spalten angeben (Performance, Lesbarkeit, weniger Überraschungen bei
Schemaänderungen).

**Spalten umbenennen (Alias) mit `AS`:**
```sql
SELECT
    fare_amount AS fahrpreis,
    tip_amount AS trinkgeld
FROM yellow_taxi_data;
```
`AS` ist optional, `fare_amount fahrpreis` funktioniert auch – `AS` ist
aber lesbarer.

---

## 3. WHERE – Zeilen filtern

```sql
SELECT * FROM yellow_taxi_data
WHERE passenger_count > 1;
```

**Wichtige Operatoren:**

| Operator | Bedeutung |
|---|---|
| `=`, `<>` / `!=` | gleich, ungleich |
| `<`, `>`, `<=`, `>=` | Vergleich |
| `AND`, `OR`, `NOT` | Verknüpfung |
| `BETWEEN a AND b` | Bereich (inklusive) |
| `IN (a, b, c)` | Wert in Liste |
| `LIKE 'muster%'` | Textmuster, case-sensitive |
| `ILIKE 'muster%'` | Textmuster, **case-insensitive** (Postgres-spezifisch) |
| `IS NULL` / `IS NOT NULL` | NULL-Prüfung (niemals `= NULL` verwenden!) |

```sql
-- Bereich
SELECT * FROM yellow_taxi_data
WHERE tpep_pickup_datetime BETWEEN '2021-01-01' AND '2021-01-31';

-- Liste
SELECT * FROM yellow_taxi_data
WHERE payment_type IN (1, 2);

-- Textsuche, case-insensitive (Postgres-spezifisch)
SELECT * FROM yellow_taxi_data
WHERE store_and_fwd_flag ILIKE 'y%';

-- NULL-Check
SELECT * FROM yellow_taxi_data
WHERE congestion_surcharge IS NOT NULL;
```

**Falle:** `NULL` ist nie gleich irgendetwas, auch nicht sich selbst.
`WHERE spalte = NULL` liefert **immer** 0 Zeilen. Immer `IS NULL` /
`IS NOT NULL` benutzen.

---

## 4. ORDER BY – Sortieren

```sql
SELECT * FROM yellow_taxi_data
ORDER BY fare_amount DESC;        -- absteigend
ORDER BY fare_amount ASC;         -- aufsteigend (Default)
ORDER BY tpep_pickup_datetime, fare_amount DESC;  -- mehrstufig
```

Postgres-Spezifikum: `NULLS FIRST` / `NULLS LAST` steuern, wo NULL-Werte
einsortiert werden (Default: `NULLS LAST` bei `ASC`, `NULLS FIRST` bei `DESC`):
```sql
ORDER BY congestion_surcharge NULLS LAST;
```

---

## 5. LIMIT / OFFSET – Zeilen begrenzen (Postgres-spezifisch)

`LIMIT`/`OFFSET` ist keine ANSI-SQL-Standard-Syntax, sondern
Postgres/MySQL-Dialekt (Standard-SQL nutzt `FETCH FIRST n ROWS ONLY`, das
Postgres auch unterstützt).

```sql
SELECT * FROM yellow_taxi_data
ORDER BY fare_amount DESC
LIMIT 10;                 -- nur die ersten 10 Zeilen

SELECT * FROM yellow_taxi_data
ORDER BY fare_amount DESC
LIMIT 10 OFFSET 20;        -- 10 Zeilen, ab Zeile 21 (Pagination)
```

**Wichtig:** `LIMIT` ohne `ORDER BY` liefert eine **undefinierte** Reihenfolge
– für konsistente Ergebnisse (z. B. Pagination) immer mit `ORDER BY`
kombinieren.

---

## 6. DISTINCT – Duplikate entfernen

```sql
SELECT DISTINCT payment_type FROM yellow_taxi_data;

-- Mehrere Spalten: Kombination muss eindeutig sein
SELECT DISTINCT vendorid, payment_type FROM yellow_taxi_data;
```

**Postgres-spezifisch: `DISTINCT ON`** – pro Gruppe nur die "erste" Zeile
(nach `ORDER BY`) behalten, sehr nützlich, aber nicht Standard-SQL:
```sql
-- Pro VendorID nur die teuerste Fahrt
SELECT DISTINCT ON (vendorid) *
FROM yellow_taxi_data
ORDER BY vendorid, fare_amount DESC;
```
`DISTINCT ON` **muss** mit `ORDER BY` kombiniert werden, wobei die
`DISTINCT ON`-Spalte(n) am Anfang von `ORDER BY` stehen müssen.

---

## 7. Aggregatfunktionen

```sql
SELECT
    COUNT(*)              AS anzahl_fahrten,
    SUM(fare_amount)       AS summe_fahrpreis,
    AVG(fare_amount)       AS durchschnitt_fahrpreis,
    MIN(fare_amount)       AS min_fahrpreis,
    MAX(fare_amount)       AS max_fahrpreis
FROM yellow_taxi_data;
```

`COUNT(*)` zählt alle Zeilen (auch mit NULL-Werten), `COUNT(spalte)` zählt
nur Zeilen, in denen `spalte` **nicht** NULL ist – ein häufiger
Anfängerfehler ist die Annahme, beide seien identisch.

---

## 8. GROUP BY – Gruppieren

```sql
SELECT
    payment_type,
    COUNT(*)          AS anzahl,
    AVG(fare_amount)   AS avg_fahrpreis
FROM yellow_taxi_data
GROUP BY payment_type
ORDER BY anzahl DESC;
```

**Regel:** Jede Spalte im `SELECT`, die **keine** Aggregatfunktion ist,
muss auch in `GROUP BY` stehen. Sonst Fehler:
`column must appear in the GROUP BY clause or be used in an aggregate function`.

---

## 9. HAVING – Gruppen filtern

`WHERE` filtert Zeilen **vor** der Gruppierung, `HAVING` filtert Gruppen
**nach** der Gruppierung/Aggregation:

```sql
SELECT
    payment_type,
    COUNT(*) AS anzahl
FROM yellow_taxi_data
GROUP BY payment_type
HAVING COUNT(*) > 1000;
```

`WHERE payment_type ... COUNT(*) > 1000` würde **nicht** funktionieren,
weil `COUNT(*)` zum Zeitpunkt von `WHERE` noch nicht berechnet ist
(siehe Ausführungsreihenfolge in Abschnitt 1).

---

## 10. JOINs – Tabellen verknüpfen

Angenommen, es gibt eine Zonen-Tabelle `taxi_zone_lookup(locationid, zone, borough)`:

```sql
-- INNER JOIN: nur Zeilen mit Match in beiden Tabellen
SELECT
    t.tpep_pickup_datetime,
    z.zone AS pickup_zone
FROM yellow_taxi_data t
INNER JOIN taxi_zone_lookup z
    ON t.pulocationid = z.locationid;

-- LEFT JOIN: alle Zeilen aus yellow_taxi_data, auch ohne Match
SELECT
    t.tpep_pickup_datetime,
    z.zone AS pickup_zone
FROM yellow_taxi_data t
LEFT JOIN taxi_zone_lookup z
    ON t.pulocationid = z.locationid;
```

| JOIN-Typ | Verhalten |
|---|---|
| `INNER JOIN` | Nur Zeilen mit Treffer in **beiden** Tabellen |
| `LEFT JOIN` | Alle Zeilen aus der linken Tabelle, rechte Spalten `NULL` bei keinem Treffer |
| `RIGHT JOIN` | Spiegelbild von `LEFT JOIN` |
| `FULL JOIN` | Alle Zeilen aus beiden Tabellen, fehlende Seite = `NULL` |

**Tabellen-Alias** (`t`, `z`) sind bei JOINs praktisch Pflicht, sobald
Spaltennamen mehrdeutig sein könnten.

---

## 11. Subqueries (Unterabfragen)

```sql
-- Subquery in WHERE
SELECT *
FROM yellow_taxi_data
WHERE fare_amount > (
    SELECT AVG(fare_amount) FROM yellow_taxi_data
);

-- Subquery als "virtuelle Tabelle" in FROM
SELECT payment_type, avg_fahrpreis
FROM (
    SELECT payment_type, AVG(fare_amount) AS avg_fahrpreis
    FROM yellow_taxi_data
    GROUP BY payment_type
) AS sub
WHERE avg_fahrpreis > 10;
```

Eine Subquery in `FROM` **muss** einen Alias haben (`AS sub`), sonst
Syntaxfehler.

---

## 12. CTE (Common Table Expression) – `WITH`

Lesbarere Alternative zu verschachtelten Subqueries, Postgres unterstützt
das voll:

```sql
WITH avg_pro_zahlungsart AS (
    SELECT payment_type, AVG(fare_amount) AS avg_fahrpreis
    FROM yellow_taxi_data
    GROUP BY payment_type
)
SELECT *
FROM avg_pro_zahlungsart
WHERE avg_fahrpreis > 10;
```

Mehrere CTEs lassen sich verketten:
```sql
WITH a AS (...),
     b AS (...)
SELECT * FROM a JOIN b ON ...;
```

---

## 13. Typische Postgres-Besonderheiten (Dialekt)

| Feature | Beispiel |
|---|---|
| `ILIKE` (case-insensitive LIKE) | `WHERE name ILIKE 'müller%'` |
| `DISTINCT ON` | siehe Abschnitt 6 |
| `LIMIT`/`OFFSET` | siehe Abschnitt 5 |
| Cast mit `::` | `SELECT fare_amount::int FROM ...` |
| Array-Typen | `SELECT ARRAY[1,2,3]` |
| `RETURNING` bei `INSERT`/`UPDATE`/`DELETE` | `INSERT INTO t (...) VALUES (...) RETURNING id;` |
| `EXPLAIN ANALYZE` | Ausführungsplan mit echten Laufzeiten anzeigen |

`::` ist Postgres-spezifisches Cast-Kürzel, äquivalent zu
`CAST(fare_amount AS int)` (Standard-SQL).

---

## 14. Kurz-Referenzkarte (Cheat Sheet)

```sql
-- Struktur
SELECT spalten FROM tabelle
WHERE zeilenfilter
GROUP BY gruppierspalten
HAVING gruppenfilter
ORDER BY sortierspalten
LIMIT n OFFSET m;

-- Ausführungsreihenfolge
FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT

-- NULL niemals mit = vergleichen
WHERE spalte IS NULL / IS NOT NULL

-- COUNT(*) vs COUNT(spalte)
COUNT(*)      -- alle Zeilen
COUNT(spalte) -- nur Nicht-NULL-Werte

-- case-insensitive Suche (Postgres)
WHERE spalte ILIKE '%muster%'
```