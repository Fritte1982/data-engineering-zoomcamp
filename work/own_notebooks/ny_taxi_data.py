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
from sqlalchemy import create_engine
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

host = "host.docker.internal" #default host

year = 2021
month = 1
prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
url = prefix + f'yellow_tripdata_{year}-{month:02d}.csv.gz'

# region iter chunks, create n insert the pg-db

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default=host, help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
@click.option("--repo_url",default=None, help='Repository URL')
@click.option("--year",default=2021,type=int, help='Dataset Year')
@click.option("--month",default=1, type=int, help='Dataset Month')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, repo_url, year, month):
    # Ingestion logic here
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

    for df_chunk in tqdm( df_iter,  desc="NY Taxi ETL", unit="chunk", dynamic_ncols=True,
                        disable=False, total=total_chunks ):

        if first:
        # Create table schema (no data)
            df_chunk.head(0).to_sql(
            name=target_table,
            con=engine,
            if_exists="replace"
        )
            first = False
            # print("Table created")

        # Insert chunk
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