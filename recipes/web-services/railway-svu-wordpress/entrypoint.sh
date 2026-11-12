#!/bin/sh
set -eu

# Railway can expose the event MPM again when mounting the runtime volume.
if [ -e /etc/apache2/mods-enabled/mpm_event.load ]; then
    a2dismod mpm_event >/dev/null
fi

# The web root is persistent; refresh only this service-owned readiness probe.
cp /usr/local/share/railway-health.php /var/www/html/railway-health.php
chmod 644 /var/www/html/railway-health.php

# Refresh only owned analytics assets and the consent gate, never CMS content.
mkdir -p /var/www/html/site-analytics /var/www/html/wp-content/mu-plugins
cp /usr/local/share/site-analytics/consent.js /var/www/html/site-analytics/consent.js
cp /usr/local/share/site-analytics/99-web-analytics.php /var/www/html/wp-content/mu-plugins/99-web-analytics.php
chmod 644 /var/www/html/site-analytics/consent.js /var/www/html/wp-content/mu-plugins/99-web-analytics.php

exec docker-entrypoint.sh "$@"
