FROM postgres:18

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget -O /docker-entrypoint-initdb.d/lego.sql https://raw.githubusercontent.com/neondatabase/postgres-sample-dbs/main/lego.sql
