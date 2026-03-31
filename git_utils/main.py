#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from typing import List, Optional


def require_gh() -> None:
    if not shutil.which("gh"):
        print("gh CLI not found in PATH", file=sys.stderr)
        raise SystemExit(1)


def run_gh(args: List[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["gh"] + args
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def list_open_pr_urls(*, author: Optional[str], label: Optional[str], repo: Optional[str]) -> List[str]:
    args = ["pr", "list", "--json", "url", "--jq", ".[] | .url", "--state", "open"]
    if author:
        args += ["--author", author]
    if label:
        args += ["--label", label]
    if repo:
        args += ["--repo", repo]
    result = run_gh(args)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# dependabot-rebase
# ---------------------------------------------------------------------------


def cmd_dependabot_rebase(args: argparse.Namespace) -> int:
    require_gh()
    urls = list_open_pr_urls(author=args.author, label=args.label, repo=args.repo)
    if not urls:
        print("No open PRs found.")
        return 0

    print(f"Found {len(urls)} open PR(s). Posting '@dependabot rebase' comment on each...")
    errors = 0
    for url in urls:
        if args.dry_run:
            print(f"  [dry-run] would comment on {url}")
            continue
        result = run_gh(["pr", "comment", url, "--body", "@dependabot rebase"], check=False)
        if result.returncode != 0:
            print(f"  [ERROR] {url}: {result.stderr.strip()}", file=sys.stderr)
            errors += 1
        else:
            print(f"  [OK] {url}")

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# pr-urls  (list open PR URLs, one per line)
# ---------------------------------------------------------------------------


def cmd_pr_urls(args: argparse.Namespace) -> int:
    require_gh()
    urls = list_open_pr_urls(author=args.author, label=args.label, repo=args.repo)
    for url in urls:
        print(url)
    return 0


# ---------------------------------------------------------------------------
# merged-branches  (list / delete local branches already merged into a base)
# ---------------------------------------------------------------------------


def local_merged_branches(base: str) -> List[str]:
    result = subprocess.run(
        ["git", "branch", "--merged", base],
        text=True,
        capture_output=True,
        check=True,
    )
    branches: List[str] = []
    for line in result.stdout.splitlines():
        name = line.strip().lstrip("* ")
        if name and name != base and not name.startswith("(HEAD"):
            branches.append(name)
    return branches


def current_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def cmd_merged_branches(args: argparse.Namespace) -> int:
    branches = local_merged_branches(args.base)
    if not branches:
        print(f"No local branches fully merged into '{args.base}'.")
        return 0

    print(f"Local branches merged into '{args.base}':")
    for branch in branches:
        print(f"  {branch}")

    if not args.delete:
        print("\nRe-run with --delete to remove them.")
        return 0

    if not args.yes:
        response = input(f"\nDelete {len(branches)} branch(es)? [y/N]: ").strip().lower()
        if response != "y":
            print("Aborted.")
            return 0

    errors = 0
    head = current_branch()
    for branch in branches:
        if branch == head:
            print(f"  [SKIP] {branch} (currently checked out)")
            continue
        result = subprocess.run(
            ["git", "branch", "-d", branch],
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            print(f"  [ERROR] {branch}: {result.stderr.strip()}", file=sys.stderr)
            errors += 1
        else:
            print(f"  [DELETED] {branch}")

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# remote-prune  (fetch --prune + show what was removed)
# ---------------------------------------------------------------------------


def cmd_remote_prune(args: argparse.Namespace) -> int:
    remote = args.remote
    print(f"Pruning stale remote-tracking branches for '{remote}'...")
    result = subprocess.run(
        ["git", "fetch", "--prune", remote],
        text=True,
        capture_output=True,
    )
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output)
    if result.returncode != 0:
        return 1
    print("Done.")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Git / GitHub utility belt.")
    sub = parser.add_subparsers(dest="command", required=True)

    # dependabot-rebase
    p_dr = sub.add_parser(
        "dependabot-rebase",
        help="Post '@dependabot rebase' on every open PR.",
    )
    p_dr.add_argument("--author", default="app/dependabot", help="Filter PRs by author (default: app/dependabot).")
    p_dr.add_argument("--label", default=None, help="Filter PRs by label.")
    p_dr.add_argument("--repo", default=None, help="Target repo in owner/name form (defaults to current repo).")
    p_dr.add_argument("--dry-run", action="store_true", help="Print what would happen without posting comments.")

    # pr-urls
    p_pu = sub.add_parser("pr-urls", help="Print open PR URLs, one per line.")
    p_pu.add_argument("--author", default=None, help="Filter by PR author.")
    p_pu.add_argument("--label", default=None, help="Filter by label.")
    p_pu.add_argument("--repo", default=None, help="Target repo in owner/name form.")

    # merged-branches
    p_mb = sub.add_parser("merged-branches", help="List (and optionally delete) local branches merged into a base.")
    p_mb.add_argument("--base", default="main", help="Base branch to compare against (default: main).")
    p_mb.add_argument("--delete", action="store_true", help="Delete the merged branches.")
    p_mb.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt.")

    # remote-prune
    p_rp = sub.add_parser("remote-prune", help="Fetch and prune stale remote-tracking branches.")
    p_rp.add_argument("remote", nargs="?", default="origin", help="Remote name (default: origin).")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dispatch = {
        "dependabot-rebase": cmd_dependabot_rebase,
        "pr-urls": cmd_pr_urls,
        "merged-branches": cmd_merged_branches,
        "remote-prune": cmd_remote_prune,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
