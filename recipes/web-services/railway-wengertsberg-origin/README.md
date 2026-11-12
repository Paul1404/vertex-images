# Wengertsberg historical Caddy origin

> Historical configuration: the active CloudFront origin is the protected Vertex
> Gateway. This Caddy build is not the current production route. The details
> below describe the retired Railway arrangement and must not be used as live
> deployment instructions.

This tiny Caddy service is the public origin for the existing
`wengertsberg.de` CloudFront distribution. WordPress and MariaDB stay on the
private Railway network. The service requires the `ORIGIN_VERIFY` variable,
which must match CloudFront's `X-Wengertsberg-Origin-Key` custom origin header.
Do not log or commit its value.

CloudFront uses this service's Railway-provided `*.up.railway.app` domain as
its origin and the managed `AllViewerExceptHostHeader` origin request policy.
The former SSH host is retired; its old origin record is not a supported
rollback path. Caddy sends the canonical
`wengertsberg.de` Host and HTTPS indication to WordPress. This prevents
WordPress from redirecting a request back to the public hostname in a loop.
Do not delete the Railway-provided service domain while CloudFront uses it.

`/healthz` is the only unauthenticated path on the origin. All other direct
requests return 403, including requests to the Railway-generated domain.
After DNS cutover, verify CloudFront HTTP 200, direct-origin HTTP 403, an
authenticated WordPress flow, and website-file and database integrity.
