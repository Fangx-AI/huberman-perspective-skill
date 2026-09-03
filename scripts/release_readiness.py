from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "SKILL.md",
    "pyproject.toml",
    "LICENSE",
    "DATA-LICENSE.md",
    "THIRD_PARTY_NOTICES.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "FIDELITY.md",
    "CITATION.cff",
    "VERSION",
    "requirements.lock",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/evidence-correction.yml",
    ".github/ISSUE_TEMPLATE/safety-report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/pull_request_template.md",
    "docs/COPYRIGHT_AND_DATA_POLICY.md",
    "docs/ARCHITECTURE.md",
    "docs/DATA_DICTIONARY.md",
    "docs/MAINTENANCE.md",
    "docs/PROJECT_STATUS.md",
    "docs/PUBLISHING.md",
    "docs/REPRODUCIBILITY.md",
    "docs/USAGE_EXAMPLES.md",
    "references/extraction-framework.md",
    "references/fidelity-scorecard.md",
    "references/evals/user-value-blackbox-2026-09-03.md",
    "references/huberman-operating-model.md",
    "scripts/research_checkpoint.py",
    "scripts/release_readiness.py",
)

README_LINKS = (
    "FIDELITY.md",
    "docs/COPYRIGHT_AND_DATA_POLICY.md",
    "docs/ARCHITECTURE.md",
    "docs/DATA_DICTIONARY.md",
    "docs/MAINTENANCE.md",
    "docs/PROJECT_STATUS.md",
    "docs/PUBLISHING.md",
    "docs/REPRODUCIBILITY.md",
    "docs/USAGE_EXAMPLES.md",
    "references/fidelity-scorecard.md",
)

PLAYBOOK_IDS = (
    "decide-whether-to-try-one-health-protocol",
    "start-and-sustain-one-habit",
    "retain-what-you-learn",
    "stabilize-sleep-wake-timing",
    "protect-one-focus-block",
    "start-exercise-without-protocol-overload",
    "improve-food-environment-first",
)


def git_origin(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def check(root: Path = ROOT, require_origin: bool = False) -> tuple[list[str], list[str]]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing release-readiness artifact: {relative}")

    if errors:
        return errors, warnings

    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    version_sources = {
        "pyproject.toml": re.search(
            r'^version\s*=\s*"([^"]+)"',
            (root / "pyproject.toml").read_text(encoding="utf-8"),
            re.MULTILINE,
        ),
        "CITATION.cff": re.search(
            r'^version:\s*"([^"]+)"',
            (root / "CITATION.cff").read_text(encoding="utf-8"),
            re.MULTILINE,
        ),
        "README.md": re.search(
            r"当前版本：`([^`]+)`",
            (root / "README.md").read_text(encoding="utf-8"),
        ),
    }
    for relative, match in version_sources.items():
        if not match or match.group(1) != version:
            errors.append(f"version mismatch in {relative}: expected {version}")

    readme = (root / "README.md").read_text(encoding="utf-8")
    for relative in README_LINKS:
        if relative not in readme:
            errors.append(f"README does not route readers to {relative}")

    first_screen = readme[:1800]
    for marker in ("## 30 秒开始", "## 回答会是什么样", "npx skills add"):
        if marker not in first_screen:
            errors.append(f"README first screen omits user-onboarding marker: {marker}")
    if "当前公开快照包括" in first_screen:
        errors.append("README puts research inventory before the user can understand first use")

    for stale_command in (
        "query_study_cards.py",
        "query_evidence_relations.py",
        "query_knowledge_graph.py",
        "quick_validate.py",
    ):
        if stale_command in readme:
            errors.append(f"README references missing command: {stale_command}")

    examples = (root / "docs/USAGE_EXAMPLES.md").read_text(encoding="utf-8")
    for playbook_id in PLAYBOOK_IDS:
        if playbook_id not in examples:
            errors.append(f"usage examples omit playbook: {playbook_id}")
    for boundary in ("ADHD", "hippocampal growth", "skip meals", "full transcripts"):
        if boundary not in examples:
            errors.append(f"usage examples omit safety/copyright boundary: {boundary}")

    maintenance = (root / "docs/MAINTENANCE.md").read_text(encoding="utf-8")
    for marker in ("## Roadmap", "## 1.0 exit criteria", "independent", "copyright"):
        if marker not in maintenance:
            errors.append(f"maintenance roadmap omits: {marker}")

    ci = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for command in (
        "python scripts/release_check.py",
        "python scripts/release_readiness.py",
        "python -m unittest discover -s tests -v",
        "python scripts/install_skill.py",
    ):
        if command not in ci:
            errors.append(f"CI omits release gate: {command}")

    origin = git_origin(root)
    github_origin = bool(re.search(r"(?:github\.com[:/])[^/]+/[^/]+(?:\.git)?$", origin))
    if require_origin and not github_origin:
        errors.append("Git origin is missing or is not a GitHub repository")
    elif not origin:
        warnings.append("Git origin is not configured; local artifact readiness does not prove GitHub publication")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check repository-level release and contribution readiness.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-origin", action="store_true")
    args = parser.parse_args()
    errors, warnings = check(args.root, args.require_origin)
    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"FAIL  {error}")
    if errors:
        print(f"summary: {len(errors)} failed, {len(warnings)} warning(s)")
        return 1
    print(f"PASS  release readiness: documentation, examples, contribution flow and CI gates ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
