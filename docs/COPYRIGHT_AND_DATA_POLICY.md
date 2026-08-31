# Copyright and data-license audit

Audit date: 2026-08-31. This is an engineering risk assessment, not legal advice.

## Release decision

The repository may publish original code, independent evidence classifications, factual identifiers, canonical links and minimal source-location metadata. It must not publish raw or complete third-party expressive content.

| Source class | Public repository | Local cache only | Reason |
|---|---|---|---|
| Original scripts/tests | Yes, MIT | — | Authored for this project |
| Original evidence notes and schemas | Yes, CC BY-NC 4.0 | — | Independent analysis; attribution required |
| Episode/video/article titles, IDs, URLs, dates | Minimal fields only | Full page snapshots | Needed for identification; no ownership claimed |
| Huberman Lab Show Notes, newsletters, transcripts | No | Only when lawfully accessed | Scicomm identifies these as copyrighted content |
| YouTube/Bilibili captions and media | No | Temporary research cache only | Platform/uploader rights and terms vary |
| Paper abstracts/full text/PDFs | No by default | Per-record license controls | API access does not equal redistribution permission |
| Images, logos, voice, likeness | No | No project need | Trademark, publicity and copyright risk |
| Premium/paywalled material | No | User-provided lawful access only; never exported | Access-control and contract boundary |

## Authoritative policy findings

- Scicomm Media's copyright guidelines state that its podcasts, transcripts, audio/video, newsletters, photos and social posts are protected; they require attribution, limit content use to non-commercial contexts, restrict clips, prohibit derivative works without permission and prohibit synthetic likeness uses: <https://www.scicommedia.com/copyright-guidelines/>.
- Huberman Lab identifies `Huberman Lab®` as a registered trademark and states there is no authorization to use Dr. Huberman's name, image, brand or likeness without written consent: <https://www.hubermanlab.com/faq/what-should-i-do-if-i-see-suspicious-content-mentioning-dr-huberman-or-the-huberman-lab-podcast>.
- YouTube uploaders retain ownership of their content; platform access does not grant this repository a redistribution license: <https://www.youtube.com/t/terms>.
- Bilibili's international agreement states that exclusive/self-produced content may not be privately redistributed without permission: <https://www.bilibili.com/blackboard/protocal/international_hans.html>.
- Europe PMC warns that free access remains subject to each author/publisher's copyright or license and that bulk retrieval must use supported channels: <https://europepmc.org/help> and <https://europepmc.org/developers>.

## Controls implemented

1. Raw `episode-pages.jsonl`, resource-page dumps, captions and transcripts are ignored and forbidden by `release_check.py`.
2. The public claim index removes transcript-derived prose and keeps neutral topic labels, source URLs and timestamps.
3. The public graph removes detailed claim labels and course notes that could reproduce source expression.
4. No logos, photos, audio or video are included.
5. The project is clearly marked unofficial; automatic lifestyle-guidance activation does not imply Huberman, Huberman Lab, Scicomm Media or Stanford endorsement.
6. Licenses explicitly exclude third-party material and identifiers.

## Residual risks before broad publication

- A personality/perspective Skill using a living person's name may raise trademark, publicity or implied-affiliation questions even when marked unofficial.
- Transformative summaries and criticism may be legally defensible in some jurisdictions, but Scicomm's current guidelines are more restrictive than a general open-content license.
- Repository maintainers should obtain professional review or written permission before commercial distribution, branding, paid training or inclusion of longer source-derived prose.

The release checker reduces accidental payload publication; it does not provide legal clearance.
