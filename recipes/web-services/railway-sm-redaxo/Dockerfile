FROM friendsofredaxo/redaxo@sha256:34144244f37dcd410e59437219a4425fab8a506bb4e12cf3892985c127e1cbd3

# Use the source commit to refresh the package-update layer.
ARG SECURITY_REBUILD=local
RUN test -n "$SECURITY_REBUILD" \
    && apt-get update -o APT::Update::Error-Mode=any \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -o Dpkg::Options::=--force-confold \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# PHP uses prefork; loading the event MPM as well prevents Apache starting.
RUN a2dismod mpm_event \
    && a2enmod mpm_prefork \
    && apache2ctl -t

COPY analytics /usr/local/share/site-analytics
RUN php -l /usr/local/share/site-analytics/boot.php

COPY entrypoint.sh /usr/local/bin/redaxo-railway-entrypoint
COPY railway-health.php /usr/local/share/railway-health.php
RUN php -l /usr/local/share/railway-health.php
RUN chmod 755 /usr/local/bin/redaxo-railway-entrypoint

ENTRYPOINT ["/usr/local/bin/redaxo-railway-entrypoint"]
CMD ["apache2-foreground"]

COPY healthz.conf /etc/apache2/conf-available/railway-health.conf
RUN a2enmod alias && a2enconf railway-health && apache2ctl -t
