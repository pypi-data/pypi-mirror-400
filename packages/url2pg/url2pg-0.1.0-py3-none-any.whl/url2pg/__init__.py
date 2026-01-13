import pandas as pd
from sqlalchemy import create_engine
import math
import argparse
import os
import logging

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        prog="url2pg",
        description="Ingest CSV or Parquet file data to a Postgres table",
    )
    parser.add_argument("--version", action="version", version="%(prog)s v0.1.0")

    parser.add_argument("--user", help="user name for postgres", default="root")
    parser.add_argument("--password", help="password for postgres", default="root")
    parser.add_argument("--host", help="host for postgres", default="localhost")
    parser.add_argument("--port", help="port for postgres", default="5432")
    parser.add_argument(
        "--table_name", help="name of the table to write data to", required=True
    )
    parser.add_argument("--db", help="database name for postgres", required=True)
    parser.add_argument(
        "--url_file", help="url to the csv or parquet file", required=True
    )

    args = parser.parse_args()

    url2pg(args)


def url2pg(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url_file = params.url_file

    csv_temp_file = "temp.csv"

    logger = logging.getLogger()
    logger.info("Ingestion-Data script started")

    logger.info(f"Downloading data from {url_file}")
    if url_file.endswith(".csv"):
        os.system(f"wget {url_file} -O {csv_temp_file}")
        df = pd.read_csv(csv_temp_file, nrows=100)
    elif url_file.endswith(".parquet"):

        logger.info("Converting Parquet file to CSV")
        os.system(f"wget {url_file} -O {csv_temp_file}.parquet")
        df = pd.read_parquet(csv_temp_file + ".parquet")
        os.remove(csv_temp_file + ".parquet")

        df.to_csv(csv_temp_file, index=False)
        df = df.head(n=100)

    else:
        raise Exception(
            f"Sorry, but the url_file you are using ({url_file}) needs to be a CSV or a Parquet file."
        )

    logger.info("Connecting to the database")
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    logger.info("Creating table in the database if it does not exist")
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")

    logger.info("Inserting data into the database in chunks")
    n_lines = len(pd.read_csv(csv_temp_file))
    chunksize = 100000

    df_iter = pd.read_csv(csv_temp_file, iterator=True, chunksize=chunksize)
    for i in range(math.ceil(n_lines / chunksize)):
        df = next(df_iter)
        df.to_sql(name=table_name, con=engine, if_exists="append")
        logger.info(f"chunk {i + 1} from {math.ceil(n_lines / chunksize)} inserted")

    logger.info("Insertion finished")
    os.remove(csv_temp_file)


if __name__ == "__main__":
    main()
