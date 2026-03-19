from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scan_org


class ScanOrgTest(unittest.TestCase):
    def test_resolve_actor_prefers_cli_argument(self):
        with patch.dict(os.environ, {"SOFASTACK_REVIEW_ACTOR": "env-user"}, clear=True), patch.object(
            scan_org,
            "resolve_gh_login",
            return_value="gh-user",
        ):
            actor = scan_org.resolve_actor("cli-user", {"actor": "policy-user"})

        self.assertEqual("cli-user", actor)

    def test_resolve_actor_uses_environment_before_policy(self):
        with patch.dict(os.environ, {"SOFASTACK_REVIEW_ACTOR": "env-user"}, clear=True), patch.object(
            scan_org,
            "resolve_gh_login",
            return_value="gh-user",
        ):
            actor = scan_org.resolve_actor(None, {"actor": "policy-user"})

        self.assertEqual("env-user", actor)

    def test_resolve_actor_uses_policy_override_when_present(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            scan_org,
            "resolve_gh_login",
            return_value="gh-user",
        ):
            actor = scan_org.resolve_actor(None, {"actor": "policy-user"})

        self.assertEqual("policy-user", actor)

    def test_resolve_actor_falls_back_to_gh_login(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            scan_org,
            "resolve_gh_login",
            return_value="gh-user",
        ):
            actor = scan_org.resolve_actor(None, {})

        self.assertEqual("gh-user", actor)

    def test_resolve_actor_errors_when_no_source_is_available(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(scan_org, "resolve_gh_login", return_value=None):
            with self.assertRaises(SystemExit) as cm:
                scan_org.resolve_actor(None, {})

        self.assertIn("missing actor", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
