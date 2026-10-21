# iPay application: Apache + mod_wsgi (via mod_wsgi-express), house standard.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# apache2-dev and gcc are needed to build mod_wsgi against this image's Python.
RUN apt-get update \
 && apt-get install -y --no-install-recommends apache2 apache2-dev gcc libc6-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt mod_wsgi==5.0.2 \
 && apt-get purge -y gcc libc6-dev && apt-get autoremove -y

COPY . .
RUN useradd --system --home-dir /app --shell /usr/sbin/nologin ipay && chown -R ipay /app
USER ipay

EXPOSE 8000
ENTRYPOINT ["sh", "deploy/entrypoint.sh"]
