"""Select public source commits whose latest main CI passed."""
import json
import os
import re
import urllib.error
import urllib.request

ALLOWLIST = {
    "hofstetten": {"repository": "Paul1404/hof-stetten.de", "image": "ghcr.io/paul1404/vertex-hofstetten", "workflow": "ci.yml"},
    "untereuerheim": {"repository": "Paul1404/untereuerheim.com", "image": "ghcr.io/paul1404/vertex-untereuerheim", "workflow": "ci.yml"},
}


def api(path):
    request = urllib.request.Request("https://api.github.com/" + path, headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"], "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def eligible(run, sha, repository, workflow):
    return (run.get("head_sha") == sha and run.get("head_branch") == "main"
            and run.get("event") == "push" and run.get("conclusion") == "success"
            and run.get("status") == "completed"
            and run.get("path") == f".github/workflows/{workflow}"
            and run.get("head_repository", {}).get("full_name") == repository)


def tag_for(sha, recipe):
    if not re.fullmatch(r"[a-f0-9]{40}", sha) or not re.fullmatch(r"[a-f0-9]{40}", recipe):
        raise ValueError("Full source and recipe commits required")
    return f"sha-{sha}-recipe-{recipe}"


def published(image, tag):
    """Check whether the image tag is publicly readable."""
    package = image.removeprefix("ghcr.io/")
    try:
        with urllib.request.urlopen("https://ghcr.io/token?service=ghcr.io&scope=repository:" + package + ":pull", timeout=30) as response:
            token = json.load(response)["token"]
        req = urllib.request.Request(f"https://ghcr.io/v2/{package}/manifests/{tag}", method="HEAD", headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.v2+json"})
        with urllib.request.urlopen(req, timeout=30):
            return True
    except urllib.error.HTTPError as error:
        if error.code in (401, 403, 404):
            return False
        raise


def plan(recipe, selected="all", fetch=api, exists=published):
    if selected not in ("all", *ALLOWLIST):
        raise ValueError("Unknown workload")
    result = []
    for name, entry in ALLOWLIST.items():
        if selected not in ("all", name):
            continue
        repo = entry["repository"]
        meta = fetch(f"repos/{repo}")
        if meta["private"] or meta["archived"] or meta["default_branch"] != "main":
            raise ValueError("Public active main source required")
        sha = fetch(f"repos/{repo}/commits/main")["sha"]
        tag = tag_for(sha, recipe)
        runs = fetch(f"repos/{repo}/actions/workflows/{entry['workflow']}/runs?event=push&branch=main&head_sha={sha}&per_page=100")["workflow_runs"]
        newest = runs[0] if runs else None
        if not newest or not eligible(newest, sha, repo, entry["workflow"]) or exists(entry["image"], tag):
            continue
        result.append({"name": name, **entry, "sha": sha, "recipe": recipe, "tag": tag, "ci_run": newest["id"]})
    return result


if __name__ == "__main__":
    result = plan(os.environ["GITHUB_SHA"], os.environ.get("WORKLOAD", "all"))
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write("matrix=" + json.dumps({"include": result}, separators=(",", ":")) + "\n")
        output.write("count=" + str(len(result)) + "\n")
