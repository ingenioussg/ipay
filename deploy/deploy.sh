#!/usr/bin/env bash
# Ship the committed HEAD to the iPay server: push to GitHub, copy the tree over SSH, rebuild.
# Only committed files travel, so documents/, docs/legacy/ and .env never leave the PC.
#   bash deploy/deploy.sh
set -euo pipefail
HOST="${IPAY_HOST:-ipay-ingenious}"

if [ -n "$(git status --porcelain)" ]; then
    echo "Commit first: the working tree has uncommitted changes." >&2
    exit 1
fi

git push origin HEAD
REV="$(git rev-parse --short HEAD)"

git -c core.autocrlf=false archive --format=tar HEAD | ssh "$HOST" "set -e
    sudo rm -rf /opt/ipay/src.new && sudo mkdir -p /opt/ipay/src.new
    sudo tar -xf - -C /opt/ipay/src.new
    sudo ln -sf /opt/ipay/.env /opt/ipay/src.new/.env
    echo $REV | sudo tee /opt/ipay/src.new/REVISION >/dev/null
    sudo rm -rf /opt/ipay/src && sudo mv /opt/ipay/src.new /opt/ipay/src"

ssh "$HOST" "sudo sh -c 'cd /opt/ipay/src && docker compose -p ipay -f docker-compose.prod.yml up -d --build --remove-orphans'"
echo "Deployed $REV to $HOST."
