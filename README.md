# Vertex images

This repository builds and publishes images for allowlisted public projects. Runtime configuration, secrets and deployment changes stay in private repositories.

## Public application images

The current allowlist is `Paul1404/hof-stetten.de` and `Paul1404/untereuerheim.com`, published as `ghcr.io/paul1404/vertex-hofstetten` and `ghcr.io/paul1404/vertex-untereuerheim`.

`build.yml` polls every ten minutes and also supports manual and `source-ci-passed` runs. Scheduled runs can be delayed. Immediate source notifications need a scoped GitHub App to send `source-ci-passed`. Its planner ignores dispatch payload refs, resolves an allowlisted repository's current `main` commit, and requires that commit's latest `ci.yml` push run to pass. Only this repository's `main` branch publishes images.

Each workload uses `image.yml`. The build runner checks out the exact source commit with read-only permissions, runs source checks, vulnerability scans and application smoke tests, then saves the tested image. Fixable HIGH and CRITICAL findings block publication. A fresh publisher reuses that image, rechecks the source commit and CI result, publishes an immutable tag of `sha-{source}-recipe-{hub}`, and attests its digest. The publisher check is named `image-{workload} / publish`; Fleet verifies that specific job.

Pull requests run repository tests and the CMS checks below; they cannot publish. Existing tags are never overwritten. A failed publisher can be rerun while its one-day tested-image artifact remains. If an image was pushed but its attestation failed, do not promote it until the publisher is rerun and provenance verifies. If the artifact has expired, use a new recipe commit. Verify anonymous pulls by digest before enabling Fleet promotion. The `evidence-{workload}` artifact records source and recipe commits, CI runs, image digest, vulnerability report and SBOM.

`security.yml` scans the newest published digest weekly or by manual dispatch. It verifies the workload's publisher, provenance, source labels and vulnerability policy. The scan pulls the image without running it. It may scan a newer image than the one currently deployed; Fleet's deployed-image checks remain separate.

## CMS images

The public CMS recipes are under `recipes/web-services`. `cms.yml` runs secret scanning, source checks and all six fixture contexts. It publishes only the three CMS application images, `vertex-cms-sm`, `vertex-cms-svu` and `vertex-cms-wengertsberg`; the retired Caddy origins remain test fixtures.

Each application is built once. A fresh `cms-image.yml` publisher publishes the tested image, its digest provenance and a recovery archive. Recovery releases are named `cms-{site}-{commit}` and contain the Docker archive, SHA256 checksum and `release.json` metadata. The archive contains image files only. It does not include production data or runtime configuration. Fleet independently verifies the image and archive before updating its desired state. See [the migration record](docs/cms-migration.md) and [the recipe guide](recipes/web-services/README.md).

## Maintenance

Run the planner and policy tests with:

```sh
python3 -m unittest discover -s tests -v
```

Run CMS source checks with:

```sh
bash recipes/web-services/source-checks.sh
```

Source and recipe commits are recorded in image tags and labels. The public source Dockerfiles may use mutable base tags or package repositories, so the tag records provenance but does not promise byte-for-byte reproducibility. Public logs, artifacts, image layers and caches must contain no private source, credentials, customer data or deployment configuration.

Capacity checked on 2026-11-12: standard public runner compute and GHCR storage
and bandwidth are free. Concurrent jobs are shared across the account: Free 20,
GitHub Pro 40, Team 60, Enterprise 500. Public Ubuntu runners have 4 CPUs, 16 GB
RAM and 14 GB disk; hosted jobs are limited to six hours and matrices to 256 jobs.
Larger runners are paid. Artifact/cache allowances are separate; tested images
are retained for one day and reports for fourteen days. See GitHub's
[limits](https://docs.github.com/en/actions/reference/limits),
[runner specifications](https://docs.github.com/en/actions/reference/runners/github-hosted-runners),
[Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
and [Packages billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages).
