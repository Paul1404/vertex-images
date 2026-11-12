# SVU historical Caddy origin

> Historical configuration: the active CloudFront origin is the protected Vertex
> Gateway. This Caddy build is not the current production route. The details
> below describe the retired Railway arrangement and must not be used as live
> deployment instructions.

This small Caddy service is the public origin for the existing
`sv-untereuerheim.de` CloudFront distribution. WordPress and MariaDB stay
private on Railway. `ORIGIN_VERIFY` must match CloudFront's
`X-SVU-Origin-Key` custom origin header. Never log or commit its value.

CloudFront uses the Railway-generated `*.up.railway.app` domain and the
managed `AllViewerExceptHostHeader` origin request policy on **all** cache
behaviors, including `/wp-content/*` and `/wp-includes/*`. The former SSH host
is retired; its old origin records are not a supported rollback path.
Caddy sends the canonical `sv-untereuerheim.de` Host and HTTPS indication to
WordPress. Never remove the Railway service domain while CloudFront uses it.

Only `/healthz` works without the origin verification header. A direct request
to any other path must return 403. After changes, verify public pages, static
assets, and an authenticated editor session. Recovery requires verified database
and website-file backups, not the old Compose host.
