#!/usr/bin/env python
# coding: utf-8
"""
Insert Table n Data from rep-source:'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
in to the pg-container :
cli>:'docker run -it --rm -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi"
-v ny_taxi_postgres_data:/var/lib/postgresql -p 5432:5432 postgres:18'
"""


#region imports
import pandas as pd
from sqlalchemy import create_engine
#endregion

#region repo-adress-variables
year = 2021
month = 1
prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
url = prefix + f'yellow_tripdata_{year}-{month:02d}.csv.gz'
#endregion

#region sqlalchemy pg-engine-sting
engine = create_engine('postgresql+psycopg://root:root@localhost:5432/ny_taxi')
# endregion

df = pd.read_csv(url, nrows=100)

# region dtype parse
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

df = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    nrows=100,
    dtype=dtype,
    parse_dates=parse_dates
)
#endregion


print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))

# region iter chunks, create n insert the pg-db
df_iter = pd.read_csv(
    url,
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
)


first = True

for df_chunk in df_iter:

    if first:
        # Create table schema (no data)
        df_chunk.head(0).to_sql(
            name="yellow_taxi_data",
            con=engine,
            if_exists="replace"
        )
        first = False
        print("Table created")

    # Insert chunk
    df_chunk.to_sql(
        name="yellow_taxi_data",
        con=engine,
        if_exists="append"
    )

    print("Inserted:", len(df_chunk))
#endregion