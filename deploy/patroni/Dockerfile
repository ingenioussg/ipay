# PostgreSQL 16 managed by Patroni (etcd as the DCS), as on the house servers.
FROM postgres:16-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv \
 && python3 -m venv /opt/patroni \
 && /opt/patroni/bin/pip install --no-cache-dir "patroni[etcd3]==4.0.4" "psycopg[binary]==3.2.3" \
 && rm -rf /var/lib/apt/lists/*

COPY patroni.yml /etc/patroni.yml
COPY post_bootstrap.sh /usr/local/bin/post_bootstrap.sh
RUN chmod 0755 /usr/local/bin/post_bootstrap.sh \
 && mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql

USER postgres
EXPOSE 5432 8008
ENTRYPOINT ["/opt/patroni/bin/patroni", "/etc/patroni.yml"]
