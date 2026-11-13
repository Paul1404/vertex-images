# CMS image adoption

On 2026-11-12, Schlossmuehle, SV Untereuerheim and Wengertsberg adopted CMS release `ff9dfd1cdd29c53c0a17c0a4dad6f852d735faa8`. The [CMS pipeline](https://github.com/Paul1404/vertex-images/actions/runs/43295202395) passed source checks, all six image fixtures, scans and publication. Private Fleet verified the signed image configurations, recovery layers and release metadata before updating the three image pins.

The live readback matched the published digests. All three homepages and database health checks returned 200 with the new release header. Protected origins returned 403 without credentials. The [published-digest scan](https://github.com/Paul1404/vertex-images/actions/runs/43297718826) passed as well.

## Rollback images

| Site | Previous image |
| --- | --- |
| Schlossmuehle | `ghcr.io/paul1404/web-services-sm-redaxo@sha256:a003baaa0cb1ec913d61265a6fc0e45ed04921001010c560b37d891d40863e31` |
| SV Untereuerheim | `ghcr.io/paul1404/web-services-svu-wordpress@sha256:978bd5b7d8c921e9d77eb72a0926467a38e031fa1922ae80484d8c8abc4b8a14` |
| Wengertsberg | `ghcr.io/paul1404/web-services-wengertsberg-wordpress@sha256:85df557b83a6017c552766f1b10700a843c1c189acb024f7366089539ddc74d6` |

Keep these digests, historical releases and archive metadata while recovery records reference them. The old publishers are disabled. Recipe and theme changes belong in this repository; deployment credentials and desired-state promotion remain in private Fleet.

Image scans do not cover persisted CMS cores, add-ons, plugins, media, database or editorial content. Authenticated production administration, contact-email receipt and a fresh restore were not exercised during this image migration. The isolated fixtures cover synthetic login and restart persistence.
