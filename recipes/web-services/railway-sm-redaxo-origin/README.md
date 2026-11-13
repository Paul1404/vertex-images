# Schlossmühle Caddy origin fixture

Historical only. The active CloudFront origin is the protected Vertex Gateway. Keep this context for the retired Railway proxy and redirect tests; do not use it as deployment guidance.

`/healthz` is public; other paths require `X-SM-Origin-Key`. The proxy forwards REDAXO requests to the canonical HTTPS host. The redirect function preserves the path and query when sending `www` to the apex.
