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

The three sites adopted the hub release at
`ff9dfd1cdd29c53c0a17c0a4dad6f852d735faa8` on 2026-11-12 after
[the main CMS pipeline](https://github.com/Paul1404/vertex-images/actions/runs/43295202395)
passed all source, fixture, scan and publication gates. The private Fleet
consumer independently verified the signed image configuration, every recovery
layer and all three release records before updating the intended image pins,
release headers and application recovery metadata. Database and historical
origin recovery entries and all persistent volume identities were preserved.

Live pod image IDs matched the published digests. All three public homepages
and database-backed health checks returned 200 with the new release header;
all three protected origins returned 403 without credentials. The independent
[published-digest scan](https://github.com/Paul1404/vertex-images/actions/runs/43297718826)
also passed. Fixable HIGH/CRITICAL findings block delivery; findings with no
scanner-listed fix remain visible in the full reports. Image scans do not cover
persisted CMS cores, addons, plugins or customer content.

The old wrapper's two publishers are disabled. Its source history, release
archives and registry digests remain available for recovery; archival is pending
the owner's decision. Active recipe and theme changes belong here. Deployment
credentials and desired-state promotion remain private.

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

Authenticated production CMS administration, contact email receipt and a fresh
restoration were not exercised during this image-only migration. The existing
isolated fixtures exercise synthetic CMS login and restart persistence. Detailed
timing and live-readback evidence are retained in the private operational record;
no latency speedup or byte-for-byte build reproducibility is claimed.
