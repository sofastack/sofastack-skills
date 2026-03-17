---
name: sofastack-pr-review
description: Review pull requests for SOFAStack repositories (sofa-rpc, sofa-jraft, sofa-boot, sofa-bolt, sofa-registry, sofa-tracer, sofa-ark, etc.) with maintainer-grade rigor. Use when triaging contributor updates, reconciling prior review feedback, validating AI/bot comments, checking compatibility and regression risks, and drafting concise publish-ready maintainer replies.
---

# SOFAStack PR Review

Use this skill to run high-signal PR reviews across SOFAStack repositories with consistent standards and low back-and-forth.

## Input Contract

Collect or derive these fields before review:

- `repo`: `<owner>/<repo>`
- `pr_number`: numeric ID
- `head_sha`: latest commit SHA on the PR head
- `pr_context`: files, comments, reviews, checks
- `linked_issues`: issue IDs/URLs explicitly linked by PR metadata/text (may be empty)
- `goal_source`: `linked-issue` or `pr-description-only`
- `publish_mode`: `draft-only` (default) or `send-after-confirm`
- `output_mode`: `human` (default) or `pipeline`

Optional but recommended handoff from issue work:
- `goal`
- `acceptance_criteria`
- `non_goals`
- `change_plan`
- `test_results`

If `pr_number` or `head_sha` cannot be confirmed, ask one short clarification before continuing.
If linked issues exist, fetch their latest body/comments and treat reported symptoms as review contract.
If no linked issue exists, derive scope from PR title/body + latest author explanation and mark it as inferred.

## Review Workflow

1. Collect latest PR context
- Pull current PR head SHA, changed files, reviews, review comments, issue comments, and checks.
- Prefer `gh` first; if `gh` GraphQL/networking is unstable, fall back to GitHub REST via `curl`.
- Always confirm you are reviewing the current head SHA.

2. Establish target problem and completion criteria
- If linked issue(s) exist, extract concrete scenarios/symptoms from issue body and key maintainer comments.
- Build a scenario coverage map: `scenario -> changed code -> tests -> status`.
- Mark each scenario as `resolved`, `partially resolved`, `unresolved`, or `out of scope`.
- If no linked issue exists, derive scenarios from PR description and explicitly label assumptions as inferred.

3. Reconcile prior feedback
- Extract prior maintainer concerns and AI/bot suggestions.
- Mark each as `resolved`, `partially resolved`, `unresolved`, or `obsolete`.
- Require code evidence before marking `resolved`.

4. Verify CI and merge gates
- Check required checks first, then drill into failed jobs/logs.
- For Java repos, explicitly verify style/formatting and test gates when present.
- Separate `blocking` vs `non-blocking` failures in review output.

5. Find new risks
- Focus on regressions and compatibility first, then polish.
- Prioritize: API compatibility, behavior changes, lifecycle leaks, concurrency safety, migration impact, and missing tests.
- When a PR touches shared validation or transport code, check sibling entry points for the same bug class.

6. Evaluate AI/bot suggestions
- Judge by technical correctness and user impact, not confidence tone.
- Classify each as:
  - `reasonable and fixed`
  - `reasonable but not fixed`
  - `not applicable / low value`
- Treat Copilot, Dependabot, CodeRabbit, and similar automation as inputs, not authority.

7. Decide review action
- If fixes are required, recommend `request changes`.
- If checks are clean and no blocking findings remain, recommend `approve`.
- If the PR is not ready for a formal state but has useful non-blocking feedback, recommend `comment`.
- If asked to merge, follow repository policy; otherwise do not merge automatically.

8. Prepare comment summary for maintainer confirmation
- Findings first (`P1/P2/P3`), each with path and line.
- Then open questions/assumptions.
- Then issue-coverage verdict (`full` / `partial` / `not addressed`).
- Then a brief addressed-items summary and maintainer comment draft.
- Include explicit proposed action: `comment`, `request changes`, `approve`, or `merge-ready`.

9. Send only after explicit user confirmation
- Do not post review/comment automatically after drafting.
- Ask for confirmation first, then execute the selected GitHub action.

## Communication Language Policy

- Default: follow the primary language used by the linked issue + PR discussion.
- If language is mixed or ambiguous, prefer the latest maintainer/contributor exchange.
- If the user explicitly requests a language, user request overrides defaults.

## Severity Rules

Use these levels consistently:

- `P1`: breaking changes, silent behavior regressions, leaks, data loss, security risks.
- `P2`: significant correctness risks, fragile concurrency, likely runtime surprises.
- `P3`: observability/log quality, maintainability issues, polish.

Do not inflate severity for stylistic preferences.

## GitHub Ops Fallbacks

- If `gh` GraphQL fails, use REST endpoints:
  - `GET /repos/{owner}/{repo}/pulls/{number}`
  - `GET /repos/{owner}/{repo}/pulls/{number}/files`
  - `GET /repos/{owner}/{repo}/pulls/{number}/reviews`
  - `GET /repos/{owner}/{repo}/issues/{number}`
  - `GET /repos/{owner}/{repo}/issues/{number}/comments`
  - `GET /repos/{owner}/{repo}/commits/{sha}/check-runs`
  - `GET /repos/{owner}/{repo}/commits/{sha}/status`

## Evidence Standard

Before posting a finding, ensure:

- Reproducible from current head.
- Specific path and line reference exists.
- Impact statement explains who breaks.
- Suggested direction is practical.
- For linked-issue PRs, include evidence that each in-scope scenario is covered or explicitly still missing.

## Output Contract

Default (`output_mode=human`) output should be human-friendly:

1. `Review Decision`
- recommended action (`comment` / `request changes` / `approve` / `merge-ready`)
- whether it is blocking
- confidence

2. `Findings`
- list findings in severity order `P1 -> P3`
- include file/line evidence and impact
- if none, state `no blocking findings`

3. `Contract Check`
- if issue-to-pr handoff is available, report goal/criteria alignment
- call out any non-goal violations

4. `Issue Coverage`
- if linked issue exists: verdict `full` / `partial` / `not addressed`
- list scenario statuses (`resolved`/`partially resolved`/`unresolved`) with code-test evidence
- if no linked issue: state `no linked issue` and show inferred scope source

5. `Risk and Gate Status`
- required checks summary
- residual risks and testing gaps
- merge preconditions

6. `Publish-ready Maintainer Review Draft`
- draft body for selected action

7. `Publish Gate`
- explicit confirmation question before sending

If `output_mode=pipeline`, append one machine-readable block after the human output:

```yaml
handoff:
  review_decision:
    action: "comment|request changes|approve|merge-ready"
    blocking: false
    decision_confidence: "high|medium|low"
  findings: []
  contract_check:
    goal_match: "pass|partial|fail|unknown"
    acceptance_criteria_status: []
    non_goal_violations: []
  issue_coverage:
    linked_issue: true
    verdict: "full|partial|not addressed|inferred-no-issue"
    scenarios: []
  gate_status:
    required_checks: []
    residual_risks: []
    merge_preconditions: []
```

Default rule: no GitHub comment/review is sent until user explicitly confirms.
