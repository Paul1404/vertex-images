# Reviewed changes after the public-source import

The original file hashes and upstream commit remain in `import.json`. Do not
rewrite that baseline to conceal later changes.

The first hosted CMS migration run, `43292632914`, passed all six functional
fixtures and failed all six newly introduced vulnerability gates. The complete
reports remain attached to that run. This is evidence about the original images,
not a passing scan for the changed recipes below.

## Active CMS images

All three application Dockerfiles now refresh Debian distribution packages using
`apt-get update` and a noninteractive `apt-get upgrade`, preserve existing package
configuration, and remove package caches and lists afterward. `SECURITY_REBUILD`
is supplied as the exact hub commit by `cms.yml`, so a new reviewed source commit
invalidates the security-update layer even if its Dockerfile base is unchanged.

The initial WordPress reports identified fixable high and critical findings in
Apache 2.4.69 (fixed in 2.4.71), apt 3.0.3 (3.0.4), ImageMagick Debian revisions,
linux-libc-dev and zlib. Both WordPress recipes retain their original
`wordpress:7.1.3` base and the existing PHP, theme, entrypoint and prefork contracts.
The new hosted build and scan must establish which fixes are actually available
from the configured distribution repositories.

REDAXO also had vulnerable Symfony components in its bundled source image;
upgrading Debian packages cannot fix those PHP dependencies. Its base is changed
from digest `212699c8ec07f5e7bd9d8f52458a919671450627f77e2165e805f057b67f767c`
to the official stable REDAXO 5 image digest
`34144244f37dcd410e59437219a4425fab8a506bb4e12cf3892985c127e1cbd3`.
The upstream stable Dockerfile identifies REDAXO 5.21.6 and PHP 8.4. Inspecting the
published amd64 image's bundled Composer metadata confirmed
`symfony/http-foundation` and `symfony/yaml` at 7.4.21, above the report's required
7.4.19 and 7.4.18 fixes. No dependency suppression or vulnerability-policy change
is used. The PHP and REDAXO major lines are preserved.

Sources inspected on 2026-11-12:
[official REDAXO image source](https://github.com/FriendsOfREDAXO/docker-redaxo/blob/main/images/5-stable/Dockerfile),
[official image documentation](https://github.com/FriendsOfREDAXO/docker-redaxo).
The manifest digest and Composer versions were independently read from the public
registry image. Local execution of that amd64 image was unavailable because the
local Docker daemon did not provide amd64 execution; the hosted fixture and scan
jobs must verify the changed image before publication.

## Persistent CMS data boundary

A clean image scan covers the published image's files. It does not cover the
existing `/var/www/html` volume, persisted REDAXO core and addons, WordPress
plugins, editorial content or database. The entrypoints continue updating only
owned health, analytics and theme assets. A new base image does not imply an
upgrade of the persisted REDAXO installation. No customer core, configuration,
content or database is changed to satisfy the image scan. Runtime CMS and plugin
updates require their own reviewed backup and application verification workflow.

## Historical Caddy origin fixtures

The three historical origin recipes use the official Caddy 2.11.9 patch release
and pinned builder/runtime multiarchitecture index digests. The builder was
verified with Go 1.27.4 and xcaddy 0.4.7. Caddy is rebuilt with module-wide
replacements for go-jose/v4 4.1.6 and x/net 0.62.0, then its runtime Alpine
packages are upgraded using the same commit-keyed security argument. Revisit
these temporary module overrides whenever Caddy is updated; do not pin an older
replacement over a newer upstream fix. No origin runtime is being redeployed.

All three contexts built locally for ARM64. The production-target AMD64 fixtures
and full vulnerability scans must still pass on hosted runners. References:
[official Caddy images](https://hub.docker.com/_/caddy),
[Caddy 2.11.9 release](https://github.com/caddyserver/caddy/releases/tag/v2.11.9),
[upstream dependency baseline](https://github.com/caddyserver/caddy/blob/v2.11.9/go.mod).

## Recovery identity

CMS builds explicitly produce one AMD64 manifest without BuildKit's automatic
provenance index. The fresh publisher emits signed GitHub provenance separately.
Recovery config IDs are derived from the actual saved config bytes and registry
manifest, because Docker 29's containerd store can report a manifest or index as
its inspect ID. Private Fleet verifies every archived layer against the signed
config's ordered rootfs diff IDs before adopting its recovery metadata.
