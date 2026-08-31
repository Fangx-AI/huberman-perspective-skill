from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def main() -> int:
    full_catalog = ROOT / "references" / "catalog" / "episode-pages.jsonl"
    target = SCRIPTS / ("contract_check_full.py" if full_catalog.is_file() else "release_check.py")
    profile = "full local cache" if full_catalog.is_file() else "public release"
    print(f"contract profile: {profile}")
    return subprocess.call([sys.executable, str(target)])


if __name__ == "__main__":
    raise SystemExit(main())
