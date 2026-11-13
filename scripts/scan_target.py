"""Find the latest published image and its source revision."""
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

from plan import ALLOWLIST, api

TAG = re.compile(r"sha-([a-f0-9]{40})-recipe-([a-f0-9]{40})")
HUB = "Paul1404/vertex-images"
SCAN_CATALOG = {
    **{name: {**entry, "build_workflow": "build.yml", "publisher_job": f"image-{name} / publish", "signer_workflow": "image.yml", "policy_path": "scripts/check-image-vulnerabilities.py", "events": ("schedule", "workflow_dispatch", "repository_dispatch")} for name, entry in ALLOWLIST.items()},
    **{f"cms-{site}": {"repository": HUB, "image": f"ghcr.io/paul1404/vertex-cms-{site}", "build_workflow": "cms.yml", "publisher_job": f"publish-cms-{site} / publish", "signer_workflow": "cms-image.yml", "policy_path": "scripts/check-image-vulnerabilities.py", "events": ("push", "workflow_dispatch"), "context": "recipes/web-services/" + {"sm": "railway-sm-redaxo", "svu": "railway-svu-wordpress", "wengertsberg": "railway-wengertsberg-wordpress"}[site]} for site in ("sm", "svu", "wengertsberg")},
}


class PublicRegistry:
    def __init__(self, image):
        self.package = image.removeprefix("ghcr.io/")
        try:
            with urllib.request.urlopen(f"https://ghcr.io/token?service=ghcr.io&scope=repository:{self.package}:pull", timeout=30) as response:
                self.token = json.load(response)["token"]
        except urllib.error.HTTPError as error:
            raise ValueError("Anonymous package access required; verify package is public") from error

    def request(self, suffix):
        request = urllib.request.Request(f"https://ghcr.io/v2/{self.package}/{suffix}", headers={"Authorization": "Bearer " + self.token, "Accept": "application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read(), response.headers

    def tags(self):
        tags = []
        suffix = "tags/list?n=100"
        while suffix:
            body, headers = self.request(suffix)
            tags.extend(json.loads(body).get("tags") or [])
            link = headers.get("Link", "")
            if not link:
                break
            target = link.split("<", 1)[1].split(">", 1)[0]
            prefix = f"/v2/{self.package}/"
            if not target.startswith(prefix) or not target[len(prefix):].startswith("tags/list?"):
                raise ValueError("Unexpected registry pagination target")
            suffix = target[len(prefix):]
        return tags

    def digest(self, tag):
        body, headers = self.request("manifests/" + tag)
        digest = "sha256:" + hashlib.sha256(body).hexdigest()
        if headers.get("Docker-Content-Digest") != digest:
            raise ValueError("Manifest digest did not match registry response")
        return digest


def resolve(name, fetch=api, registry_factory=PublicRegistry):
    if name not in SCAN_CATALOG:
        raise ValueError("Unknown workload")
    entry = SCAN_CATALOG[name]
    repo = entry["repository"]
    for repository in (repo, HUB):
        meta = fetch(f"repos/{repository}")
        if meta["private"] or meta["archived"] or meta["default_branch"] != "main":
            raise ValueError("Public active main repositories required")
    registry = registry_factory(entry["image"])
    candidates = []
    for tag in registry.tags():
        match = TAG.fullmatch(tag)
        if not match:
            continue
        source, recipe = match.groups()
        if repo == HUB and source != recipe:
            continue
        source_date = fetch(f"repos/{repo}/commits/{source}")["commit"]["committer"]["date"]
        recipe_date = fetch(f"repos/{HUB}/commits/{recipe}")["commit"]["committer"]["date"]
        candidates.append((source_date, recipe_date, tag, source, recipe))
    for _, _, tag, source, recipe in sorted(candidates, reverse=True):
        # Only scan commits reachable from main.
        if any(fetch(f"repos/{repository}/compare/{sha}...main")["status"] not in ("ahead", "identical") for repository, sha in ((repo, source), (HUB, recipe))):
            continue
        runs = fetch(f"repos/{HUB}/actions/workflows/{entry['build_workflow']}/runs?branch=main&head_sha={recipe}&per_page=100")["workflow_runs"]
        trusted_runs = [r for r in runs if r.get("path") == f".github/workflows/{entry['build_workflow']}" and r.get("head_sha") == recipe and r.get("head_branch") == "main" and r.get("event") in entry["events"] and r.get("head_repository", {}).get("full_name") == HUB]
        published = False
        for run in trusted_runs:
            jobs = fetch(f"repos/{HUB}/actions/runs/{run['id']}/jobs?per_page=100")["jobs"]
            if any(j.get("name") == entry["publisher_job"] and j.get("status") == "completed" and j.get("conclusion") == "success" for j in jobs):
                published = True
                break
        if not published:
            continue
        digest = registry.digest(tag)
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
            raise ValueError("Invalid manifest digest")
        return {"name": name, "repository": repo, "source_sha": source, "recipe_sha": recipe, "tag": tag, "image": entry["image"] + "@" + digest, "signer_workflow": entry["signer_workflow"], "policy_path": entry["policy_path"], "context": entry.get("context", "")}
    raise ValueError("No trusted published image found; publish the package before scanning")


if __name__ == "__main__":
    target = resolve(sys.argv[1])
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        for key, value in target.items():
            output.write(f"{key}={value}\n")
    with open("scan-target.json", "w") as record:
        json.dump(target, record, indent=2)
