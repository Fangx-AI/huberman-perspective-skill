from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    from validate_action_playbooks import load_jsonl, validate_playbooks
except ModuleNotFoundError:  # pragma: no cover - module-based test import
    from scripts.validate_action_playbooks import load_jsonl, validate_playbooks


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
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
    "SKILL.md",
    "agents/openai.yaml",
    "docs/COPYRIGHT_AND_DATA_POLICY.md",
    "docs/DATA_DICTIONARY.md",
    "docs/REPRODUCIBILITY.md",
    "docs/MAINTENANCE.md",
    "docs/PROJECT_STATUS.md",
    "docs/PUBLISHING.md",
    "docs/USAGE_EXAMPLES.md",
    "scripts/release_readiness.py",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/evidence-correction.yml",
    ".github/ISSUE_TEMPLATE/safety-report.yml",
    ".github/pull_request_template.md",
    "references/catalog/episodes.csv",
    "references/catalog/claim-index.jsonl",
    "references/catalog/academic-identifier-overrides.csv",
    "references/catalog/academic-repair-queue.csv",
    "references/catalog/academic-study-cards.jsonl",
    "references/catalog/evidence-relations.jsonl",
    "references/catalog/action-playbooks.jsonl",
    "references/catalog/knowledge-graph.json",
    "references/catalog/release-manifest.json",
]

FORBIDDEN_NAMES = {
    "batch-02-transcript-analysis.md",
    "episode-pages.jsonl",
    "episode-resources.csv",
    "sample-transcript-analysis.md",
}
FORBIDDEN_SUFFIXES = {".mp3", ".mp4", ".pyc", ".srt", ".vtt", ".wav"}
IGNORED_PARTS = {".git", ".tmp-install", ".venv", "__pycache__"}
PRIVATE_PATTERNS = {
    "GitHub token": re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    "OpenAI-style token": re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private key": re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\r\n,]+"),
}


def csv_count(path: Path) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check() -> list[str]:
    errors = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts):
            continue
        if path.name in FORBIDDEN_NAMES:
            errors.append(f"forbidden raw catalog: {path.relative_to(ROOT)}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden payload type: {path.relative_to(ROOT)}")
        if path.suffix.lower() in {".csv", ".json", ".jsonl", ".md", ".py", ".toml", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            for label, pattern in PRIVATE_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"possible {label} in {path.relative_to(ROOT)}")

    policy = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if not re.search(r"allow_implicit_invocation:\s*true", policy):
        errors.append("agents/openai.yaml must allow automatic lifestyle-guidance invocation")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    version_sources = {
        "pyproject.toml": re.search(r'^version\s*=\s*"([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE),
        "CITATION.cff": re.search(r'^version:\s*"([^"]+)"', (ROOT / "CITATION.cff").read_text(encoding="utf-8"), re.MULTILINE),
        "README.md": re.search(r"当前版本：`([^`]+)`", (ROOT / "README.md").read_text(encoding="utf-8")),
    }
    for relative, match in version_sources.items():
        if not match or match.group(1) != version:
            errors.append(f"version mismatch in {relative}: expected {version}")

    expected_counts = {
        "references/catalog/episodes.csv": 425,
        "references/catalog/youtube-transcript-queue.csv": 424,
        "references/catalog/bilibili-discovery.csv": 34,
        "references/catalog/courses-lectures.csv": 8,
        "references/catalog/academic-verification-queue.csv": 1736,
    }
    for relative, expected in expected_counts.items():
        path = ROOT / relative
        if path.is_file() and csv_count(path) != expected:
            errors.append(f"unexpected row count for {relative}: expected {expected}, got {csv_count(path)}")

    academic_path = ROOT / "references" / "catalog" / "academic-verification-queue.csv"
    repair_path = ROOT / "references" / "catalog" / "academic-repair-queue.csv"
    if academic_path.is_file() and repair_path.is_file():
        with academic_path.open(encoding="utf-8-sig", newline="") as handle:
            pending_urls = {row["url"] for row in csv.DictReader(handle) if row["verification_status"] == "pending"}
        with repair_path.open(encoding="utf-8-sig", newline="") as handle:
            repair_urls = {row["url"] for row in csv.DictReader(handle)}
        if repair_urls != pending_urls:
            errors.append("academic repair queue does not match pending verification URLs")

    study_cards: list[dict] = []
    study_cards_path = ROOT / "references" / "catalog" / "academic-study-cards.jsonl"
    if academic_path.is_file() and study_cards_path.is_file():
        with academic_path.open(encoding="utf-8-sig", newline="") as handle:
            academic_by_url = {row["url"]: row for row in csv.DictReader(handle)}
        review_ids = set()
        card_count = 0
        with study_cards_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                card_count += 1
                card = json.loads(line)
                study_cards.append(card)
                review_id = card.get("review_id", "")
                if not review_id or review_id in review_ids:
                    errors.append(f"empty or duplicate study-card review_id at line {line_number}")
                review_ids.add(review_id)
                if not card.get("null_findings") or not card.get("limitations") or not card.get("safe_interpretation"):
                    errors.append(f"study card lacks negative findings/boundaries at line {line_number}")
                sample_size = card.get("sample_size")
                if card.get("verification_status") == "verified-review":
                    if not isinstance(sample_size, str) or not sample_size.strip():
                        errors.append(f"review card lacks a review-scope sample_size at line {line_number}")
                elif not (isinstance(sample_size, int) and not isinstance(sample_size, bool) and sample_size > 0):
                    errors.append(f"study card lacks a positive integer sample_size at line {line_number}")
                if not all(url.startswith("https://") for url in card.get("provenance_urls", [])):
                    errors.append(f"study card lacks HTTPS provenance at line {line_number}")
                queue_urls = card.get("queue_urls", card.get("source_urls", []))
                if card.get("source_scope") == "external-context" and queue_urls:
                    errors.append(f"external-context card must not mutate the episode queue at line {line_number}")
                for url in queue_urls:
                    row = academic_by_url.get(url)
                    if not row or row.get("verification_status") != card.get("verification_status") or row.get("evidence_notes") != card.get("queue_note"):
                        errors.append(f"study card and academic queue drifted for {url}")
        if card_count < 20:
            errors.append(f"too few study cards: {card_count}")

    evidence_relations: list[dict] = []
    evidence_relations_path = ROOT / "references" / "catalog" / "evidence-relations.jsonl"
    if evidence_relations_path.is_file():
        review_ids = {card.get("review_id", "") for card in study_cards}
        relation_ids = set()
        with evidence_relations_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                relation = json.loads(line)
                evidence_relations.append(relation)
                relation_id = relation.get("relation_id", "")
                if not relation_id or relation_id in relation_ids:
                    errors.append(f"empty or duplicate evidence relation at line {line_number}")
                relation_ids.add(relation_id)
                if relation.get("source_review_id") not in review_ids or relation.get("target_review_id") not in review_ids:
                    errors.append(f"evidence relation references unknown study card at line {line_number}")
                if relation.get("relation") not in {"replicates", "supports", "qualifies", "challenges", "contradicts"}:
                    errors.append(f"unsupported evidence relation at line {line_number}")
                if not relation.get("rationale") or not relation.get("boundary"):
                    errors.append(f"evidence relation lacks rationale/boundary at line {line_number}")
        if not evidence_relations:
            errors.append("evidence relation catalog is empty")
        elif len(evidence_relations) < 10:
            errors.append(f"too few evidence relations: {len(evidence_relations)}")

    claims: list[dict] = []
    claims_path = ROOT / "references" / "catalog" / "claim-index.jsonl"
    if claims_path.is_file():
        claim_count = 0
        with claims_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                claim_count += 1
                record = json.loads(line)
                claims.append(record)
                if "claim_text" in record:
                    errors.append(f"claim_text leaked at claim-index line {line_number}")
                if not record.get("source_urls") or not record.get("youtube_ids"):
                    errors.append(f"claim locator incomplete at line {line_number}")
        if claim_count != 47:
            errors.append(f"unexpected public claim count: {claim_count}")

    action_playbooks: list[dict] = []
    action_playbooks_path = ROOT / "references" / "catalog" / "action-playbooks.jsonl"
    if action_playbooks_path.is_file():
        try:
            action_playbooks = load_jsonl(action_playbooks_path)
            validate_playbooks(action_playbooks, study_cards, claims)
        except (OSError, ValueError) as exc:
            errors.append(f"invalid action playbook catalog: {exc}")
        if len(action_playbooks) != 17:
            errors.append(f"unexpected action playbook count: {len(action_playbooks)}")

    graph_path = ROOT / "references" / "catalog" / "knowledge-graph.json"
    if graph_path.is_file():
        raw = graph_path.read_text(encoding="utf-8")
        if re.search(r'"show_notes"\s*:', raw):
            errors.append("show_notes payload leaked into public graph")
        graph = json.loads(raw)
        if graph.get("schema") != "public-evidence-v2":
            errors.append("public graph schema must be public-evidence-v2")
        for node in graph.get("nodes", []):
            if node.get("type") == "claim" and ("http" in node.get("label", "") or len(node.get("label", "")) > 180):
                errors.append(f"unsanitized claim label: {node.get('id')}")
        stats = graph.get("stats", {})
        expected_findings = sum(1 + len(card.get("null_findings", [])) for card in study_cards)
        expected_limitations = sum(len(card.get("limitations", [])) for card in study_cards)
        expected_topics = len(
            {
                re.sub(r"[^a-z0-9-]+", "-", tag.lower()).strip("-")
                for card in study_cards
                for tag in card.get("topic_tags", [])
                if re.sub(r"[^a-z0-9-]+", "-", tag.lower()).strip("-")
            }
        )
        expected_null_findings = sum(len(card.get("null_findings", [])) for card in study_cards)
        if stats.get("study_card_nodes") != len(study_cards) or stats.get("study_finding_nodes") != expected_findings:
            errors.append("public graph study-card or finding count is stale")
        if stats.get("study_limitation_nodes") != expected_limitations or stats.get("evidence_topic_nodes") != expected_topics:
            errors.append("public graph limitation or evidence-topic count is stale")
        if stats.get("evidence_relation_nodes") != len(evidence_relations):
            errors.append("public graph evidence-relation count is stale")
        expected_action_steps = sum(len(playbook.get("actions", [])) for playbook in action_playbooks)
        if stats.get("action_playbook_nodes") != len(action_playbooks) or stats.get("action_step_nodes") != expected_action_steps:
            errors.append("public graph action-playbook or action-step count is stale")
        relations = {}
        for edge in graph.get("edges", []):
            relation = edge.get("relation", "")
            relations[relation] = relations.get(relation, 0) + 1
        if relations.get("reports_null_finding") != expected_null_findings or relations.get("has_limitation") != expected_limitations:
            errors.append("public graph lost null-finding or limitation relations")
        typed_relation_edges = sum(relations.get(kind, 0) for kind in {"replicates", "supports", "qualifies", "challenges", "contradicts"})
        if relations.get("has_evidence_relation") != len(evidence_relations) or typed_relation_edges != len(evidence_relations):
            errors.append("public graph lost or duplicated typed evidence-relation edges")
        expected_study_links = sum(len(playbook.get("evidence_links", [])) for playbook in action_playbooks)
        expected_claim_links = sum(len(playbook.get("claim_links", [])) for playbook in action_playbooks)
        expected_groundings = sum(
            len(action.get("evidence_refs", []))
            for playbook in action_playbooks
            for action in playbook.get("actions", [])
        )
        if (
            relations.get("has_action") != expected_action_steps
            or relations.get("uses_study_evidence") != expected_study_links
            or relations.get("uses_claim_context") != expected_claim_links
            or relations.get("grounded_in") != expected_groundings
        ):
            errors.append("public graph lost or duplicated action-playbook relations")
        academic_path = ROOT / "references" / "catalog" / "academic-verification-queue.csv"
        if academic_path.is_file():
            with academic_path.open(encoding="utf-8-sig", newline="") as handle:
                academic_rows = list(csv.DictReader(handle))
            verified_urls = {row["url"] for row in academic_rows if row["verification_status"] != "pending"}
            graph_resource_urls = {
                node.get("url") for node in graph.get("nodes", []) if node.get("type") == "resource" and node.get("url")
            }
            linked_verified = len(verified_urls & graph_resource_urls)
            external_verified = sum(
                node.get("type") == "resource"
                and node.get("source_scope") == "external-context"
                and node.get("verification_status") != "pending"
                for node in graph.get("nodes", [])
            )
            if graph.get("stats", {}).get("verified_academic_resource_nodes") != linked_verified + external_verified:
                errors.append("knowledge graph verified academic count is stale")

    manifest_path = ROOT / "references" / "catalog" / "release-manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("raw_payloads_included") is not False:
            errors.append("manifest must state raw_payloads_included=false")
        for name, expected_hash in manifest.get("sha256", {}).items():
            artifact = manifest_path.parent / name
            if not artifact.is_file():
                errors.append(f"manifest artifact missing: {name}")
            elif sha256(artifact) != expected_hash:
                errors.append(f"manifest hash mismatch: {name}")

    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print("PASS  public release structure, counts, automatic lifestyle invocation, and copyright payload guards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
