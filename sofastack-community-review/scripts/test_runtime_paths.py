from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import runtime_paths


class RuntimePathsTest(unittest.TestCase):
    def test_default_state_file_prefers_explicit_env(self):
        with patch.dict(os.environ, {runtime_paths.STATE_FILE_ENV: "~/custom/state.json"}, clear=True):
            self.assertEqual(Path.home() / "custom" / "state.json", runtime_paths.default_state_file())

    def test_default_state_file_uses_home_override_before_xdg(self):
        with patch.dict(
            os.environ,
            {
                runtime_paths.HOME_ENV: "~/review-home",
                "XDG_STATE_HOME": "~/ignored-state",
            },
            clear=True,
        ):
            self.assertEqual(Path.home() / "review-home" / "state.json", runtime_paths.default_state_file())

    def test_default_state_file_falls_back_to_xdg_state(self):
        with patch.dict(os.environ, {"XDG_STATE_HOME": "~/state-root"}, clear=True):
            self.assertEqual(
                Path.home() / "state-root" / runtime_paths.SKILL_SLUG / "state.json",
                runtime_paths.default_state_file(),
            )

    def test_default_mirror_root_falls_back_to_xdg_cache(self):
        with patch.dict(os.environ, {"XDG_CACHE_HOME": "~/cache-root"}, clear=True):
            self.assertEqual(
                Path.home() / "cache-root" / runtime_paths.SKILL_SLUG / "mirrors",
                runtime_paths.default_mirror_root(),
            )

    def test_resolve_state_file_uses_policy_when_cli_value_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            resolved = runtime_paths.resolve_state_file(None, policy={"stateFile": "~/policy/state.json"})

        self.assertEqual(Path.home() / "policy" / "state.json", resolved)

    def test_resolve_state_file_prefers_skill_env_over_policy(self):
        with patch.dict(
            os.environ,
            {runtime_paths.STATE_FILE_ENV: "~/env/state.json"},
            clear=True,
        ):
            resolved = runtime_paths.resolve_state_file(None, policy={"stateFile": "~/policy/state.json"})

        self.assertEqual(Path.home() / "env" / "state.json", resolved)


if __name__ == "__main__":
    unittest.main()
