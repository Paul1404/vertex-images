# Website image recipes

These public recipes were imported from `Paul1404/web-services` at commit
`1589e2e7acd72f5ac7f9351571ffd3de7f1ae4d0`. `import.json` records the original
Git blob and SHA-256 of each copied file. Original notices and per-context
README files remain intact. This move does not grant additional rights to the
original code; upstream components retain their own licenses.

The three CMS application contexts are `railway-sm-redaxo`,
`railway-svu-wordpress`, and `railway-wengertsberg-wordpress`. The historical
names keep Docker and fixture paths compatible. They run on Vertex, and do
not describe the deployment provider. Three Caddy origin contexts remain for
source and fixture coverage; they do not represent active origin deployments.

From the hub checkout:

```sh
bash recipes/web-services/source-checks.sh
cd recipes/web-services
docker build --pull -t local/cms:test railway-sm-redaxo
python3 tests/release-smoke.py railway-sm-redaxo local/cms:test
```

The same build and smoke commands accept any of the six historical context
names. The fixtures create isolated Docker networks and volumes with synthetic
data and remove them afterward. Keep all fixture files: the WordPress tests
also mount the historical Wengertsberg seed. Do not run fixture setup against
a production volume or database.

Wengertsberg's managed theme, contact handler, SEO code and hashed assets are
part of its image context. The historical `site-content.html` is a disposable
fixture input. Current editorial pages, WordPress options and media are stored
on persistent volumes and must never be replaced from that seed. Preserve the
owned theme and analytics assets without replacing other site data.

REDAXO must refuse an empty production installation. Its migration hold remains
an explicit data-migration operation. Preserve prefork Apache, port 80,
database-backed `/healthz`, restart persistence, editor login, protected-origin
behavior, and analytics consent tests.

Runtime credentials, customer records, website uploads and database contents
are not build inputs. Deployment resources, secret references, release headers
and desired-state changes belong to the private `vertex-fleet` repository.
The old publishing/promotion scripts and Fleet deploy key were not imported.
The redirect source under `railway-sm-redaxo-origin` remains source/test material;
copying it does not apply CloudFront changes.

`import.json` is historical import evidence. Future reviewed edits use the hub
commit as their source revision; update provenance rather than pretending that
modified files still match their original source blobs. The REDAXO base is
pinned by digest. WordPress currently retains its reviewed version tag, so a
rebuild is not a claim of byte-for-byte reproducibility. Record resolved base
materials and scan each candidate before production promotion.
