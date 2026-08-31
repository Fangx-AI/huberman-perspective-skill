# GitHub publishing and release procedure

Canonical repository: <https://github.com/Fangx-AI/huberman-perspective-skill>.

## Preflight

Run from a clean public checkout, not from the maintainer's private cache:

```bash
python -m pip install --requirement requirements.lock
python scripts/release_check.py
python scripts/release_readiness.py --require-origin
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

Then confirm:

- `git status --porcelain` is empty;
- `VERSION`, `pyproject.toml`, `CITATION.cff` and the README version agree;
- the tag points to the exact tested commit;
- the release manifest diff contains only expected sanitized artifacts;
- the copyright audit date and residual-risk wording are still current;
- no issue, example or fixture contains restricted source text, patient data or credentials.

## Publish a tagged release

```bash
git push origin main --follow-tags
gh release create "v$(cat VERSION)" \
  --repo Fangx-AI/huberman-perspective-skill \
  --verify-tag \
  --title "Huberman Perspective Skill v$(cat VERSION)" \
  --generate-notes
```

On PowerShell, obtain the version with `(Get-Content VERSION).Trim()` and pass the resulting tag to `gh release create`.

Do not publish from a dirty tree, move an existing release tag, or attach raw transcript/media archives. If a release contains a medical-safety or copyright regression, remove the affected release artifact, publish a corrective patch and document the incident without exposing sensitive material.

## Repository settings

- Keep default workflow permissions read-only unless a release workflow explicitly needs more.
- Require pull-request checks before merging when branch-protection capabilities are available.
- Use GitHub private security advisories for secrets, private data, exploitable script behavior or sensitive safety reports.
- Keep Discussions/Issues focused on source corrections, reproducibility and safe behavior; they are not a venue for personal medical diagnosis.

The repository is unofficial and uses a living person's name descriptively. Public availability does not remove the trademark, publicity, platform-term or copyright residual risks documented in `COPYRIGHT_AND_DATA_POLICY.md`.
