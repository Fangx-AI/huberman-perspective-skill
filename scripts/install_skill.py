from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL_ITEMS = (
    ".github",
    "SKILL.md",
    "agents",
    "scripts",
    "references",
    "docs",
    "tests",
    "README.md",
    "LICENSE",
    "DATA-LICENSE.md",
    "THIRD_PARTY_NOTICES.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "VERSION",
    "pyproject.toml",
    "requirements.lock",
)


def default_destination() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    base = Path(codex_home) if codex_home else Path.home() / ".codex"
    return base / "skills" / "huberman-perspective"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Skill without overwriting an existing destination.")
    parser.add_argument("--destination", type=Path, default=default_destination())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    destination = args.destination.expanduser().resolve()

    if destination.exists():
        raise SystemExit(f"refusing to overwrite existing destination: {destination}")

    print(f"source: {ROOT}")
    print(f"destination: {destination}")
    if args.dry_run:
        return 0

    destination.mkdir(parents=True)
    for name in INSTALL_ITEMS:
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, target)
    print("installed; restart or refresh Codex skill discovery if needed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
