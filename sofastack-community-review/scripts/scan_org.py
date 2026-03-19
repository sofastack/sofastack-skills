#!/usr/bin/env python3
"""Scan all SOFAStack v1 repositories for candidate community-review threads."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import runtime_paths

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_POLICY = SKILL_ROOT / "references" / "repo-policy.json"
COMMUNITY_REVIEW = SCRIPT_DIR / "community_review.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-file", type=Path, default=DEFAULT_POLICY)
    parser.add_argument(
        "--actor",
        default=None,
        help="Override actor login; otherwise resolve from env, optional policy override, or gh auth",
    )
    parser.add_argument("--state-file", type=Path, default=None)
    parser.add_argument("--initial-lookback-hours", type=int, default=4)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def load_policy(path: Path) -> dict:
    return json.loads(path.read_text())


def resolve_gh_login() -> str | None:
    try:
        result = subprocess.run(
            ["gh", "api", "user"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    output = result.stdout.strip()
    if not output:
        return None
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        return None

    login = payload.get("login")
    if isinstance(login, str) and login.strip():
        return login.strip()
    return None


def resolve_actor(cli_actor: str | None, policy: dict[str, Any]) -> str:
    actor = (
        cli_actor
        or os.getenv("SOFASTACK_REVIEW_ACTOR")
        or os.getenv("GITHUB_ACTOR")
        or policy.get("actor")
        or resolve_gh_login()
    )
    if actor:
        return actor
    raise SystemExit(
        "missing actor: pass --actor, set SOFASTACK_REVIEW_ACTOR/GITHUB_ACTOR, "
        "or authenticate gh so the current login can be resolved"
    )


def run_scan(repo: str, actor: str, maintainers: list[str], lookback: int, state_file: Path) -> list[dict]:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(COMMUNITY_REVIEW),
        "scan",
        "--repo",
        repo,
        "--actor",
        actor,
        "--maintainers",
        ",".join(maintainers),
        "--initial-lookback-hours",
        str(lookback),
        "--state-file",
        str(state_file),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    output = result.stdout.strip() or "[]"
    return json.loads(output)


def main() -> None:
    args = parse_args()
    policy = load_policy(args.policy_file)
    actor = resolve_actor(args.actor, policy)
    state_file = runtime_paths.resolve_state_file(args.state_file, policy=policy)
    flat: list[dict] = []
    by_repo: list[dict] = []

    for entry in policy["repos"]:
        repo = entry["repo"]
        maintainers = entry["maintainers"]
        candidates = run_scan(repo, actor, maintainers, args.initial_lookback_hours, state_file)
        by_repo.append({
            "repo": repo,
            "candidateCount": len(candidates),
            "candidates": candidates,
        })
        flat.extend(candidates)

    payload = {
        "actor": actor,
        "stateFile": str(state_file),
        "repoCount": len(policy["repos"]),
        "candidateCount": len(flat),
        "byRepo": by_repo,
        "candidates": flat,
    }
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
