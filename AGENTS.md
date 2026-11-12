# Vertex images guidance

This public repository accepts only explicit public-source allowlists. Never add private source inputs, Fleet write credentials, customer data or runtime secrets. Preserve source main CI and vulnerability gates. PR workflows are read-only; publishing is main-only on fresh runners using ephemeral package credentials. Use full verified action commit SHAs, not annotated tag object IDs.

Run `python3 -m unittest discover -s tests -v`. Build recipes live in `.github/workflows/build.yml`; planner and allowlist live in `scripts/plan.py`. Tags identify full source and recipe revisions and must never be overwritten. Production promotion belongs to the private Fleet repository and pins verified image digests. Document measured delivery results without assuming speedup or byte reproducibility.
