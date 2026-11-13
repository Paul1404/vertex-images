# Stalwart image

Builds Stalwart 0.16.27 from upstream commit `aa47d8ef7bfba7200d3293198ac2592747b20e73` with the legacy-password patch used on mx. The workflow runs the patch's synthetic authentication tests, builds the default RocksDB and enterprise features, scans the image and publishes the tested image with provenance.

The locked OpenTelemetry commit is fetched from its upstream repository because the Stalwart fork is no longer available. The revision in `Cargo.lock` stays unchanged.

Publication accepts a newer `main` only when the Stalwart recipe, workflow and scan policy are unchanged since the build.

This prepares an image; mx continues to use its existing pinned image. A rebuilt binary will not necessarily match the installed binary byte for byte.
