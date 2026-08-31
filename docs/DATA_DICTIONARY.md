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

## `claim-index.jsonl`

One JSON object per source locator. Public records contain `claim_id`, neutral `topic`, YouTube IDs/URLs, timestamps, speaker scope, evidence layer, boundary and parse quality. The private `claim_text` field is deliberately omitted.

## `knowledge-graph.json`

JSON object with `schema`, `generated_at`, `stats`, `nodes` and `edges`. Node types are `episode`, `topic`, `youtube`, `bilibili`, `course-lecture`, `claim`, and `resource`. Public claim labels are neutral topic names; detailed transcript-derived prose is absent.

## Evidence levels

- `A-Direct`: official page, original paper or direct public statement.
- `A-Synthesis`: repeated pattern synthesized from multiple A sources.
- `B-External`: independent criticism, methods context or replication evidence.
- `C-Lead`: discovery lead requiring canonical-source verification.

Evidence level identifies provenance; it does not replace study-design appraisal.
