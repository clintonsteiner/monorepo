from __future__ import annotations

from unittest.mock import MagicMock, patch

from git_utils.main import cmd_dependabot_rebase, cmd_merged_branches, cmd_pr_urls, cmd_remote_prune, list_open_pr_urls

# ---------------------------------------------------------------------------
# list_open_pr_urls
# ---------------------------------------------------------------------------


def _make_args(**kwargs):
    m = MagicMock()
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


@patch("git_utils.main.run_gh")
def test_list_open_pr_urls_basic(mock_run):
    mock_run.return_value = MagicMock(stdout="https://github.com/o/r/pull/1\nhttps://github.com/o/r/pull/2\n")
    urls = list_open_pr_urls(author="app/dependabot", label=None, repo=None)
    assert urls == ["https://github.com/o/r/pull/1", "https://github.com/o/r/pull/2"]
    called_args = mock_run.call_args[0][0]
    assert "--author" in called_args
    assert "app/dependabot" in called_args


@patch("git_utils.main.run_gh")
def test_list_open_pr_urls_empty(mock_run):
    mock_run.return_value = MagicMock(stdout="\n  \n")
    urls = list_open_pr_urls(author=None, label=None, repo=None)
    assert urls == []


# ---------------------------------------------------------------------------
# cmd_dependabot_rebase
# ---------------------------------------------------------------------------


@patch("git_utils.main.run_gh")
@patch("git_utils.main.require_gh")
def test_dependabot_rebase_dry_run(mock_req, mock_run, capsys):
    mock_run.return_value = MagicMock(stdout="https://github.com/o/r/pull/1\n")
    args = _make_args(author="app/dependabot", label=None, repo=None, dry_run=True)
    rc = cmd_dependabot_rebase(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "dry-run" in out
    # comment call should NOT have been made
    for c in mock_run.call_args_list:
        assert "comment" not in c[0][0]


@patch("git_utils.main.run_gh")
@patch("git_utils.main.require_gh")
def test_dependabot_rebase_no_prs(mock_req, mock_run, capsys):
    mock_run.return_value = MagicMock(stdout="")
    args = _make_args(author="app/dependabot", label=None, repo=None, dry_run=False)
    rc = cmd_dependabot_rebase(args)
    assert rc == 0
    assert "No open PRs" in capsys.readouterr().out


@patch("git_utils.main.run_gh")
@patch("git_utils.main.require_gh")
def test_dependabot_rebase_posts_comments(mock_req, mock_run):
    pr_url = "https://github.com/o/r/pull/42"
    list_result = MagicMock(stdout=pr_url + "\n")
    comment_result = MagicMock(returncode=0, stderr="")

    mock_run.side_effect = [list_result, comment_result]
    args = _make_args(author="app/dependabot", label=None, repo=None, dry_run=False)
    rc = cmd_dependabot_rebase(args)
    assert rc == 0
    # second call should be the comment
    comment_call_args = mock_run.call_args_list[1][0][0]
    assert "comment" in comment_call_args
    assert "@dependabot rebase" in comment_call_args
    assert pr_url in comment_call_args


# ---------------------------------------------------------------------------
# cmd_pr_urls
# ---------------------------------------------------------------------------


@patch("git_utils.main.run_gh")
@patch("git_utils.main.require_gh")
def test_pr_urls_output(mock_req, mock_run, capsys):
    mock_run.return_value = MagicMock(stdout="https://github.com/o/r/pull/1\n")
    args = _make_args(author=None, label=None, repo=None)
    rc = cmd_pr_urls(args)
    assert rc == 0
    assert "https://github.com/o/r/pull/1" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# cmd_merged_branches
# ---------------------------------------------------------------------------


@patch("git_utils.main.subprocess.run")
def test_merged_branches_list_only(mock_run, capsys):
    mock_run.return_value = MagicMock(stdout="  main\n  feature/done\n  old-branch\n", returncode=0)
    args = _make_args(base="main", delete=False, yes=False)
    rc = cmd_merged_branches(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "feature/done" in out
    assert "old-branch" in out
    assert "Re-run with --delete" in out


@patch("git_utils.main.subprocess.run")
def test_merged_branches_none(mock_run, capsys):
    mock_run.return_value = MagicMock(stdout="  main\n", returncode=0)
    args = _make_args(base="main", delete=False, yes=False)
    rc = cmd_merged_branches(args)
    assert rc == 0
    assert "No local branches" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# cmd_remote_prune
# ---------------------------------------------------------------------------


@patch("git_utils.main.subprocess.run")
def test_remote_prune_success(mock_run, capsys):
    mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
    args = _make_args(remote="origin")
    rc = cmd_remote_prune(args)
    assert rc == 0
    called = mock_run.call_args[0][0]
    assert "fetch" in called
    assert "--prune" in called
    assert "origin" in called
