FROM friendsofredaxo/redaxo@sha256:212699c8ec07f5e7bd9d8f52458a919671450627f77e2165e805f057b67f767c

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
