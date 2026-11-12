# CMS recipe ownership migration

`recipes/web-services` contains the complete public build inputs and synthetic
functional fixtures for the three CMS images formerly built by
`Paul1404/web-services`. Original input provenance is recorded in its import
manifest. The managed Wengertsberg theme is included; private configuration,
site data and the old Fleet-key publisher are excluded.

Six contexts retain functional verification: three CMS applications and three
historical Caddy origins. Only the active CMS images are publication candidates.
Source checks, secret scanning, functional tests, vulnerability policy and
isolated publication must pass before promotion. No origin deployment is revived.

The source repository's existing publishers and branch gates remain active
during validation. The private Fleet consumer owns eventual digest promotion.
It must verify the hub publisher identity, exact source/recipe commit, tested
image identity and signature, then update only the intended site's image,
release header and source metadata. Prior image archive URLs and hashes remain
valid recovery provenance.

The initial production rollback references are:

| Site | Existing image |
| --- | --- |
| Schlossmuehle | `ghcr.io/paul1404/web-services-sm-redaxo@sha256:a003baaa0cb1ec913d61265a6fc0e45ed04921001010c560b37d891d40863e31` |
| SV Untereuerheim | `ghcr.io/paul1404/web-services-svu-wordpress@sha256:978bd5b7d8c921e9d77eb72a0926467a38e031fa1922ae80484d8c8abc4b8a14` |
| Wengertsberg | `ghcr.io/paul1404/web-services-wengertsberg-wordpress@sha256:85df557b83a6017c552766f1b10700a843c1c189acb024f7366089539ddc74d6` |

Archive the old wrapper only after all three new images pass the original CMS
fixtures and scans, independent registry/signature checks, private promotion,
Fleet reconciliation and canonical HTTPS/protected-origin readback. Preserve
all existing persistent data and old registry digests. Disable duplicate old
publishers and retire their scoped deploy key after replacement promotion works.
Keep historical releases and tags because recovery metadata still references them.

Migration verification is ongoing. Local source/import checks do not establish
GitHub build success, production adoption, authenticated CMS operation, contact
email receipt or restoration. Record measured Actions and live-readback evidence
when each stage completes.
