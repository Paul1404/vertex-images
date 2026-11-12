#!/bin/sh
set -eu

# The build validates prefork, but the Railway runtime can expose event again.
# Enforce one MPM immediately before the upstream WordPress entrypoint runs.
if [ -e /etc/apache2/mods-enabled/mpm_event.load ]; then
    a2dismod mpm_event >/dev/null
fi

# WordPress lives on a volume. Keep the versioned theme in sync without
# replacing uploads, database content, other themes, or site configuration.
mkdir -p /var/www/html/wp-content/themes/wengertsberg
cp -R /usr/src/wengertsberg-theme/. /var/www/html/wp-content/themes/wengertsberg/
chown -R www-data:www-data /var/www/html/wp-content/themes/wengertsberg

cp /usr/local/share/railway-health.php /var/www/html/railway-health.php
chmod 644 /var/www/html/railway-health.php

# Refresh only owned analytics assets and the consent gate, never CMS content.
mkdir -p /var/www/html/site-analytics /var/www/html/wp-content/mu-plugins
cp /usr/local/share/site-analytics/consent.js /var/www/html/site-analytics/consent.js
cp /usr/local/share/site-analytics/99-web-analytics.php /var/www/html/wp-content/mu-plugins/99-web-analytics.php
chmod 644 /var/www/html/site-analytics/consent.js /var/www/html/wp-content/mu-plugins/99-web-analytics.php

exec docker-entrypoint.sh "$@"
