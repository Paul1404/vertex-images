# SVU WordPress image

This build supplies the SV Untereuerheim WordPress workload on Vertex RKE2.
Fleet manages the deployment, its persistent `/var/www/html` volume and the
separate MariaDB workload. CloudFront reaches it through the protected Vertex
Gateway. The `railway-` directory name is retained for the existing build and
release automation.

Apache uses prefork. Preserve the existing table prefix and
`https://sv-untereuerheim.de` site URL, and never replace populated site data
with an empty volume. Runtime credentials and site data are outside Git.
