# Deploying iPay

The demo runs on `ipay-ingenious`, an AWS EC2 server (Debian 13), reached over Tailscale. Addresses and access are in CLAUDE.md under "Server".

## Everyday deploy

Commit first, then run:

```bash
bash deploy/deploy.sh
```

The script pushes HEAD to GitHub, copies the committed tree to `/opt/ipay/src` over SSH, then rebuilds and restarts whatever changed. Only committed files travel, so `documents/` and `.env` never leave the PC. Migrations run when the app container starts.

## Stack

`docker-compose.prod.yml`, compose project `ipay`:

| Service | What it runs |
| --- | --- |
| `etcd` | Patroni's DCS |
| `db` | PostgreSQL 16 under Patroni (`deploy/patroni/`), a single member |
| `app` | iPay on Apache + mod_wsgi (`Dockerfile`, `deploy/entrypoint.sh`), on 127.0.0.1:8080 |
| `proxy` | Caddy, in the `public` profile: HTTPS for `IPAY_DOMAIN`, bound to `PUBLIC_BIND_IP` |

The tailnet address is served by `tailscale serve` from 127.0.0.1:8080.

## Server `.env`

The server's `.env` lives at `/opt/ipay/.env`. It was created on the server, is readable by root only, and its values must never be copied off it. Its keys are listed in `.env.example`.

## Useful commands

```bash
ssh ipay-ingenious "sudo docker exec ipay-db-1 /opt/patroni/bin/patronictl -c /etc/patroni.yml list"   # cluster state
ssh ipay-ingenious "sudo sh -c 'cd /opt/ipay/src && docker compose -p ipay -f docker-compose.prod.yml logs --tail 50 app'"
ssh ipay-ingenious "sudo docker exec -it ipay-db-1 psql -U postgres -d ipay"                          # SQL shell
```

## Before any real data

- Daily `pg_dump` to S3, with a tested restore.
- A security review: a content security policy and an audit log.
