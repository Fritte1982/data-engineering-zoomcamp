# NY Taxi ETL – Dokumentation

## Zweck

Python-Skript zum Laden der NYC Yellow-Taxi-Daten (CSV, gzip, chunked) in eine
PostgreSQL-Datenbank, die in einem Docker-Container läuft. Das Skript legt bei
Bedarf die Ziel-Datenbank automatisch an und fügt die Daten chunk-weise ein.

---

## 1. Ausgangsproblem: `database "ny_taxi" does not exist`

**Ursache:** `POSTGRES_USER`, `POSTGRES_PASSWORD` und `POSTGRES_DB` werden von
Postgres **nur bei der Erstinitialisierung** (`initdb`) des Datenverzeichnisses
ausgewertet. Das passiert nur, wenn das Volume, in das
`/var/lib/postgresql` gemountet wird, **leer** ist.

Wird ein bereits existierendes Named Volume wiederverwendet
(`-v ny_taxi_postgres_data:/var/lib/postgresql`), läuft `initdb` nicht erneut
→ `POSTGRES_DB=ny_taxi` wird komplett ignoriert.

**Lösungen:**

```bash
# A) Volume neu anlegen (sauberster Weg, alle Daten weg)
docker volume rm ny_taxi_postgres_data
docker run -it --rm -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 postgres:18
```

```bash
# B) DB manuell nachträglich anlegen (Volume/Daten bleiben erhalten)
pgcli -h host.docker.internal -U root -d postgres
```
```sql
CREATE DATABASE ny_taxi;
```

Alle vorhandenen DBs im Container anzeigen:
```bash
pgcli -h host.docker.internal -U root -d postgres -c "\l"
```

Besser: Das Skript prüft/erstellt die DB selbst (siehe Abschnitt 2), damit man
sich um das Volume-Problem im Alltag keine Gedanken mehr machen muss.

---

## 2. Automatisches Anlegen der Ziel-Datenbank

Um `CREATE DATABASE` ausführen zu können, muss man sich zuerst mit einer
**bereits existierenden** DB verbinden – standardmäßig ist das `postgres`.
Erst danach kann man auf die eigentliche Ziel-DB umschalten.

```python
def ensure_database_exists(pg_user, pg_pass, pg_host, pg_port, pg_db):
    # Verbindung zur Standard-DB "postgres", NICHT zur Ziel-DB
    admin_engine = create_engine(
        f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/postgres'
    )

    # CREATE DATABASE darf serverseitig nicht in einer Transaktion laufen -> autocommit
    with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": pg_db}
        ).scalar()

        if not exists:
            # Identifier (Tabellen-/DB-Namen) können nicht als SQL-Parameter gebunden werden,
            # daher String-Interpolation - pg_db muss aus vertrauenswürdiger Quelle stammen (CLI-Flag)
            conn.execute(text(f'CREATE DATABASE "{pg_db}"'))
            print(f"Datenbank '{pg_db}' wurde angelegt.")
        else:
            print(f"Datenbank '{pg_db}' existiert bereits.")

    admin_engine.dispose()
```

**Wichtige Punkte:**

| Aspekt | Erklärung |
|---|---|
| Verbindung zu `postgres` | Standard-DB, die praktisch immer existiert; wird nur gebraucht, um `CREATE DATABASE` absetzen zu können |
| `AUTOCOMMIT` | `CREATE DATABASE` kann nicht innerhalb eines Transaktionsblocks laufen → sonst Fehler `CREATE DATABASE cannot run inside a transaction block` |
| Kein Parameter-Binding für den DB-Namen | `:dbname`-Bindings funktionieren nur für **Werte**, nicht für **Identifier** (Tabellen-/DB-Namen) |
| Race Condition | Bei parallelen Läufen könnte zwischen `SELECT` und `CREATE` eine andere Instanz die DB anlegen → `CREATE DATABASE` schlägt dann mit "already exists" fehl. Für ein seriell laufendes ETL-Skript unkritisch |

Damit ist das Skript **idempotent** bezüglich der Datenbank: Es kann beliebig
oft aufgerufen werden, egal ob `ny_taxi` schon existiert oder nicht.

---

## 3. Bug: `if_exists="replace"` im Insert-Loop

### Ursprünglicher (fehlerhafter) Code

```python
for df_chunk in tqdm(df_iter, ...):
    if first:
        df_chunk.head(0).to_sql(name=target_table, con=engine, if_exists="replace")
        first = False

    df_chunk.to_sql(
        name=target_table,
        con=engine,
        if_exists="replace"   # ← Bug: läuft bei JEDEM Chunk
    )
```

`if_exists="replace"` bedeutet **nicht** "nur Header/Spalten ersetzen", sondern
intern etwa:

```sql
DROP TABLE IF EXISTS target_table;
CREATE TABLE target_table (...);   -- Schema aus den DataFrame-Dtypes
-- danach INSERT der Zeilen aus dem DataFrame
```

Die Zeilenanzahl im DataFrame (z. B. `head(0)` = 0 Zeilen) spielt für das
Verhalten von `if_exists` keine Rolle – `replace` löscht immer die **ganze
Tabelle**, unabhängig davon, ob 0 oder 100.000 Zeilen eingefügt werden.

Weil der ursprüngliche Code `if_exists="replace"` bei **jedem** Chunk
aufruft, wird die Tabelle bei jedem Durchlauf komplett gelöscht und neu
angelegt. Am Ende steht nur der **letzte** Chunk (100.000 Zeilen) in der
Tabelle statt aller ~1,37 Mio. Zeilen.

### Korrigierter Code

```python
first = True

for df_chunk in tqdm(df_iter, desc="NY Taxi ETL", unit="chunk",
                      dynamic_ncols=True, disable=False, total=total_chunks):

    if first:
        # Schema einmalig anlegen: head(0) = 0 Zeilen, DROP+CREATE nur hier
        df_chunk.head(0).to_sql(name=target_table, con=engine, if_exists="replace")
        first = False

    # Daten anhängen statt Tabelle jedes Mal neu zu erstellen
    df_chunk.to_sql(name=target_table, con=engine, if_exists="append")
```

### Ablauf im Detail

| Chunk | `if first:`-Block | `to_sql(..., if_exists=...)` außerhalb |
|---|---|---|
| 1 | `head(0)` → Tabelle wird **einmal** komplett neu erstellt (`replace`) | 100.000 Zeilen werden **angehängt** (`append`) |
| 2 | übersprungen (`first=False`) | 100.000 Zeilen angehängt |
| 3 | übersprungen | 100.000 Zeilen angehängt |
| ... | ... | ... |

`replace` löscht die Tabelle nur **einmal zu Beginn** und legt sie mit dem
korrekten Schema leer an. Alle eigentlichen Daten kommen ausschließlich über
`append` hinein – pro Chunk genau einmal, da der Aufruf außerhalb von
`if first:` bei jeder Schleifeniteration genau einmal ausgeführt wird.

### `if_exists`-Optionen im Überblick

| Wert | Verhalten |
|---|---|
| `"fail"` | Fehler, falls Tabelle existiert (Default von pandas) |
| `"replace"` | `DROP TABLE` + `CREATE TABLE` neu, danach Daten einfügen |
| `"append"` | Tabelle bleibt bestehen, Daten werden nur per `INSERT` hinzugefügt |

### Wann entstehen trotzdem Duplikate?

Der obige Ablauf ist für einen **vollständigen** Durchlauf sicher. Duplikate
entstehen nur in folgenden Fällen:

- Das Skript bricht **mitten im Durchlauf** ab und wird **manuell ab einem
  späteren Chunk** neu gestartet, ohne dass `first=True` erneut den
  `replace`-Schritt durchläuft.
- Ein externer Prozess fügt parallel Daten in dieselbe Tabelle ein.

Für robustes **Resume nach Abbruch** (ohne kompletten Neustart) wären weitere
Maßnahmen nötig, z. B.:
- Primary Key/Unique Constraint + `INSERT ... ON CONFLICT DO NOTHING`
- Tracking, welcher Chunk zuletzt erfolgreich committed wurde (z. B. in einer
  separaten Metadaten-Tabelle oder Datei)

---

## 4. Vollständiges, korrigiertes Skript

```python
#!/usr/bin/env python
# coding: utf-8
"""
Insert Table n Data from rep-source:'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
in to the pg-container :
    cli>:   'docker run -it --rm -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi"
            -v ny_taxi_postgres_data:/var/lib/postgresql -p 5432:5432 postgres:18'
"""

#region imports
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
import math
import click

#endregion
total_chunks = math.ceil(1369765 / 100000)

# region dtype declare
dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]
#endregion

host = "host.docker.internal"  # default host

year = 2021
month = 1
prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
url = prefix + f'yellow_tripdata_{year}-{month:02d}.csv.gz'


def ensure_database_exists(pg_user, pg_pass, pg_host, pg_port, pg_db):
    """
    Legt die Ziel-Datenbank an, falls sie noch nicht existiert.
    Verbindet sich dazu mit der Standard-DB 'postgres', da CREATE DATABASE
    nicht aus der Ziel-DB selbst heraus ausgeführt werden kann.
    """
    admin_engine = create_engine(
        f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/postgres'
    )

    # CREATE DATABASE darf nicht in einer Transaktion laufen -> autocommit
    with admin_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": pg_db}
        ).scalar()

        if not exists:
            # Identifier können nicht als SQL-Parameter gebunden werden.
            # pg_db sollte daher nur aus vertrauenswürdiger Quelle (CLI-Flag) stammen.
            conn.execute(text(f'CREATE DATABASE "{pg_db}"'))
            print(f"Datenbank '{pg_db}' wurde angelegt.")
        else:
            print(f"Datenbank '{pg_db}' existiert bereits.")

    admin_engine.dispose()


# region iter chunks, create n insert the pg-db

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default=host, help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
@click.option("--repo_url", default=None, help='Repository URL')
@click.option("--year", default=2021, type=int, help='Dataset Year')
@click.option("--month", default=1, type=int, help='Dataset Month')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, repo_url, year, month):
    # Zielt-DB anlegen, falls sie noch nicht existiert
    ensure_database_exists(pg_user, pg_pass, pg_host, pg_port, pg_db)

    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    final_url = repo_url

    if final_url is None:
        final_url = (
            "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/"
            f"yellow_tripdata_{year}-{month:02d}.csv.gz"
        )

    df_iter = pd.read_csv(
        final_url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=100000
    )

    first = True

    for df_chunk in tqdm(df_iter, desc="NY Taxi ETL", unit="chunk", dynamic_ncols=True,
                          disable=False, total=total_chunks):

        if first:
            # Schema einmalig anlegen (0 Zeilen -> nur Spaltenstruktur/DROP+CREATE)
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace"
            )
            first = False
            # print("Table created")

        # Chunk-Daten anhängen (nicht ersetzen!)
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append"
        )

#endregion


# region main
if __name__ == '__main__':
    run()
# endregion
```

---

## 5. Änderungen gegenüber der Ausgangsversion (Zusammenfassung)

| # | Änderung | Grund |
|---|---|---|
| 1 | `ensure_database_exists()` hinzugefügt, wird zu Beginn von `run()` aufgerufen | DB wird automatisch angelegt, falls sie fehlt → kein manuelles `CREATE DATABASE` mehr nötig |
| 2 | `from sqlalchemy import create_engine, text` | `text()` wird für rohe SQL-Statements benötigt |
| 3 | Zweiter `to_sql(...)`-Aufruf: `if_exists="replace"` → `if_exists="append"` | Verhindert, dass die Tabelle bei jedem Chunk gelöscht und neu befüllt wird; sonst enthält die Tabelle am Ende nur den letzten Chunk |