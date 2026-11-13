# Wengertsberg Caddy origin fixture

Historical only. This Railway origin is retired; current traffic uses the protected Vertex Gateway. Keep the context for proxy and authentication tests.

Only `/healthz` is public. Other paths require `X-Wengertsberg-Origin-Key`. Caddy forwards the canonical `wengertsberg.de` host and HTTPS scheme to WordPress.
