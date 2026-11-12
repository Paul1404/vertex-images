# Schlossmühle historical Caddy origin

> Historical configuration: the active CloudFront origin is the protected Vertex
> Gateway. This Caddy build is not the current production route. The details
> below describe the retired Railway arrangement and must not be used as live
> deployment instructions.

This Caddy service receives traffic from the existing
`schlossmuehle-untereuerheim.de` CloudFront distribution and reaches REDAXO
on Railway's private network. Only `/healthz` is public without the
`X-SM-Origin-Key` header. `ORIGIN_VERIFY` must equal the value of CloudFront's
custom origin header; never log or commit it.

CloudFront must use this service's generated `*.up.railway.app` domain and
the managed `AllViewerExceptHostHeader` origin request policy on the default
behavior and all three static behaviors (`/media/*`, `/assets/*`,
`/template/*`). Preserve the existing WAF, certificate, and cache policies.
Do not delete the Railway-generated domain. The former SSH host is retired;
old origin DNS records are not a supported rollback path.

The existing site redirects `www` to the apex. The viewer-request CloudFront
Function in `cloudfront-www-redirect.js` preserves that behavior and query
parameters on all four cache behaviors. It must be tested before association.
After a cutover, verify public HTML, template CSS and JS, media, the REDAXO
backend, direct-origin denial, and a successful CloudFront invalidation.
