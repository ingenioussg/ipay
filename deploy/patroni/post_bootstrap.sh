#!/bin/sh
# Runs once, after Patroni initialises the cluster: creates the application role and database.
# Patroni passes a superuser connection string as $1. Values come from the environment.
set -e
psql "$1" -v ON_ERROR_STOP=1 \
    -v app_user="$POSTGRES_USER" -v app_password="$POSTGRES_PASSWORD" -v app_db="$POSTGRES_DB" <<'SQL'
CREATE ROLE :"app_user" LOGIN PASSWORD :'app_password';
CREATE DATABASE :"app_db" OWNER :"app_user";
SQL
