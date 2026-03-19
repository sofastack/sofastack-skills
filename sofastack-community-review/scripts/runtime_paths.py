#!/usr/bin/env python3
"""Path resolution helpers for SOFAStack community review runtime state."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping, Any

SKILL_SLUG = "sofastack-community-review"
STATE_FILE_ENV = "SOFASTACK_COMMUNITY_REVIEW_STATE_FILE"
MIRROR_ROOT_ENV = "SOFASTACK_COMMUNITY_REVIEW_MIRROR_ROOT"
HOME_ENV = "SOFASTACK_COMMUNITY_REVIEW_HOME"


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(str(value))).expanduser()


def _xdg_dir(env_name: str, home_fallback: str) -> Path:
    configured = os.getenv(env_name)
    if configured:
        return expand_path(configured)
    return Path.home() / home_fallback


def _storage_home() -> Path | None:
    configured = os.getenv(HOME_ENV)
    if configured:
        return expand_path(configured)
    return None


def default_state_file() -> Path:
    configured = os.getenv(STATE_FILE_ENV)
    if configured:
        return expand_path(configured)

    storage_home = _storage_home()
    if storage_home is not None:
        return storage_home / "state.json"

    return _xdg_dir("XDG_STATE_HOME", ".local/state") / SKILL_SLUG / "state.json"


def default_mirror_root() -> Path:
    configured = os.getenv(MIRROR_ROOT_ENV)
    if configured:
        return expand_path(configured)

    storage_home = _storage_home()
    if storage_home is not None:
        return storage_home / "mirrors"

    return _xdg_dir("XDG_CACHE_HOME", ".cache") / SKILL_SLUG / "mirrors"


def resolve_state_file(value: str | Path | None = None, *, policy: Mapping[str, Any] | None = None) -> Path:
    if value:
        return expand_path(value)

    if os.getenv(STATE_FILE_ENV) or os.getenv(HOME_ENV):
        return default_state_file()

    if policy:
        policy_value = policy.get("stateFile")
        if isinstance(policy_value, str) and policy_value.strip():
            return expand_path(policy_value)

    return default_state_file()
