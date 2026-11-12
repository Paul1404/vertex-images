# CMS recipe guidance

Keep all six context directory names aligned with the workflows and
`tests/release-smoke.py`. Run `bash recipes/web-services/source-checks.sh` from
the hub root and exercise the affected production image with the disposable
CMS fixtures before shipping.

Preserve persistent `/var/www/html`, database/table identities, public URLs and
owned release behavior. Entrypoints refresh only owned readiness, analytics
and theme assets. They must not replace uploads, other themes, CMS configuration
or current editorial pages. REDAXO must refuse a missing migrated configuration.
Never run fixture setup or a historical seed against production storage.

Keep prefork Apache, port 80 and database-backed `/healthz`. WordPress fixtures
verify editor login, restart persistence and failed-database behavior. The
Wengertsberg theme's contact flow, SEO, public/review separation and hashed asset
paths remain functional requirements; source syntax checks alone are insufficient.

Keep three consent-loader copies identical. REDAXO uses its owned OUTPUT_FILTER
addon; WordPress uses its owned MU plugin. Preserve explicit consent, withdrawal,
DNT/GPC and exclusion of authenticated/review pages. Wengertsberg adapts loader
presentation through the theme rather than mutating shared loader semantics.

Historical origins are tested recipes, not desired-state deployments. No runtime
or Fleet credentials belong here. Production promotion and protected-origin
secret references are owned by private Fleet. Preserve source notices, import
provenance, old rollback image references and release assets when consolidating.
