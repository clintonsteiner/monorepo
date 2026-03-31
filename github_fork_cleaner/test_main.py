import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from github_fork_cleaner import main


class MainTests(unittest.TestCase):
    def test_classify_my_fork_prefers_review_for_stale_fork_with_open_pr(self) -> None:
        recommendation, reasons = main.classify_my_fork(
            days_since_push_value=250,
            stale_days=180,
            ahead=0,
            behind=12,
            archived=False,
            open_prs=True,
        )
        self.assertEqual(recommendation, "review")
        self.assertIn("has open pull requests", reasons)
        self.assertIn("12 commit(s) behind parent", reasons)

    def test_classify_my_fork_marks_archived_stale_fork_for_delete(self) -> None:
        recommendation, reasons = main.classify_my_fork(
            days_since_push_value=365,
            stale_days=180,
            ahead=0,
            behind=0,
            archived=True,
            open_prs=False,
        )
        self.assertEqual(recommendation, "delete-candidate")
        self.assertIn("already archived", reasons)

    def test_audit_network_forks_sorts_dormant_before_watch_before_active(self) -> None:
        repo = {"default_branch": "main"}
        forks = [
            {
                "full_name": "acme/active-fork",
                "owner": {"login": "acme"},
                "archived": False,
                "pushed_at": "2026-03-20T00:00:00Z",
                "default_branch": "main",
            },
            {
                "full_name": "acme/watch-fork",
                "owner": {"login": "acme"},
                "archived": False,
                "pushed_at": "2026-03-01T00:00:00Z",
                "default_branch": "main",
            },
            {
                "full_name": "acme/dormant-fork",
                "owner": {"login": "acme"},
                "archived": False,
                "pushed_at": "2025-01-01T00:00:00Z",
                "default_branch": "main",
            },
        ]

        ops = mock.Mock()
        ops.get_repo.return_value = repo
        ops.list_forks_of.return_value = forks
        ops.compare.side_effect = [
            {"ahead": 2, "behind": 0},
            {"ahead": 0, "behind": 3},
            {"ahead": 0, "behind": 10},
        ]

        rows = main.audit_network_forks(ops, "owner/repo", stale_days=180)

        self.assertEqual([row.full_name for row in rows], ["acme/dormant-fork", "acme/watch-fork", "acme/active-fork"])
        self.assertEqual([row.recommendation for row in rows], ["dormant", "watch", "active"])

    def test_parse_args_supports_legacy_audit_flags(self) -> None:
        with mock.patch("sys.argv", ["main.py", "--mode", "my-forks", "--days", "90", "--archive", "--yes"]):
            args = main.parse_args()

        self.assertEqual(args.command, "audit")
        self.assertEqual(args.days, 90)
        self.assertTrue(args.archive_recommended)
        self.assertTrue(args.yes)

    def test_write_report_json_outputs_rows(self) -> None:
        row = main.ForkAuditRow(
            full_name="acme/fork",
            parent="upstream/repo",
            visibility="public",
            archived=False,
            open_prs=False,
            ahead=0,
            behind=5,
            last_push="2026-01-01T00:00:00Z",
            days_since_push=89,
            score=2,
            recommendation="keep",
            reasons="behind parent",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.json"
            main.write_report(str(path), [row], "Fork portfolio audit")
            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload[0]["full_name"], "acme/fork")
        self.assertEqual(payload[0]["recommendation"], "keep")

    def test_maybe_apply_actions_runs_only_recommended_targets(self) -> None:
        rows = [
            main.ForkAuditRow(
                full_name="acme/archive-me",
                parent="upstream/repo",
                visibility="public",
                archived=False,
                open_prs=False,
                ahead=0,
                behind=0,
                last_push="2025-01-01T00:00:00Z",
                days_since_push=400,
                score=20,
                recommendation="archive-candidate",
                reasons="stale",
            ),
            main.ForkAuditRow(
                full_name="acme/delete-me",
                parent="upstream/repo",
                visibility="public",
                archived=True,
                open_prs=False,
                ahead=0,
                behind=0,
                last_push="2025-01-01T00:00:00Z",
                days_since_push=400,
                score=24,
                recommendation="delete-candidate",
                reasons="stale",
            ),
            main.ForkAuditRow(
                full_name="acme/keep-me",
                parent="upstream/repo",
                visibility="public",
                archived=False,
                open_prs=False,
                ahead=3,
                behind=0,
                last_push="2026-03-01T00:00:00Z",
                days_since_push=20,
                score=0,
                recommendation="keep",
                reasons="ahead",
            ),
        ]
        ops = mock.Mock()

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            main.maybe_apply_actions(
                ops,
                rows,
                archive_recommended=True,
                delete_recommended=True,
                yes=True,
            )

        ops.set_archived.assert_called_once_with("acme/archive-me", True)
        ops.delete_repo.assert_called_once_with("acme/delete-me")
        self.assertIn("Planned changes: 1 archive, 1 delete", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
