FROM wordpress:7.1.3

# Use the source commit to refresh the package-update layer.
ARG SECURITY_REBUILD=local
RUN test -n "$SECURITY_REBUILD" \
    && apt-get update -o APT::Update::Error-Mode=any \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -o Dpkg::Options::=--force-confold \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Keep a smaller idle Apache pool while preserving the existing request ceiling.
COPY mpm_prefork.conf /etc/apache2/mods-available/mpm_prefork.conf

# The amd64 image can enable both Apache MPMs; PHP needs prefork only.
RUN a2dismod mpm_event \
    && a2enmod mpm_prefork \
    && apache2ctl -t

COPY analytics /usr/local/share/site-analytics
RUN php -l /usr/local/share/site-analytics/99-web-analytics.php

COPY entrypoint.sh /usr/local/bin/svu-wordpress-entrypoint
COPY railway-health.php /usr/local/share/railway-health.php
RUN php -l /usr/local/share/railway-health.php
RUN chmod 755 /usr/local/bin/svu-wordpress-entrypoint

ENTRYPOINT ["svu-wordpress-entrypoint"]
CMD ["apache2-foreground"]

COPY healthz.conf /etc/apache2/conf-available/railway-health.conf
RUN a2enmod alias && a2enconf railway-health && apache2ctl -t
