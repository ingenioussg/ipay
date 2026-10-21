#!/bin/sh
# Migrate the database, then serve through Apache + mod_wsgi. Apache serves /static directly.
set -e
python -m schemaconnect.postgres.migrations.migrate
exec mod_wsgi-express start-server routing.wsgi \
    --port 8000 \
    --processes 2 --threads 8 \
    --url-alias /static /app/static \
    --server-root /tmp/mod_wsgi \
    --log-to-terminal --access-log \
    --limit-request-body 10485760
