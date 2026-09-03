# Project architecture

## Design goal

The repository should make deep research maintainable while keeping the user experience simple. A user describes a real health-related life problem; the Skill returns a small, safe next step. Research, attribution and evidence machinery remain traceable backstage.

The architecture adapts the research-to-model workflow from [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill). Nuwa's useful contribution here is the separation between source collection, framework extraction and independent fidelity testing. This project adds health-evidence calibration, medical safety and user-outcome layers, and does not imitate Huberman in the first person.

## Repository map

The durable research layer lives at `references/research/`; the main synthesis files are `references/extraction-framework.md` and `references/huberman-operating-model.md`; user actions live in `references/catalog/action-playbooks.jsonl`.

```text
huberman-perspective-skill/
├── SKILL.md                         # short user-facing router and safety contract
├── agents/openai.yaml               # discovery text and automatic invocation policy
├── references/
│   ├── research/                    # seven source-analysis dimensions and durable checkpoints
│   │   ├── 01-writings.md
│   │   ├── 02-conversations.md
│   │   ├── 03-expression-dna.md
│   │   ├── 04-external-views.md
│   │   ├── 05-decisions.md
│   │   ├── 06-timeline.md
│   │   └── 07-courses-lectures.md
│   ├── extraction-framework.md      # rules for promoting patterns into operating models
│   ├── huberman-operating-model.md  # distilled models, heuristics, tensions and limits
│   ├── coaching-guide.md            # user conversation and adjustment workflow
│   ├── fidelity-scorecard.md         # independent behavior-scoring method
│   ├── evals/                        # realistic prompts, outputs and evaluation records
│   └── catalog/                      # structured source, study, relation and action data
├── scripts/
│   ├── research_checkpoint.py       # summarize durable research dimensions and gaps
│   ├── query_action_playbooks.py    # map natural language to one action playbook
│   ├── query_evidence.py            # retrieve bounded study evidence
│   └── ...                           # collection, validation and release tools
├── tests/                            # deterministic contracts and safety regressions
├── FIDELITY.md                       # latest independent product-quality report
└── docs/                             # architecture, maintenance, publishing and policy
```

## Runtime path

```text
user request
    ↓
automatic Skill discovery
    ↓
safety and intent classification
    ↓
one help mode
    ↓
one action playbook or bounded framework inference
    ↓
minimum action + real-world measure + failure adjustment
    ↓
follow-up based on what actually happened
```

`SKILL.md` must remain short enough to load cheaply. It links to the operating model only for framework inference, to the coaching guide for multi-turn adjustment and to structured catalogs for evidence questions.

## Maintenance path

```text
source discovery
    ↓
research dimension files
    ↓  research_checkpoint.py
candidate pattern
    ↓  extraction-framework five gates
operating model / heuristic / contextual claim / reject
    ↓
action playbook
    ↓
unit and safety tests
    ↓
independent answer Agent
    ↓
independent scoring Agent
    ↓
FIDELITY.md + release
```

Every layer has a different job:

| Layer | Owns | Must not do |
|---|---|---|
| Source | canonical URLs, timestamps, bibliographic identity | imply efficacy |
| Research | summarize patterns, criticism and uncertainty | hide contradictions |
| Extraction | decide what is general enough to become a model | promote popularity into truth |
| Operating model | generate decision order and bounded inference | act as a medical protocol |
| Evidence | test claims against studies and guidelines | inherit podcast authority |
| Action | turn one decision into a safe experiment or clear no | dump every possible tool |
| Coaching | fit the action to the user's life and feedback | shame or diagnose |
| Evaluation | test observable behavior independently | score wording alone |

## What was adopted from Nuwa

| Nuwa pattern | Adaptation in this project |
|---|---|
| Six research dimensions saved inside the Skill | Seven dimensions, adding courses and public teaching material |
| Triple validation for mental models | Five gates: recurrence, generative power, distinctiveness, evidence calibration and user safety |
| Contradictions remain visible | Temporal, domain, evidence and real-life fit tensions are retained |
| Research checkpoint | Deterministic checkpoint script reports dimensions and unresolved markers |
| Independent fidelity scorecard | User benefit and medical safety receive half of the total score |
| Self-contained examples | Public eval records contain prompts and judgments without redistributing transcripts |

## What was intentionally not adopted

- 不以第一人称扮演 Huberman (no first-person impersonation);
- style imitation as a product objective;
- storing or redistributing full third-party books, videos, captions or transcripts;
- treating a recognizable voice as evidence of correctness;
- stopping ordinary user help at a research-review checkpoint.

## Navigation by task

- Improving a user answer: start with `SKILL.md`, then `references/coaching-guide.md` and the matching action playbook.
- Adding a new topic: update the relevant research dimension, run the checkpoint, then apply the extraction gates.
- Adding a claim: create traceable source and study records before changing action guidance.
- Changing a core model: document cross-context evidence, limits and tensions in `huberman-operating-model.md`.
- Preparing a release: run unit tests, release gates, fresh-install tests and independent fidelity scoring.

## Architectural invariants

1. User-facing answers do not depend on loading the full catalog.
2. Every framework inference is distinguishable from direct public statements.
3. Every high-risk route can stop and escalate.
4. Research counts are inventory metrics, not product-success metrics.
5. A new model requires stronger evidence than a new contextual claim.
6. A new action requires an observable outcome and failure path.
7. No release is considered behaviorally validated by static tests alone.
