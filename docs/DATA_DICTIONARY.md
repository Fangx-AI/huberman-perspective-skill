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

The queue is generated only from resources classified by the shared `scripts/resource_classification.py` rules. The catalog builder and graph builder import the same classifier so a publisher cannot silently be academic in one artifact and nonacademic in another. Host inclusion means “needs scholarly verification,” not “is a high-quality study.”

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

One JSON object per manually reviewed high-priority paper. A card records source URLs, primary-source provenance, study design, sample, intervention/exposure, comparator, outcomes, result summary, negative findings, limitations and a bounded safe interpretation. `sample_size` is a positive integer for original or observational studies; for `verified-review` it is a non-empty review-scope string such as “not applicable (narrative review of 10 techniques)”, never a fictitious participant count. Review cards must also identify systematic/meta-analytic/narrative design and preserve search, risk-of-bias and pooled-effect limitations. Optional `search_aliases` preserve discoverability for documented legacy spellings without changing canonical IDs or names. Episode-linked cards default to `source_scope=episode-linked`; their `queue_urls` default to `source_urls` and must remain aligned with the Show Notes queue. An independently selected replication or counter-study uses `source_scope=external-context` plus an explicit empty `queue_urls` list, so it cannot mutate or inflate Episode queue statistics. `apply_academic_study_cards.py` is the only supported path for promoting queue-linked records.

## `evidence-relations.jsonl`

One JSON object per manually reviewed relationship between two study cards. Required fields are stable `relation_id`, source and target `review_id`, typed `relation` (`replicates`, `supports`, `qualifies`, `challenges`, or `contradicts`), exact `claim_scope`, `rationale`, relationship `boundary`, HTTPS provenance and review date. A relation is directional and claim-scoped: `challenges` must not be interpreted as rejecting every result in the target paper.

## `claim-index.jsonl`

One JSON object per source locator. Public records contain `claim_id`, neutral `topic`, YouTube IDs/URLs, timestamps, speaker scope, evidence layer, boundary and parse quality. The private `claim_text` field is deliberately omitted.

## `action-playbooks.jsonl`

One JSON object per outcome-first user playbook. Each playbook defines a concrete `user_goal`, aliases, scope, selective first questions, baseline checks, one to three actions, study links, public-claim context, exclusions, escalation rules and a bounded summary. Every action records `classification`, trigger, minimum version, observable metric, review interval, adaptation rule, stop conditions and declared evidence references.

Action classifications are deliberately narrower than evidence levels:

- `evidence-supported`: the action direction is reasonably supported by the linked human evidence, within the recorded boundary.
- `bounded-experiment`: a low-risk personal experiment consistent with evidence, but not a validated universal dose or protocol.
- `framework-inference`: an implementation choice synthesized from Huberman's public framework; it must not be presented as a tested prescription.

`support_type` records `direct-support`, `bounded-support`, or `framework-context`. Every playbook must link at least one reviewed study and one public claim locator. This catalog is decision support, not medical diagnosis or treatment.

## `knowledge-graph.json`

JSON object with `schema`, `generated_at`, `stats`, `nodes` and `edges`. Node types are `episode`, `topic`, `youtube`, `bilibili`, `course-lecture`, `claim`, `resource`, `study-card`, `study-finding`, `study-limitation`, `evidence-topic`, `evidence-relation`, `action-playbook`, and `action-step`. Study cards connect to reviewed resources through `reviews_resource`; external resources retain `source_scope=external-context` and zero Episode links. Positive summaries, null findings and limitations use `reports_result`, `reports_null_finding`, and `has_limitation`. A source card connects to an evidence-relation node with `has_evidence_relation`; that node connects to the target card with its typed relation. Playbooks connect to steps with `has_action`, to reviewed studies with `uses_study_evidence`, and to public claim context with `uses_claim_context`; each step uses `grounded_in` for its declared references. Public claim labels remain neutral topic names; detailed transcript-derived prose is absent.

## Evidence levels

- `A-Direct`: official page, original paper or direct public statement.
- `A-Synthesis`: repeated pattern synthesized from multiple A sources.
- `B-External`: independent criticism, methods context or replication evidence.
- `C-Lead`: discovery lead requiring canonical-source verification.

Evidence level identifies provenance; it does not replace study-design appraisal.
