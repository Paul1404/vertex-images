# CMS image recipes

These public build contexts came from `Paul1404/web-services` at commit `1589e2e7acd72f5ac7f9351571ffd3de7f1ae4d0`. [import.json](import.json) records the original files and hashes; later hub changes are tracked in this repository. Upstream components retain their own licenses.

Three contexts build the active CMS images: `railway-sm-redaxo`, `railway-svu-wordpress` and `railway-wengertsberg-wordpress`. The three `*-origin` contexts remain for historical fixture coverage only. Their directory names are retained for build and release compatibility.

Run the source checks and one image fixture from the repository root:

```sh
bash recipes/web-services/source-checks.sh
cd recipes/web-services
docker build --pull -t local/cms:test railway-sm-redaxo
python3 tests/release-smoke.py railway-sm-redaxo local/cms:test
```

The smoke test accepts any of the six context names. It creates isolated networks, volumes and synthetic data, then removes them. Never run fixture setup against production storage.

CMS images keep the existing database and `/var/www/html` data. Entrypoints refresh only owned health, analytics and theme files. REDAXO refuses an empty installation. The Wengertsberg theme is deployed from this image, but page content, options and media remain in WordPress. `site-content.html` is an initial test seed; do not import it over editorial changes.

Runtime credentials and customer data are not build inputs. Deployment resources and secrets belong in private `vertex-fleet`. The historical redirect function is test material and does not apply CloudFront changes. See [the migration record](../../docs/cms-migration.md) and [security changes](SECURITY-DELTA.md).
