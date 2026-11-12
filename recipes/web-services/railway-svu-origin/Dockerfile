FROM caddy:2.11.6-alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY entrypoint.sh /usr/local/bin/svu-origin-entrypoint
RUN chmod 755 /usr/local/bin/svu-origin-entrypoint

ENTRYPOINT ["/usr/local/bin/svu-origin-entrypoint"]
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
