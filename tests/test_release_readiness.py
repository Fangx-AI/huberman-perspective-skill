from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("release_readiness", ROOT / "scripts" / "release_readiness.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ReleaseReadinessTests(unittest.TestCase):
    def test_committed_repository_has_required_publishability_artifacts(self) -> None:
        errors, _warnings = MODULE.check(ROOT, require_origin=False)
        self.assertEqual(errors, [])

    def test_missing_artifacts_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            errors, _warnings = MODULE.check(Path(directory), require_origin=False)
        self.assertTrue(errors)
        self.assertTrue(any("README.md" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
