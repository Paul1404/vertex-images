# Vertex images guidance

Build only allowlisted public sources. Keep private inputs, runtime secrets and
Fleet credentials out of this repository. Source and PR jobs are read-only;
publish from main on a separate runner. Preserve source CI and vulnerability
gates. Pin actions to commit SHAs, not annotated tag IDs.

`build.yml` plans external-source builds through `scripts/plan.py` and calls
`image.yml` for each workload. Keep source and recipe commits in tags and never
overwrite them. Consumers check each workload's publisher job, not the combined
workflow result. Private Fleet owns digest promotion.

`security.yml` scans published digests weekly and on demand. Its resolver is
`scripts/scan_target.py`; CMS entries go in `SCAN_CATALOG`, not the external
build allowlist. Run `python3 -m unittest discover -s tests -v` after edits.

CMS contexts are in `recipes/web-services`. Run
`bash recipes/web-services/source-checks.sh` and the affected image fixtures.
`cms.yml` requires source/secret checks and all six image checks before publishing.
Keep those PR check names. Historical origins are test fixtures, not deployments.
`cms-image.yml` publishes the tested archives, signatures and recovery assets.

The Paperless AI adapter is in `recipes/paperless-ai`. Run
`python3 -m unittest discover -s recipes/paperless-ai/adapter -p 'test_*.py'`.
Its workflow tests and scans the image before publishing it from main.

The Stalwart recipe builds the pinned upstream release with the mx legacy
password patch and its synthetic tests. Building an image does not deploy it.
