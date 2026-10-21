# Deploying iPay to AWS (demo)

One EC2 server in Ingenious's own AWS account runs three containers from `docker-compose.prod.yml`:

- `db`: PostgreSQL 16, with data on a Docker volume.
- `app`: iPay on Apache + mod_wsgi. Migrations run at start.
- `proxy`: Caddy, which gets and renews the HTTPS certificate automatically.

Demo only: no real payroll data until backups and a security review are in place.

## 1. AWS account (owner, once)

1. Create the AWS account with `it@ingenious.sg`. Turn on MFA for the root user straight away, and do not use root day to day: create an IAM Identity Center (or IAM) user with AdministratorAccess and MFA.
2. Use the region **Asia Pacific (Singapore), ap-southeast-1**.
3. Billing > Budgets: add a monthly budget alert, for example US$30.

## 2. Server (owner, in the EC2 console)

1. **Launch instance**
   - Name: `ipay-demo`
   - Image: Ubuntu Server 24.04 LTS, 64-bit (Arm)
   - Type: `t4g.small` (2 vCPU, 2 GiB); roughly US$15-20 a month with storage
   - Key pair: create `ipay-demo` (ED25519, `.pem`) and save it as `C:\Users\ahmed\.ssh\ipay-demo.pem`
   - Security group `ipay-demo`: SSH (22) from **My IP** only; HTTP (80) and HTTPS (443) from anywhere
   - Storage: 20 GiB gp3
2. **Elastic IP**: allocate one and associate it with the instance, so the address survives restarts.
3. **DNS**: add an A record such as `ipay-demo.ingenious.sg`, pointing to the Elastic IP, wherever `ingenious.sg` DNS is hosted.
4. Tell Claude the Elastic IP and the host name.

## 3. Install (Claude, over SSH)

1. Add an `ipay-demo` host alias to `~/.ssh/config` using the key above.
2. On the server: install Docker Engine and the compose plugin, turn on unattended security upgrades, and allow only ports 22, 80 and 443 in `ufw`.
3. Copy the code to `/opt/ipay`. Only files git does not ignore are copied, so `documents/` (legacy material) and `.env` never leave the PC:
   ```bash
   git ls-files --cached --others --exclude-standard | tar -czf - -T - | ssh ipay-demo "sudo mkdir -p /opt/ipay && sudo tar -xzf - -C /opt/ipay"
   ```
4. Create `/opt/ipay/.env` **on the server** from `.env.example`, with fresh values for `FLASK_SECRET_KEY`, `POSTGRES_PASSWORD` and `SETUP_TOKEN`, plus `IPAY_DOMAIN` and `IPAY_DEMO=1`. Secrets are generated there and never copied back.
5. `cd /opt/ipay && sudo docker compose -f docker-compose.prod.yml up -d --build`, then check that the HTTPS certificate was issued and that `/` redirects to `/setup`.
6. Give the owner the one-time setup link, `https://<host>/setup?token=<SETUP_TOKEN>`. It stops working once the owner account exists.

## 4. Updating

Copy the changed code as in step 3.3, then:

```bash
ssh ipay-demo "cd /opt/ipay && sudo docker compose -f docker-compose.prod.yml up -d --build app"
```

Migrations run when the app container starts.

## 5. Before any real data

- Daily `pg_dump` to S3, with a tested restore.
- A security review: a content security policy, sign-in alerts, audit logging and access-right enforcement.
- Production on the house Patroni setup if high availability is needed.
