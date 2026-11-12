import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'scripts'))
import scan_target

SOURCE = 'a' * 40
RECIPE = 'b' * 40
DIGEST = 'sha256:' + 'c' * 64
TAG = f'sha-{SOURCE}-recipe-{RECIPE}'


class Registry:
    def tags(self):
        return ['latest', TAG]

    def digest(self, tag):
        assert tag == TAG
        return DIGEST


class ScanTests(unittest.TestCase):
    def fetch(self, path):
        if '/commits/' in path:
            return {'commit': {'committer': {'date': '2026-11-12T10:00:00Z'}}}
        if '/compare/' in path:
            return {'status': 'ahead'}
        if '/jobs?' in path:
            return {'jobs': [{'name': f'image-{name} / publish', 'status': 'completed', 'conclusion': 'success'} for name in scan_target.ALLOWLIST]}
        if '/runs?' in path:
            return {'workflow_runs': [{'path': '.github/workflows/build.yml', 'head_sha': RECIPE, 'head_branch': 'main', 'event': 'workflow_dispatch', 'status': 'completed', 'conclusion': 'failure', 'id': 123, 'head_repository': {'full_name': scan_target.HUB}}]}
        return {'private': False, 'archived': False, 'default_branch': 'main'}

    def test_resolves_existing_digest_and_source_policy(self):
        for name in scan_target.ALLOWLIST:
            result = scan_target.resolve(name, fetch=self.fetch, registry_factory=lambda _: Registry())
            self.assertTrue(result['image'].endswith('@' + DIGEST))
            self.assertEqual(result['source_sha'], SOURCE)
            self.assertEqual(result['recipe_sha'], RECIPE)

    def test_missing_published_image_fails(self):
        with patch.object(Registry, 'tags', return_value=['latest', 'sha-not-full']):
            with self.assertRaisesRegex(ValueError, 'No trusted published'):
                scan_target.resolve('hofstetten', fetch=self.fetch, registry_factory=lambda _: Registry())

    def test_private_source_rejected_before_registry_access(self):
        with self.assertRaisesRegex(ValueError, 'Public active'):
            scan_target.resolve('hofstetten', fetch=lambda _: {'private': True}, registry_factory=lambda _: self.fail('registry accessed'))

    def test_untrusted_recipe_rejected(self):
        def fetch(path):
            return {'workflow_runs': []} if '/runs?' in path else self.fetch(path)
        with self.assertRaisesRegex(ValueError, 'No trusted published'):
            scan_target.resolve('hofstetten', fetch=fetch, registry_factory=lambda _: Registry())

    def test_failed_own_publisher_blocks_even_if_other_succeeded(self):
        def fetch(path):
            if '/jobs?' in path:
                return {'jobs': [{'name': 'image-hofstetten / publish', 'status': 'completed', 'conclusion': 'failure'}, {'name': 'image-untereuerheim / publish', 'status': 'completed', 'conclusion': 'success'}]}
            return self.fetch(path)
        with self.assertRaisesRegex(ValueError, 'No trusted published'):
            scan_target.resolve('hofstetten', fetch=fetch, registry_factory=lambda _: Registry())
        self.assertIn('@sha256:', scan_target.resolve('untereuerheim', fetch=fetch, registry_factory=lambda _: Registry())['image'])

    def test_non_main_commit_rejected(self):
        def fetch(path):
            return {'status': 'diverged'} if '/compare/' in path else self.fetch(path)
        with self.assertRaisesRegex(ValueError, 'No trusted published'):
            scan_target.resolve('hofstetten', fetch=fetch, registry_factory=lambda _: Registry())

    def test_bad_digest_rejected(self):
        with patch.object(Registry, 'digest', return_value='latest'):
            with self.assertRaisesRegex(ValueError, 'Invalid manifest digest'):
                scan_target.resolve('hofstetten', fetch=self.fetch, registry_factory=lambda _: Registry())

    def test_manifest_digest_is_checked_against_bytes(self):
        registry = object.__new__(scan_target.PublicRegistry)
        registry.package = 'paul1404/vertex-hofstetten'
        with patch.object(registry, 'request', return_value=(b'{}', {'Docker-Content-Digest': DIGEST})):
            with self.assertRaisesRegex(ValueError, 'Manifest digest did not match'):
                registry.digest(TAG)


if __name__ == '__main__':
    unittest.main()
