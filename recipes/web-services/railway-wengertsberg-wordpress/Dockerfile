FROM wordpress:7.1.3

# Keep a smaller idle Apache pool while preserving the existing request ceiling.
COPY mpm_prefork.conf /etc/apache2/mods-available/mpm_prefork.conf
COPY theme /usr/src/wengertsberg-theme
COPY build-theme-assets.sh /usr/local/bin/wengertsberg-build-assets
RUN sh /usr/local/bin/wengertsberg-build-assets /usr/src/wengertsberg-theme
RUN for file in /usr/src/wengertsberg-theme/*.php; do php -l "$file" || exit 1; done

# The amd64 variant currently enables both Apache MPMs. PHP's prefork MPM is
# required; loading event alongside it makes Apache fail before WordPress starts.
RUN a2dismod mpm_event \
    && a2enmod mpm_prefork \
    && apache2ctl -t

COPY analytics /usr/local/share/site-analytics
RUN php -l /usr/local/share/site-analytics/99-web-analytics.php

COPY entrypoint.sh /usr/local/bin/wengertsberg-entrypoint
COPY railway-health.php /usr/local/share/railway-health.php
RUN php -l /usr/local/share/railway-health.php
RUN chmod 755 /usr/local/bin/wengertsberg-entrypoint

ENTRYPOINT ["wengertsberg-entrypoint"]
CMD ["apache2-foreground"]

COPY healthz.conf /etc/apache2/conf-available/railway-health.conf
RUN a2enmod alias && a2enconf railway-health && apache2ctl -t
