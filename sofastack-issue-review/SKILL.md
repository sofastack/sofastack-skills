---
name: sofastack-issue-review
description: Review SOFAStack ecosystem issues with a classify-first workflow (reproduce for behavior issues, evidence-check for consultative asks, and route repo-mismatch threads correctly) and draft maintainer-grade replies that directly answer the user, request only the missing details that matter, and preserve a low-noise maintainer voice.
---

# SOFAStack Issue Review

Follow this workflow to review a SOFAStack issue and produce a concise maintainer response.

## Core Principles

- Classify first: behavior/regression issue vs consultative/support question vs feature request/documentation ask.
- For behavior/regression issues: reproduce first, theorize second.
- For consultative/support questions: verify by repository evidence scan first and answer directly.
- Solve the user's ask; do not hide behind generic triage language.
- Match the thread language: Chinese thread -> Chinese reply, English thread -> English reply, unless the user explicitly asks otherwise.
- Use repository reality, not vague platform language. Call out repo mismatches when the issue belongs in another SOFAStack repository.
- Respect the SOFAStack issue templates when requesting more info. For bug reports, strongly prefer these fields when relevant: project version, language version, OS version, IDE version, reproduce steps, expected behavior.
- If an existing comment already answers the same question well, avoid duplicate long replies; add only the missing delta.
- Never wrap GitHub @mentions in code spans.

## Input Contract

Collect or derive these fields before review:

- `repo`: `<owner>/<repo>`
- `issue_number`: numeric ID
- `issue_context`: title/body/comments
- `publish_mode`: `draft-only` (default) or `post-after-confirm`
- `output_mode`: `human` (default) or `pipeline`

Optional but recommended:

- `known_labels`: existing labels on the issue
- `desired_outcome`: whether user wants triage only or triage + implementation handoff

If `issue_number` or `issue_context` is missing, ask one short clarification before continuing.

## Workflow

1. Collect issue facts and the actual user ask
- Read the full issue body and recent comments before concluding.
- Extract: primary ask, symptom, expected behavior, actual behavior, current blocker, and whether the reporter is asking for support, a fix, a feature, or repo routing.
- Decide issue type up front:
  - behavior/regression
  - consultative/support
  - feature request / docs
- Confirm whether the issue is in the right repo. If not, draft a reply that explains the mismatch and the likely target repo.
- If GitHub API access is unstable, use:
```bash
curl -L -s https://api.github.com/repos/<owner>/<repo>/issues/<id>
curl -L -s https://api.github.com/repos/<owner>/<repo>/issues/<id>/comments
```

2. Run the right validation path (mandatory)
- For behavior/regression issues:
  - Build a minimal local reproduction when practical.
  - Prefer repo-native tests or a tiny temporary repro over speculation.
  - Record exact observed output, logs, or behavior.
- For consultative/support questions:
  - Verify with evidence scan across code, docs, examples, and issue templates.
  - Record exact files or paths searched and what was or was not found.
- Example checks:
```bash
rg -n "<keyword_or_api>" -S
rg --files | rg -i "<keyword1|keyword2>"
# or targeted test / build commands in the repo when needed
```

3. Branch by validation result
- Behavior/regression path:
  - If reproducible:
    - State clearly that the behavior is confirmed.
    - Distinguish supported behavior, usage mismatch, current bug, or feature gap.
  - If not reproducible:
    - Ask only for the minimum missing evidence needed to move forward.
- Consultative/support path:
  - If capability exists: provide exact file/path/entry point.
  - If it does not exist: say so directly and give one practical alternative.
  - If the thread belongs in another SOFAStack repo: say where and why.

4. Draft maintainer reply
- Start with a one-paragraph summary in the thread language:
  - behavior/regression: reproduction result
  - consultative/support: direct conclusion
- Then include:
  - `当前结论 / Conclusion`
  - `当前能力与边界 / Current Support Boundary`
  - `可行方案 / Practical Path`
  - `后续路径 / Next Step`
- If the issue is missing mandatory context, request only the missing fields that truly block progress.
- Keep wording factual, concise, and actionable.

5. Ask for publish confirmation (mandatory gate)
- Default behavior: generate draft only; do not post automatically.
- Present the exact comment body first, then ask for confirmation.
- Use a direct question in the thread language.

6. Post only after explicit confirmation
- Preferred:
```bash
gh api repos/<owner>/<repo>/issues/<id>/comments -f body='<reply>'
```
- Fallback when `gh` transport is unstable:
```bash
TOKEN=$(gh auth token)
curl --http1.1 -sS -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d '{"body":"<reply>"}' \
  https://api.github.com/repos/<owner>/<repo>/issues/<id>/comments
```
- After posting, return the comment URL as evidence.

## Output Contract

Default (`output_mode=human`) output should be human-friendly:

1. `Issue Summary`
- issue type + confidence
- validation result (`reproduced` / `not reproduced` / `evidence result`)
- repo-fit note if the issue likely belongs elsewhere

2. `Triage Suggestion`
- labels to add
- missing information (if any)
- whether it is ready for implementation handoff

3. `Draft Maintainer Reply`
- First sentence must match issue type:
  - behavior/regression: reproducibility status (`已复现/暂未复现` or `Reproduced/Not yet reproduced`)
  - consultative/support: direct availability conclusion
- Include at least one concrete file/path/test/doc reference when possible.
- If unsupported today: include support boundary + practical workaround + next path.
- If reproducible and conclusion is stable: do not request extra data.
- If not reproducible: request only minimal reproducible inputs.
- Keep language matched to the thread unless the user asks otherwise.

4. `Publish Gate`
- If no explicit publish confirmation exists, end with:
  - Chinese: `是否直接发布到 issue #<id>？回复“发布”或“先不发”。`
  - English: `Post this to issue #<id> now? Reply "post" or "hold".`

If `output_mode=pipeline`, append one machine-readable block after the human output:

```yaml
handoff:
  issue_classification:
    type: "功能咨询|问题排查|技术讨论|Bug 反馈|Feature request"
    validation_path: "behavior-regression|consultative-support"
    confidence: "high|medium|low"
  triage_decision:
    labels_to_add: []
    missing_info_fields: []
    ready_for_issue_to_pr: false
    ready_reason: ""
  implementation_handoff:
    goal: ""
    acceptance_criteria: []
    suggested_modules: []
    risk_hints: []
```
