# Security changes since import

`import.json` remains the record of the original source files. The initial CMS image scan is retained in [run 43292632914](https://github.com/Paul1404/vertex-images/actions/runs/43292632914). Current images must pass the policy in `cms.yml`; fixable HIGH and CRITICAL findings block publication.

## CMS application images

The three application Dockerfiles update Debian packages on each reviewed commit. `cms.yml` passes that commit as `SECURITY_REBUILD`, invalidating the package-update layer when the recipe changes.

The WordPress images retain the `wordpress:7.1.3` base and their PHP, theme and prefork contracts. REDAXO uses the official stable image at digest `34144244f37dcd410e59437219a4425fab8a506bb4e12cf3892985c127e1cbd3` (REDAXO 5.21.6, PHP 8.4). It bundles Symfony 7.4.21.

These image scans cover files inside the image. They do not update or scan persisted CMS cores, plugins, add-ons, media, content or databases. Entrypoints continue to preserve those volumes and refresh only files owned by the image. Runtime updates require a separate backup and application verification.

## Historical Caddy fixtures

The three retired origin fixtures use the official Caddy 2.11.9 patch release. Pinned builder and runtime images compile Caddy with Go 1.27.4 and xcaddy 0.4.7. Module-wide replacements select go-jose/v4 4.1.6 and x/net 0.62.0; the runtime stage upgrades Alpine packages. Recheck the replacements on Caddy updates.

References: [official REDAXO image](https://github.com/FriendsOfREDAXO/docker-redaxo), [official Caddy images](https://hub.docker.com/_/caddy), [Caddy 2.11.9 release](https://github.com/caddyserver/caddy/releases/tag/v2.11.9), [Caddy dependencies](https://github.com/caddyserver/caddy/blob/v2.11.9/go.mod).

## Recovery archives

CMS builds publish one AMD64 manifest. The fresh publisher creates signed provenance separately. Fleet checks the manifest, config and every archived layer against the signed config's ordered rootfs diff IDs before adopting recovery metadata.
