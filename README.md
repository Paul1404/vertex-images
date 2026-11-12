# Vertex images

Public build orchestration for allowlisted public application sources. Deployment configuration, runtime secrets and Fleet write access belong in a separate private repository.

The allowlisted public static sites are `Paul1404/hof-stetten.de` and `Paul1404/untereuerheim.com`, published as `ghcr.io/paul1404/vertex-hofstetten` and `ghcr.io/paul1404/vertex-untereuerheim`. Hofstetten is the first deployment pilot. During shadow verification, its existing CI, publisher and production promotion gates remain in place until measured evidence supports migration.

## Delivery contract

`build.yml` runs manually, on `source-ci-passed` repository dispatch, and on a ten-minute polling schedule. Dispatch payloads never select a repository or source ref. The planner independently resolves the allowlisted repository's current main commit and requires its newest exact-commit `ci.yml` push run to have completed successfully. It rejects private, archived and non-main-default sources. Only main in this hub can publish.

Each selected workload calls `image.yml` with its trusted planner result and gets its own build and publishing runners. The matrix permits four concurrent workload pipelines and does not cancel other workloads on failure. Each publisher depends only on its own successful build, so a slow or failed image does not hold back another image. The reusable workflow checks the calling repository, main branch and allowed trigger events before executing source code; its source runner explicitly has read-only permissions. The caller permits the reusable publisher to request package and attestation privileges, while those privileges remain absent from its source runner.

The source runner checks out an exact full SHA without persisted credentials and has read-only token permissions. It installs pinned Bun 1.3.11, uses the frozen dependency lockfile, and runs dependency audit, source checks, the source's image vulnerability policy, unit tests against built site output and production HTTP smoke checks including origin authentication. Trivy scans all vulnerability severities and generates a CycloneDX SBOM. The source policy blocks fixable HIGH/CRITICAL vulnerabilities and remains authoritative. This scan covers publication time. Existing source-repository weekly scans rebuild their own image and do not rescan the exact hub digest. Before retiring those workflows, add a weekly hub scan that retrieves each latest successful delivery record, validates its trusted source/recipe association, scans that immutable digest without rebuilding and fails under the same pinned source policy; retain the full report and surface failures for review. No runtime secrets or private configuration are supplied.

A fresh publishing runner downloads the tested image tar from this run. It executes no source scripts, rechecks current main and latest successful source CI, and publishes with this repository's ephemeral `GITHUB_TOKEN`. Packages write and OIDC/attestation privileges exist only in this job. PRs only run read-only planner unit tests and never run publication. There is no `pull_request_target` or PR-triggered privileged workflow.

Tags contain both exact revisions:

```
sha-{40-character-source-commit}-recipe-{40-character-hub-commit}
```

Existing tags are never overwritten. A failed publisher job can be rerun while its one-day tested-image artifact remains: an existing remote image is reused only if its config digest matches the tested tar, allowing missing provenance to be repaired. If artifacts expired, retain the existing tag and use a new reviewed recipe commit. A manifest published before an attestation failure is skipped by later polling; rerun that failed publisher explicitly and do not promote it until provenance is present.

Publication produces signed GitHub build provenance on the image digest. The source revision and repository are OCI labels, and `net.pdcd.vertex.recipe` records this hub's revision. The provenance signer is `.github/workflows/image.yml` and attests the hub workflow and recipe, not a checkout of the application as the workflow repository. The `evidence-{workload}` artifact contains `delivery.json` associating source SHA, recipe SHA, source CI run, hub run and digest, plus full vulnerability report and SBOM. Fleet must independently verify that association, trusted workflow/main/run success, exact source CI success and the signed digest before changing its pinned image. The hub holds no Fleet credential.

Package visibility defaults to private on first publication. Explicitly make only this public-source pilot package public, then verify an anonymous pull by digest before enabling Fleet adoption. Public repo visibility does not establish public package visibility.

## Reproducibility and privacy boundaries

Exact source, recipe, lockfile and action commits provide traceability. The inherited source Dockerfile currently uses mutable base tags and package upgrades; this pilot does not claim byte-for-byte reproducibility. Pin bases by digest and snapshot package inputs in a reviewed source change before claiming it. A source plus recipe pair is built once and reused by digest.

Private application sources and private platform adapters remain in private build workflows, which may call reviewed shared logic but retain private runners' billing and visibility boundaries. Do not copy private source, build inputs, config, credentials or customer data here for free capacity. Public logs, artifacts, SBOMs, image layers and caches are public disclosure surfaces. No private repository token is installed here. Build secrets, if ever required, need a separate private workflow and BuildKit secret mounts rather than build arguments or copied files.

The ten-minute poll avoids cross-repository credentials. For faster source notification, a narrowly scoped GitHub App may dispatch `source-ci-passed` after trusted main CI; store its private key only in the trusted source notification job and restrict its installation to this hub. Do not give notification credentials to PR jobs. The planner ignores payload refs and repeats all trust checks. Scheduled Actions can be delayed and are not a delivery SLA.

## Capacity and costs

Standard public GitHub-hosted runner compute is currently free. It is subject to plan concurrency limits: Free 20, GitHub Pro 40, Team 60, Enterprise 500, shared with other workloads of the account. GPT Pro does not change GitHub's plan. Standard public Ubuntu runners currently provide 4 CPUs, 16 GB RAM and 14 GB disk. Hosted jobs have a six-hour hard maximum and matrices a 256-job maximum. Larger runners are billed even for public repositories. GHCR container storage and bandwidth are currently free, while Actions artifact/cache storage has separate limits. This pilot keeps image artifacts for one day and evidence for fourteen days.

Verified against official documentation on 2026-11-12: [limits](https://docs.github.com/en/actions/reference/limits), [runner capacity](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [Packages billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages), [secure use](https://docs.github.com/en/actions/reference/security/secure-use).

## Verification and measurement

Run `python3 -m unittest discover -s tests -v`. Tests cover exact successful main selection, untrusted events, changed SHA, pending/newer failed runs, wrong workflow/repository, private sources, unknown workloads and deduplication.

Record source commit time, upstream CI start/end, hub queue/build/publish start/end, Fleet promotion commit and live readiness separately. Report wall time and runner job time; compare equivalent cold/warm runs before removing duplicated image work. Polling overhead, source CI and independent production gates remain part of delivery latency. A successful build alone does not establish deployment or a speedup.
