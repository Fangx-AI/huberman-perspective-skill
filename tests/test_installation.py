from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(
    (ROOT / "references" / "catalog" / "episode-pages.jsonl").exists(),
    "the full maintainer cache is not a distributable clean-install source",
)
class CleanInstallationTests(unittest.TestCase):
    def test_clean_install_contains_action_layer_and_passes_release_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "huberman-perspective"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "install_skill.py"), "--destination", str(destination)],
                check=True,
                capture_output=True,
                text=True,
            )
            for relative in (
                "SKILL.md",
                "references/catalog/action-playbooks.jsonl",
                "scripts/query_action_playbooks.py",
                "scripts/validate_action_playbooks.py",
                "tests/test_action_playbooks.py",
            ):
                self.assertTrue((destination / relative).is_file(), relative)
            result = subprocess.run(
                [sys.executable, str(destination / "scripts" / "release_check.py")],
                cwd=destination,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
