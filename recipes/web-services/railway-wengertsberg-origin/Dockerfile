FROM caddy:2.11.9-builder-alpine@sha256:646fee578e680989ca5c7fd1ce6f1de574d19fd71ef2221810cc0510a9f40c86 AS caddy-builder

RUN xcaddy build v2.11.9 \
    --replace github.com/go-jose/go-jose/v4=github.com/go-jose/go-jose/v4@v4.1.6 \
    --replace golang.org/x/net=golang.org/x/net@v0.62.0 \
    --output /usr/bin/caddy

FROM caddy:2.11.9-alpine@sha256:003a97808e781aa9f7e75cc2f43d34d461099031faf5e20faefb9f61126836f0

ARG SECURITY_REBUILD=local

RUN test -n "$SECURITY_REBUILD" && apk upgrade --no-cache

COPY --from=caddy-builder /usr/bin/caddy /usr/bin/caddy

COPY Caddyfile /etc/caddy/Caddyfile
COPY entrypoint.sh /usr/local/bin/wengertsberg-origin-entrypoint
RUN chmod 755 /usr/local/bin/wengertsberg-origin-entrypoint

ENTRYPOINT ["/usr/local/bin/wengertsberg-origin-entrypoint"]
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
