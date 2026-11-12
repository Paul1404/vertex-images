import importlib.util
import pathlib
import unittest

spec = importlib.util.spec_from_file_location("plan", pathlib.Path(__file__).parents[1] / "scripts/plan.py")
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)
SHA = "a" * 40
RECIPE = "b" * 40


class PlanTests(unittest.TestCase):
    def fetch(self, path):
        if path.endswith("commits/main"):
            return {"sha": SHA}
        if "/runs?" in path:
            return {"workflow_runs": self.runs}
        return {"private": self.private, "archived": False, "default_branch": "main"}

    def setUp(self):
        self.private = False
        self.runs = [{"id": 123, "head_sha": SHA, "head_branch": "main", "event": "push", "status": "completed", "conclusion": "success", "path": ".github/workflows/ci.yml", "head_repository": {"full_name": "Paul1404/hof-stetten.de"}}]

    def test_exact_successful_main(self):
        result = plan.plan(RECIPE, fetch=self.fetch, exists=lambda *_: False)
        self.assertEqual(result[0]["sha"], SHA)
        self.assertEqual(result[0]["ci_run"], 123)
        self.assertIn(RECIPE, result[0]["tag"])

    def test_reject_untrusted_or_incomplete_ci(self):
        for key, value in [("event", "pull_request"), ("head_branch", "feature"), ("head_sha", "c" * 40), ("conclusion", "failure"), ("status", "in_progress")]:
            with self.subTest(key=key):
                old = self.runs[0][key]
                self.runs[0][key] = value
                self.assertEqual(plan.plan(RECIPE, fetch=self.fetch, exists=lambda *_: False), [])
                self.runs[0][key] = old

    def test_newer_failure_or_pending_blocks_older_success(self):
        old = dict(self.runs[0])
        for status, conclusion in [("completed", "failure"), ("queued", None)]:
            self.runs = [{**old, "id": 124, "status": status, "conclusion": conclusion}, old]
            self.assertEqual(plan.plan(RECIPE, fetch=self.fetch, exists=lambda *_: False), [])

    def test_wrong_workflow_or_repository(self):
        for key, value in [("path", ".github/workflows/evil.yml"), ("head_repository", {"full_name": "attacker/repo"})]:
            old = self.runs[0][key]
            self.runs[0][key] = value
            self.assertEqual(plan.plan(RECIPE, fetch=self.fetch, exists=lambda *_: False), [])
            self.runs[0][key] = old

    def test_two_workloads_resolve_independently(self):
        def fetch(path):
            result = self.fetch(path)
            if "/runs?" in path:
                repo = "Paul1404/untereuerheim.com" if "untereuerheim.com" in path else "Paul1404/hof-stetten.de"
                return {"workflow_runs": [{**self.runs[0], "head_repository": {"full_name": repo}}]}
            return result
        result = plan.plan(RECIPE, fetch=fetch, exists=lambda *_: False)
        self.assertEqual({r["name"] for r in result}, {"hofstetten", "untereuerheim"})
        self.assertEqual(len({r["image"] for r in result}), 2)
        self.assertEqual(plan.plan(RECIPE, selected="untereuerheim", fetch=fetch, exists=lambda *_: False)[0]["repository"], "Paul1404/untereuerheim.com")

    def test_one_pending_source_does_not_block_other(self):
        def fetch(path):
            result = self.fetch(path)
            if "/runs?" in path and "untereuerheim.com" in path:
                return {"workflow_runs": [{**self.runs[0], "head_repository": {"full_name": "Paul1404/untereuerheim.com"}}]}
            if "/runs?" in path:
                return {"workflow_runs": [{**self.runs[0], "status": "queued", "conclusion": None}]}
            return result
        result = plan.plan(RECIPE, fetch=fetch, exists=lambda *_: False)
        self.assertEqual([r["name"] for r in result], ["untereuerheim"])

    def test_skip_published_pair(self):
        self.assertEqual(plan.plan(RECIPE, fetch=self.fetch, exists=lambda *_: True), [])

    def test_reject_private_and_unknown_sources(self):
        self.private = True
        with self.assertRaises(ValueError):
            plan.plan(RECIPE, fetch=self.fetch, exists=lambda *_: False)
        with self.assertRaises(ValueError):
            plan.plan(RECIPE, selected="evil/repo", fetch=self.fetch)

    def test_reject_noncommit_inputs(self):
        for value in ["main", "$(id)", "a" * 39]:
            with self.assertRaises(ValueError):
                plan.tag_for(value, RECIPE)


if __name__ == "__main__":
    unittest.main()
