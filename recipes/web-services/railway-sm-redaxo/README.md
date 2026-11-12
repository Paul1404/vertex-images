# Schlossmühle REDAXO image

This build supplies the Schlossmühle REDAXO workload on Vertex RKE2. Fleet
manages the deployment, its persistent `/var/www/html` volume and the separate
MariaDB workload. CloudFront reaches it through the protected Vertex Gateway.
The `railway-` directory name is retained for existing build and release
scripts. The image pins an immutable Friends Of REDAXO digest and uses Apache
prefork rather than the event MPM.

`REDAXO_MIGRATION_HOLD=1` runs an idle process for an explicitly authorized
migration. After copying site files and database data, set it to `0`. The
entrypoint refuses an empty volume and uses REDAXO's `db:set-connection` to
apply the configured database connection. Never print or commit credentials.
Do not run independent writers against the same site data.
