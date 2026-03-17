#!/usr/bin/env python3
"""Scan all SOFAStack v1 repositories for candidate community-review threads."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_POLICY = SKILL_ROOT / "references" / "repo-policy.json"
DEFAULT_STATE = Path.home() / ".codex" / "tmp" / "sofastack-community-review" / "state.json"
COMMUNITY_REVIEW = SCRIPT_DIR / "community_review.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-file", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--actor", default=None, help="Override actor login; defaults to policy actor")
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--initial-lookback-hours", type=int, default=4)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def load_policy(path: Path) -> dict:
    return json.loads(path.read_text())


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
    actor = args.actor or policy.get("actor") or "nobodyiam"
    flat: list[dict] = []
    by_repo: list[dict] = []

    for entry in policy["repos"]:
        repo = entry["repo"]
        maintainers = entry["maintainers"]
        candidates = run_scan(repo, actor, maintainers, args.initial_lookback_hours, args.state_file)
        by_repo.append({
            "repo": repo,
            "candidateCount": len(candidates),
            "candidates": candidates,
        })
        flat.extend(candidates)

    payload = {
        "actor": actor,
        "stateFile": str(args.state_file),
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
