#!/bin/bash
set -euo pipefail

# Keep the new volume mounted and reachable for the initial transfer, without
# letting the upstream image install a second, empty REDAXO site.
if [[ "${REDAXO_MIGRATION_HOLD:-0}" == "1" ]]; then
  exec sleep infinity
fi

# Railway's runtime can expose the event MPM again after the image build.
if [[ -e /etc/apache2/mods-enabled/mpm_event.load ]]; then
  a2dismod mpm_event >/dev/null
fi

config=/var/www/html/redaxo/data/core/config.yml
if [[ ! -s "$config" ]]; then
  echo >&2 "Migrated REDAXO configuration is missing; refusing a fresh install."
  exit 1
fi

: "${REDAXO_DB_HOST:?missing database host}"
: "${REDAXO_DB_NAME:?missing database name}"
: "${REDAXO_DB_LOGIN:?missing database user}"
: "${REDAXO_DB_PASSWORD:?missing database password}"

# The persisted REDAXO config contains connection settings from the old host.
# The official CLI validates and updates those settings on every start.
php /var/www/html/redaxo/bin/console -q -n db:set-connection \
  --host="$REDAXO_DB_HOST" \
  --database="$REDAXO_DB_NAME" \
  --login="$REDAXO_DB_LOGIN" \
  --password="$REDAXO_DB_PASSWORD"

cp /usr/local/share/railway-health.php /var/www/html/railway-health.php
chmod 644 /var/www/html/railway-health.php

mkdir -p /var/www/html/site-analytics
cp /usr/local/share/site-analytics/consent.js /var/www/html/site-analytics/consent.js
chmod 644 /var/www/html/site-analytics/consent.js

# Install only the owned addon. Persisted templates, other addons and content stay intact.
mkdir -p /var/www/html/redaxo/src/addons/web_analytics
cp /usr/local/share/site-analytics/boot.php /usr/local/share/site-analytics/package.yml /var/www/html/redaxo/src/addons/web_analytics/
php /var/www/html/redaxo/bin/console -q -n package:install web_analytics
php /var/www/html/redaxo/bin/console -q -n package:activate web_analytics

exec docker-entrypoint.sh "$@"
