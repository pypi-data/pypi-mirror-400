# url2pg - v0.1.0

This repository ingests data from a CSV/Parquet url into a Postgres table
overwriting the previous table if it exists.

Installation
```shell
uv add url2pg
```
or
```shell
pip install url2pg
```
Usage:
```shell
url2pg \
    --user=<postgres_user:default=root> \
    --password=<postgres_password:default=root> \
    --host=<postgres_host:default=localhost> \
    --port=<postgres_port:default=5432> \
    --db=<*_db> \
    --table_name=<*_destiny_table> \
    --url_file=<*_source_url>
```

You can use as a Docker image as well:
```shell
docker run -it \
    --network=<*_destiny_network> \
    cesarbouli/url2pg \
    --user=<postgres_user:default=root> \
    --password=<postgres_password:default=root> \
    --host=<postgres_host:default=localhost> \
    --port=<postgres_port:default=5432> \
    --db=<*_db> \
    --table_name=<*_destiny_table> \
    --url_file=<*_source_url>
```

In your docker compose file:
```yaml
services:
  ingestion-data:
    image: cesarbouli/url2pg
    command: --db=<_db_> (...)
    (...)
```
Docker image: [https://hub.docker.com/r/cesarbouli/url2pg](https://hub.docker.com/r/cesarbouli/url2pg) \
