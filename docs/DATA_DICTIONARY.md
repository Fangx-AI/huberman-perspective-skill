# Data dictionary

All public data uses UTF-8. Empty strings mean “unknown/not recorded”; they do not mean a negative result.

## `references/catalog/episodes.csv`

One row per official Episode page.

| Field | Meaning |
|---|---|
| `episode_id` | Stable slug used by the official page |
| `title` | Source title for identification |
| `url` | Canonical official Episode URL |
| `date_published` | Source publication timestamp when available |
| `episode_number` | Source episode number when available |
| `duration` | ISO 8601 duration when available |
| `topic_urls` | Semicolon-separated official topic URLs |
| `youtube_urls` | Semicolon-separated canonical YouTube URLs |
| `has_show_notes` | Boolean indicating local collector observed Show Notes; text is not exported |
| `has_timestamps` | Boolean indicating timestamps were observed; full chapter text is not exported here |
| `fetch_ok` | Collector success flag, not a content-quality score |

## `youtube-transcript-queue.csv`

Tracks canonical video ID, source URL, priority, availability and analysis state. It never contains caption text.

## `bilibili-discovery.csv`

Discovery-only Bilibili records. `source_level=C` or `mirror-only` cannot independently support a claim. `youtube_id` and `official_episode_url` perform deduplication when known.

## `academic-verification-queue.csv`

| Field | Meaning |
|---|---|
| `url` | Source URL extracted from public Episode resources |
| `episode_count` | Number of Episodes linking the URL; relevance, not quality |
| `episode_ids` | Semicolon-separated Episode IDs |
| `episode_title_sample` | One identifying Episode title |
| `verification_status` | `pending`, `verified-bibliographic`, `verified-study`, `verified-observational`, or `verified-review` |
| `evidence_notes` | Independent design/result/boundary note; not an abstract copy |

## `academic-identifier-overrides.csv`

Traceable repairs for legacy source URLs whose canonical PMID, PMCID, DOI or PII cannot be derived safely. Each row records the exact queue URL, replacement identifier, official `provenance_url` and a short note. An override only supplies a lookup key; the verifier still requires a successful public bibliographic API response before changing queue status.

## `academic-repair-queue.csv`

One row for every `pending` academic verification record. It preserves Episode linkage and adds `repair_class`, any safely parsed provider/identifier, and a bounded `next_action`. The file is a maintenance/contribution queue, not evidence; release validation requires its URL set to match the pending verification URL set exactly.

## `academic-study-cards.jsonl`

One JSON object per manually reviewed high-priority paper. A card records the exact queue URLs, primary-source provenance, study design, sample, intervention/exposure, comparator, outcomes, result summary, negative findings, limitations and a bounded safe interpretation. `apply_academic_study_cards.py` is the only supported path for promoting these records from bibliographic-only to research-level status; release validation requires every card URL, status and queue note to remain aligned.

## `claim-index.jsonl`

One JSON object per source locator. Public records contain `claim_id`, neutral `topic`, YouTube IDs/URLs, timestamps, speaker scope, evidence layer, boundary and parse quality. The private `claim_text` field is deliberately omitted.

## `knowledge-graph.json`

JSON object with `schema`, `generated_at`, `stats`, `nodes` and `edges`. Node types are `episode`, `topic`, `youtube`, `bilibili`, `course-lecture`, `claim`, `resource`, `study-card`, `study-finding`, `study-limitation`, and `evidence-topic`. Study cards connect to exact Episode resource nodes through `reviews_resource`; positive summaries, null findings and limitations use `reports_result`, `reports_null_finding`, and `has_limitation`. Public claim labels remain neutral topic names; detailed transcript-derived prose is absent.

## Evidence levels

- `A-Direct`: official page, original paper or direct public statement.
- `A-Synthesis`: repeated pattern synthesized from multiple A sources.
- `B-External`: independent criticism, methods context or replication evidence.
- `C-Lead`: discovery lead requiring canonical-source verification.

Evidence level identifies provenance; it does not replace study-design appraisal.
