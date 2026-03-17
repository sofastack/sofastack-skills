---
name: sofastack-community-review
description: Run the periodic SOFAStack GitHub community review automation for the v1 target repositories, using the SOFAStack issue/pr review skills plus local helper scripts for discovery, policy, posting, and state. Use when scanning SOFAStack issue/PR activity, generating maintainer inbox summaries, and auto-posting only high-confidence low-risk top-level comments.
---

# SOFAStack Community Review

Use this skill when running the recurring SOFAStack community review automation.

This skill orchestrates:
- discovery of new or newly-active issue and PR threads
- structured review via [$sofastack-issue-review](../sofastack-issue-review/SKILL.md) or [$sofastack-pr-review](../sofastack-pr-review/SKILL.md)
- deterministic policy evaluation via `$SKILL_ROOT/scripts/community_review.py`
- optional auto-posting for high-confidence issue comments and PR top-level comments only

Read `references/repo-policy.md` before organization-wide runs. It defines the v1 repo scope, repo-specific maintainer sets, and automation-account filters.
For machine-readable org scans, use `references/repo-policy.json` together with `scripts/scan_org.py`.

Discovery notes:
- Ignore bot-authored comments/reviews and automation-only churn from accounts such as `stale[bot]`, `dependabot[bot]`, `app/copilot-swe-agent`, `coderabbitai`, and `codecov`.
- Candidate scanning should only treat non-bot external activity after the lookback window as actionable.

Path notes:
- The commands below assume `SKILL_ROOT` points to the `sofastack-community-review` skill directory.
- Example: `export SKILL_ROOT=/path/to/sofastack-community-review`

## Defaults

- repo: `sofastack/sofa-rpc`
- actor: `nobodyiam`
- maintainers: `nobodyiam`
- mirror dir: `~/.codex/tmp/sofastack-review-mirror`
- state file: `~/.codex/tmp/sofastack-community-review/state.json`
- default branch: `master`

For organization-wide runs, prefer the wrapper below so the bot does not have to reconstruct repo/maintainer mappings every time:

```bash
python3 "$SKILL_ROOT/scripts/scan_org.py" \
  --policy-file "$SKILL_ROOT/references/repo-policy.json" \
  --state-file ~/.codex/tmp/sofastack-community-review/state.json \
  --initial-lookback-hours 4 \
  --pretty
```

If you need to operate repository-by-repository, override `--repo`, `--maintainers`, and usually `--mirror-dir` per repository. Use one shared state file and repo-specific mirror dirs.

Example mirror dir pattern for org scans:
```bash
~/.codex/tmp/sofastack-community-review/mirrors/<repo_slug>
```

## Workflow

1. Sync the isolated mirror:
```bash
python3 "$SKILL_ROOT/scripts/community_review.py" \
  sync-mirror \
  --repo sofastack/sofa-rpc \
  --mirror-dir ~/.codex/tmp/sofastack-review-mirror \
  --default-branch master
```

2. Discover candidates:
```bash
python3 "$SKILL_ROOT/scripts/community_review.py" \
  scan \
  --repo sofastack/sofa-rpc \
  --actor nobodyiam \
  --maintainers nobodyiam \
  --state-file ~/.codex/tmp/sofastack-community-review/state.json \
  --initial-lookback-hours 4
```

3. For each candidate:
- Fetch thread context with `fetch-thread`.
- If it is a PR, also check out the PR head in the isolated mirror before reviewing:
```bash
python3 "$SKILL_ROOT/scripts/community_review.py" \
  checkout-pr-head \
  --repo sofastack/sofa-rpc \
  --mirror-dir ~/.codex/tmp/sofastack-review-mirror \
  --number <pr_number>
```
- Run the appropriate review skill in `output_mode=pipeline`.
- After the review output, append exactly one `COMMUNITY_REVIEW_DECISION` JSON block with:
  - `language`
  - `decision_confidence`
  - `recommended_action`
  - `validation_completed`
  - `missing_info_fields`
  - `blocking`
  - `blocking_reasons`
  - `draft_body`
- Save the combined output to a temp file, then evaluate policy with:
```bash
python3 "$SKILL_ROOT/scripts/community_review.py" \
  decide \
  --candidate-file <candidate_json> \
  --review-file <review_output_txt>
```

4. Auto-post only when `auto_send_eligible=true`.
- Allowed auto-post actions:
  - issue top-level comment
  - PR top-level comment
- Never auto-post:
  - `approve`
  - `request changes`
  - `merge-ready`
  - security/admin threads
  - draft PRs
  - threads with a newer maintainer reply after the latest external activity
- Post via:
```bash
python3 "$SKILL_ROOT/scripts/community_review.py" \
  post-comment \
  --decision-file <decision_json>
```

5. After each handled thread, persist the processed activity signature:
```bash
python3 "$SKILL_ROOT/scripts/community_review.py" \
  mark-processed \
  --state-file ~/.codex/tmp/sofastack-community-review/state.json \
  --candidate-file <candidate_json> \
  --decision-file <decision_json>
```

6. At the end of the run, summarize all results:
```bash
python3 "$SKILL_ROOT/scripts/community_review.py" \
  summarize \
  --results-file <results_json>
```

## Output Rules

- Always produce one inbox item with these sections:
  - `Auto-sent`
  - `Needs review`
  - `Skipped/Error`
- If there is no actionable work, include `::archive-thread{}` after the inbox item.
- Keep the full draft body in the `Needs review` section.
- Auto-sent comments must include the localized AI disclaimer; manual drafts must not add it automatically.

## Hard Safety Rules

- Never use the current workspace remote configuration to decide which repository to query.
- Never post to GitHub outside the helper CLI flow above.
- Never auto-send a formal review state.
- If discovery, parsing, or GitHub API calls fail for a thread, route it to `Skipped/Error`.
