# sofastack-skills

Maintainer skills and workflows for semi-automated SOFAStack community operations.

## Skills

### 1) `sofastack-issue-review`

Review and triage SOFAStack issues, request only the missing evidence that matters, and draft maintainer replies.

### 2) `sofastack-pr-review`

Run maintainer-grade PR review for SOFAStack repositories with compatibility and regression focus.

### 3) `sofastack-community-review`

Run the scheduled SOFAStack GitHub community review automation for the v1 target repositories:

- `sofastack/sofa-rpc`
- `sofastack/sofa-jraft`
- `sofastack/sofa-boot`
- `sofastack/sofa-bolt`
- `sofastack/sofa-registry`
- `sofastack/sofa-tracer`
- `sofastack/sofa-ark`

It includes a deterministic org-level wrapper at `sofastack-community-review/scripts/scan_org.py` and machine-readable repo policy in `sofastack-community-review/references/repo-policy.json`.

## Quick Usage

```text
Use $sofastack-issue-review <issue-id>
Use $sofastack-pr-review <pr-id>
Use $sofastack-community-review
```

## Repository Layout

```text
sofastack-issue-review/
sofastack-pr-review/
sofastack-community-review/
```

Each skill contains its own `SKILL.md` and optional `references/`, `scripts/`, or `agents/` content.
