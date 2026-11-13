# Vertex images

Vertex images builds the containers for several of my websites and services. It produces tested images with traceable source revisions. The private Fleet repositories hold deployment configuration and runtime secrets.

The repository does not deploy anything itself. Fleet decides which verified digest to run on Vertex; mail remains on its own host.

## Images

| Image | Source | Build |
| --- | --- | --- |
| `vertex-hofstetten` | [hof-stetten.de](https://github.com/Paul1404/hof-stetten.de) | Static site |
| `vertex-untereuerheim` | [untereuerheim.com](https://github.com/Paul1404/untereuerheim.com) | Static site |
| `vertex-cms-sm`, `vertex-cms-svu`, `vertex-cms-wengertsberg` | [CMS recipes](recipes/web-services/) | REDAXO and WordPress sites |
| `vertex-paperless-ai-hub` | [Paperless AI adapter](recipes/paperless-ai/) | Document extraction adapter |
| `vertex-stalwart` | [Stalwart recipe](recipes/stalwart/) | Stalwart 0.16.27 with the mx legacy-password patch |

The Stalwart workflow prepares an image independently of the running mail service.

## From source to image

For the two static sites, the planner looks for a successful CI run on the source repository's current `main` commit. It checks every ten minutes and can also be triggered manually or by a source notification. The builder checks out that exact commit, runs the source checks, builds the image once, tests it and scans its packages. Fixable high and critical vulnerabilities stop publication.

A separate publisher takes the tested image, checks that the source hasn't moved, and pushes it to GHCR. Image tags contain both the source and builder commits, and GitHub attests the resulting digest. Fleet checks the publisher and provenance before changing its image pin.

The CMS, Paperless AI and Stalwart recipes live in this repository and have their own workflows. The CMS workflow tests six contexts and publishes the three application images. It also keeps a checksum-verified image archive for each release. The Paperless adapter and Stalwart workflows test and scan their images before publication. Pull requests build and test; only `main` publishes.

The weekly security workflow rescans published static-site and CMS images. It can inspect a newer release than the one Fleet currently runs.

## Working here

Run the image planner and policy tests:

```sh
python3 -m unittest discover -s tests -v
```

For changes to the CMS recipes, also run:

```sh
bash recipes/web-services/source-checks.sh
```

The [CMS recipe guide](recipes/web-services/README.md) covers its fixtures and image archives. The [Stalwart recipe](recipes/stalwart/README.md) describes the patched build.

Keep runtime configuration, credentials and private data out of this repository, its build logs and image artifacts. Source and recipe revisions identify what was built; mutable upstream packages can still produce different image bytes on a later rebuild.
