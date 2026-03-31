#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Iterable, List, Optional

API = "https://api.github.com"


def iso_to_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def build_qs(params: Dict[str, Any]) -> str:
    filtered = {key: value for key, value in params.items() if value is not None}
    return urllib.parse.urlencode(filtered)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def days_ago(value: str) -> int:
    return max(0, (now_utc() - iso_to_dt(value)).days)


def clamp_width(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    if width <= 1:
        return value[:width]
    return value[: width - 1] + "..."


def joined_reasons(reasons: List[str]) -> str:
    if reasons:
        return ", ".join(reasons)
    return "-"


def emit_json(rows: List[Any]) -> None:
    print(json.dumps([asdict(row) for row in rows], indent=2))


class BaseClient:
    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Any = None,
    ) -> Any:
        raise NotImplementedError

    def paginated(self, path: str, params: Dict[str, Any]) -> Generator[Any, None, None]:
        raise NotImplementedError


class RequestsClient(BaseClient):
    def __init__(self, token: str, verbose: bool = False):
        import requests

        self.session = requests.Session()
        self.verbose = verbose
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "github-fork-cleaner",
            }
        )

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Any = None,
    ) -> Any:
        url = API + path
        while True:
            response = self.session.request(method, url, params=params, json=json_body)
            if self.verbose:
                sys.stderr.write(f"{method} {url} -> {response.status_code}\n")
            if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
                reset = int(response.headers.get("X-RateLimit-Reset", "0"))
                time.sleep(max(0, reset - int(time.time()) + 1))
                continue
            if response.status_code >= 400:
                try:
                    message = response.json().get("message", response.text)
                except Exception:
                    message = response.text
                raise RuntimeError(f"{method} {path} -> {response.status_code}: {message}")
            if response.text:
                return response.json()
            return None

    def paginated(self, path: str, params: Dict[str, Any]) -> Generator[Any, None, None]:
        url = API + path
        next_params = dict(params)
        while True:
            response = self.session.get(url, params=next_params)
            if response.status_code >= 400:
                try:
                    message = response.json().get("message", response.text)
                except Exception:
                    message = response.text
                raise RuntimeError(f"GET {path} -> {response.status_code}: {message}")
            payload = response.json()
            if not isinstance(payload, list):
                break
            for item in payload:
                yield item
            next_url = None
            for part in response.headers.get("Link", "").split(","):
                if 'rel="next"' in part:
                    next_url = part[part.find("<") + 1 : part.find(">")]
            if not next_url:
                break
            url = next_url
            next_params = {}


class GhCliClient(BaseClient):
    def __init__(self, verbose: bool = False):
        if not shutil.which("gh"):
            raise RuntimeError("gh CLI not found in PATH")
        self.verbose = verbose

    def _run(self, args: List[str], input_str: Optional[str] = None) -> str:
        cmd = ["gh", "api"] + args
        if self.verbose:
            suffix = ""
            if input_str is not None:
                suffix = f" [stdin {len(input_str)} bytes]"
            sys.stderr.write("$ " + " ".join(cmd) + suffix + "\n")
        result = subprocess.run(cmd, input=input_str, text=True, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "gh api error")
        return result.stdout

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Any = None,
    ) -> Any:
        qs = ""
        if params:
            qs = f"?{build_qs(params)}"
        args = ["--method", method, path + qs]
        if json_body is not None:
            args += ["--input", "-"]
            output = self._run(args, input_str=json.dumps(json_body))
        else:
            output = self._run(args)
        if output.strip():
            return json.loads(output)
        return None

    def paginated(self, path: str, params: Dict[str, Any]) -> Generator[Any, None, None]:
        page = 1
        per_page = params.get("per_page", 100)
        while True:
            page_params = dict(params)
            page_params["page"] = page
            page_params["per_page"] = per_page
            payload = self.request("GET", path, params=page_params)
            if not isinstance(payload, list):
                break
            for item in payload:
                yield item
            if len(payload) < per_page:
                break
            page += 1


def choose_client(auth_mode: str, token: Optional[str], verbose: bool) -> BaseClient:
    if auth_mode in {"auto", "token"} and token:
        try:
            client = RequestsClient(token, verbose=verbose)
            client.request("GET", "/user")
            return client
        except Exception as exc:
            if auth_mode == "token":
                raise RuntimeError(f"token auth failed: {exc}") from exc
            print(f"Token auth unavailable, falling back to gh: {exc}", file=sys.stderr)

    if auth_mode in {"auto", "gh"}:
        client = GhCliClient(verbose=verbose)
        client.request("GET", "/user")
        return client

    raise RuntimeError("No working GitHub client found. Provide --token or install/authenticate gh.")


class GitHubOps:
    def __init__(self, client: BaseClient):
        self.client = client

    def get_repo(self, repo_full: str) -> Dict[str, Any]:
        return self.client.request("GET", f"/repos/{repo_full}")

    def list_my_repos(self) -> Generator[Dict[str, Any], None, None]:
        params = {"affiliation": "owner", "per_page": 100, "sort": "pushed"}
        yield from self.client.paginated("/user/repos", params)

    def list_forks_of(self, repo_full: str) -> Generator[Dict[str, Any], None, None]:
        owner, repo = repo_full.split("/", 1)
        params = {"per_page": 100, "sort": "newest"}
        yield from self.client.paginated(f"/repos/{owner}/{repo}/forks", params)

    def compare(
        self,
        parent_full: str,
        parent_default: str,
        fork_full: str,
        fork_default: str,
    ) -> Optional[Dict[str, int]]:
        parent_owner = parent_full.split("/")[0]
        fork_owner = fork_full.split("/")[0]
        path = f"/repos/{parent_full}/compare/{parent_owner}:{parent_default}...{fork_owner}:{fork_default}"
        try:
            payload = self.client.request("GET", path)
        except RuntimeError:
            return None
        return {
            "ahead": payload.get("ahead_by", 0),
            "behind": payload.get("behind_by", 0),
        }

    def has_open_prs(self, repo_full: str) -> bool:
        prs = self.client.request("GET", f"/repos/{repo_full}/pulls", params={"state": "open", "per_page": 1})
        return isinstance(prs, list) and len(prs) > 0

    def delete_repo(self, repo_full: str) -> None:
        self.client.request("DELETE", f"/repos/{repo_full}")

    def set_archived(self, repo_full: str, archive: bool) -> None:
        self.client.request("PATCH", f"/repos/{repo_full}", json_body={"archived": archive})


@dataclass
class ForkAuditRow:
    full_name: str
    parent: str
    visibility: str
    archived: bool
    open_prs: bool
    ahead: int
    behind: int
    last_push: str
    days_since_push: int
    score: int
    recommendation: str
    reasons: str


@dataclass
class NetworkAuditRow:
    full_name: str
    owner: str
    archived: bool
    ahead: int
    behind: int
    last_push: str
    days_since_push: Optional[int]
    recommendation: str
    reasons: str


def score_fork(days_since_push: int, ahead: int, open_prs: bool, archived: bool) -> int:
    score = min(days_since_push // 30, 24)
    if ahead > 0:
        score -= min(ahead, 10)
    if open_prs:
        score -= 6
    if archived:
        score += 4
    return max(0, score)


def classify_my_fork(
    *,
    days_since_push_value: int,
    stale_days: int,
    ahead: int,
    behind: int,
    archived: bool,
    open_prs: bool,
) -> tuple[str, List[str]]:
    reasons: List[str] = []
    if ahead > 0:
        reasons.append(f"{ahead} commit(s) ahead of parent")
    if behind > 0:
        reasons.append(f"{behind} commit(s) behind parent")
    if open_prs:
        reasons.append("has open pull requests")
    if archived:
        reasons.append("already archived")
    if days_since_push_value >= stale_days:
        reasons.append(f"stale for {days_since_push_value} day(s)")

    if ahead > 0:
        return "keep", reasons
    if open_prs:
        return "review", reasons
    if days_since_push_value < stale_days:
        return "keep", reasons
    if archived:
        return "delete-candidate", reasons
    return "archive-candidate", reasons


def classify_network_fork(
    *,
    days_since_push_value: Optional[int],
    stale_days: int,
    ahead: int,
    archived: bool,
) -> tuple[str, List[str]]:
    reasons: List[str] = []
    if ahead > 0:
        reasons.append(f"{ahead} commit(s) ahead of parent")
    if archived:
        reasons.append("archived")
    if days_since_push_value is not None and days_since_push_value >= stale_days:
        reasons.append(f"stale for {days_since_push_value} day(s)")

    if ahead > 0:
        return "active", reasons
    if days_since_push_value is not None and days_since_push_value >= stale_days:
        return "dormant", reasons
    return "watch", reasons


def fork_audit_sort_key(row: ForkAuditRow) -> tuple[bool, bool, bool, int, str]:
    return (
        row.recommendation != "delete-candidate",
        row.recommendation != "archive-candidate",
        row.recommendation != "review",
        -row.score,
        row.full_name,
    )


def network_audit_sort_key(row: NetworkAuditRow) -> tuple[int, int, str]:
    priority = {"dormant": 0, "watch": 1, "active": 2}
    if row.days_since_push is None:
        days_component = 1
    else:
        days_component = -row.days_since_push
    return (days_component, priority.get(row.recommendation, 99), row.full_name)


def audit_my_forks(
    ops: GitHubOps,
    *,
    stale_days: int,
    include_private: bool,
    ignore: List[str],
) -> List[ForkAuditRow]:
    rows: List[ForkAuditRow] = []
    ignored = set(ignore)
    for repo in ops.list_my_repos():
        if not repo.get("fork"):
            continue
        full_name = repo["full_name"]
        if repo["name"] in ignored or full_name in ignored:
            continue
        if repo.get("private") and not include_private:
            continue
        parent = repo.get("parent")
        if not parent:
            continue
        last_push = repo.get("pushed_at") or repo.get("updated_at")
        if not last_push:
            continue
        days_since_push_value = days_ago(last_push)
        default_branch = repo.get("default_branch") or "main"
        parent_full = parent["full_name"]
        parent_default = parent.get("default_branch") or "main"
        compare = ops.compare(parent_full, parent_default, full_name, default_branch) or {"ahead": 0, "behind": 0}
        open_prs = ops.has_open_prs(full_name)
        archived = bool(repo.get("archived"))
        recommendation, reasons = classify_my_fork(
            days_since_push_value=days_since_push_value,
            stale_days=stale_days,
            ahead=compare["ahead"],
            behind=compare["behind"],
            archived=archived,
            open_prs=open_prs,
        )
        rows.append(
            ForkAuditRow(
                full_name=full_name,
                parent=parent_full,
                visibility="private" if repo.get("private") else "public",
                archived=archived,
                open_prs=open_prs,
                ahead=compare["ahead"],
                behind=compare["behind"],
                last_push=last_push,
                days_since_push=days_since_push_value,
                score=score_fork(days_since_push_value, compare["ahead"], open_prs, archived),
                recommendation=recommendation,
                reasons=joined_reasons(reasons),
            )
        )
    return sorted(rows, key=fork_audit_sort_key)


def audit_network_forks(ops: GitHubOps, repo_full: str, *, stale_days: int) -> List[NetworkAuditRow]:
    parent = ops.get_repo(repo_full)
    parent_default = parent.get("default_branch") or "main"
    rows: List[NetworkAuditRow] = []
    for fork in ops.list_forks_of(repo_full):
        full_name = fork["full_name"]
        last_push = fork.get("pushed_at") or fork.get("updated_at")
        days_since_push_value = days_ago(last_push) if last_push else None
        default_branch = fork.get("default_branch") or "main"
        compare = ops.compare(repo_full, parent_default, full_name, default_branch) or {"ahead": 0, "behind": 0}
        recommendation, reasons = classify_network_fork(
            days_since_push_value=days_since_push_value,
            stale_days=stale_days,
            ahead=compare["ahead"],
            archived=bool(fork.get("archived")),
        )
        rows.append(
            NetworkAuditRow(
                full_name=full_name,
                owner=fork["owner"]["login"],
                archived=bool(fork.get("archived")),
                ahead=compare["ahead"],
                behind=compare["behind"],
                last_push=last_push or "",
                days_since_push=days_since_push_value,
                recommendation=recommendation,
                reasons=joined_reasons(reasons),
            )
        )
    return sorted(rows, key=network_audit_sort_key)


def summarize_counts(rows: Iterable[Any], field_name: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        key = getattr(row, field_name)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def render_table(headers: List[str], data: List[List[str]]) -> str:
    if not data:
        return ""
    widths = [len(header) for header in headers]
    for row in data:
        for index, cell in enumerate(row):
            widths[index] = min(max(widths[index], len(cell)), 44)

    def format_row(values: List[str]) -> str:
        cells: List[str] = []
        for index, value in enumerate(values):
            cells.append(clamp_width(value, widths[index]).ljust(widths[index]))
        return "  ".join(cells)

    output = [format_row(headers), format_row(["-" * width for width in widths])]
    for row in data:
        output.append(format_row(row))
    return "\n".join(output)


def print_audit_text(rows: List[ForkAuditRow], stale_days: int) -> None:
    print(f"Fork portfolio audit: {len(rows)} fork(s), stale threshold {stale_days} day(s)")
    for recommendation, count in summarize_counts(rows, "recommendation").items():
        print(f"- {recommendation}: {count}")
    print("")
    if not rows:
        print("No forks matched the audit.")
        return

    table_rows: List[List[str]] = []
    for row in rows:
        table_rows.append(
            [
                row.full_name,
                row.recommendation,
                str(row.days_since_push),
                f"{row.ahead}/{row.behind}",
                "yes" if row.open_prs else "no",
                "yes" if row.archived else "no",
                row.reasons,
            ]
        )
    print(render_table(["fork", "recommendation", "days", "ahead/behind", "open-prs", "archived", "why"], table_rows))


def print_network_text(rows: List[NetworkAuditRow], repo_full: str, stale_days: int) -> None:
    print(f"Fork network audit for {repo_full}: {len(rows)} fork(s), stale threshold {stale_days} day(s)")
    for recommendation, count in summarize_counts(rows, "recommendation").items():
        print(f"- {recommendation}: {count}")
    print("")
    if not rows:
        print("No forks found.")
        return

    table_rows: List[List[str]] = []
    for row in rows:
        if row.days_since_push is None:
            days_value = "-"
        else:
            days_value = str(row.days_since_push)
        table_rows.append(
            [
                row.full_name,
                row.recommendation,
                days_value,
                f"{row.ahead}/{row.behind}",
                "yes" if row.archived else "no",
                row.reasons,
            ]
        )
    print(render_table(["fork", "recommendation", "days", "ahead/behind", "archived", "why"], table_rows))


def write_csv(path: str, rows: List[Any]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        if not rows:
            writer = csv.writer(handle)
            writer.writerow(["note"])
            writer.writerow(["no-results"])
            return
        dictionaries = [asdict(row) for row in rows]
        writer = csv.DictWriter(handle, fieldnames=list(dictionaries[0].keys()))
        writer.writeheader()
        writer.writerows(dictionaries)


def write_json(path: str, rows: List[Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump([asdict(row) for row in rows], handle, indent=2)
        handle.write("\n")


def write_markdown(path: str, rows: List[Any], title: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(f"# {title}\n\n")
        if not rows:
            handle.write("No results.\n")
            return
        headers = list(asdict(rows[0]).keys())
        handle.write("| " + " | ".join(headers) + " |\n")
        handle.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for row in rows:
            values = [str(value).replace("\n", " ") for value in asdict(row).values()]
            handle.write("| " + " | ".join(values) + " |\n")


def write_report(path: str, rows: List[Any], title: str) -> None:
    if path.endswith(".csv"):
        write_csv(path, rows)
    elif path.endswith(".json"):
        write_json(path, rows)
    elif path.endswith(".md"):
        write_markdown(path, rows, title)
    else:
        raise RuntimeError("Unsupported output file type. Use .csv, .json, or .md.")
    print(f"Wrote report to {path}")


def maybe_apply_actions(
    ops: GitHubOps,
    rows: List[ForkAuditRow],
    *,
    archive_recommended: bool,
    delete_recommended: bool,
    yes: bool,
) -> None:
    archive_targets = [row for row in rows if archive_recommended and row.recommendation == "archive-candidate"]
    delete_targets = [row for row in rows if delete_recommended and row.recommendation == "delete-candidate"]
    if not archive_targets and not delete_targets:
        return

    print("")
    print(f"Planned changes: {len(archive_targets)} archive, {len(delete_targets)} delete")
    if not yes:
        response = input("Proceed? [y/N]: ").strip().lower()
        if response != "y":
            print("Aborted.")
            return

    for row in archive_targets:
        try:
            ops.set_archived(row.full_name, True)
            print(f"[ARCHIVED] {row.full_name}")
        except Exception as exc:
            print(f"[ERROR] {row.full_name}: {exc}", file=sys.stderr)
    for row in delete_targets:
        try:
            ops.delete_repo(row.full_name)
            print(f"[DELETED] {row.full_name}")
        except Exception as exc:
            print(f"[ERROR] {row.full_name}: {exc}", file=sys.stderr)


def add_common_auth_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--auth", choices=["auto", "token", "gh"], default="auto")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"))
    parser.add_argument("--verbose", action="store_true")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit GitHub forks and suggest what to archive, delete, or keep.")
    subparsers = parser.add_subparsers(dest="command", required=False)

    audit = subparsers.add_parser("audit", help="Audit forks in your own account.")
    audit.add_argument("--days", type=int, default=180, help="Stale threshold in days.")
    audit.add_argument("--include-private", action="store_true")
    audit.add_argument("--ignore", nargs="*", default=[])
    audit.add_argument("--format", choices=["text", "json"], default="text")
    audit.add_argument("--output", help="Write a full report to .csv, .json, or .md.")
    audit.add_argument("--archive-recommended", action="store_true")
    audit.add_argument("--delete-recommended", action="store_true")
    audit.add_argument("--yes", action="store_true")
    add_common_auth_args(audit)

    network = subparsers.add_parser("network", help="Audit forks of a repository.")
    network.add_argument("repo", help="Repository in owner/name form.")
    network.add_argument("--days", type=int, default=180, help="Stale threshold in days.")
    network.add_argument("--format", choices=["text", "json"], default="text")
    network.add_argument("--output", help="Write a full report to .csv, .json, or .md.")
    add_common_auth_args(network)

    parser.add_argument("--mode", choices=["my-forks", "forks-of"], help=argparse.SUPPRESS)
    parser.add_argument("--repo", help=argparse.SUPPRESS)
    parser.add_argument("--archive", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--delete", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--include-private", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--days", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--ignore", nargs="*", help=argparse.SUPPRESS)
    parser.add_argument("--output", help=argparse.SUPPRESS)
    parser.add_argument("--yes", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--verbose", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--auth", choices=["auto", "token", "gh"], help=argparse.SUPPRESS)
    parser.add_argument("--token", help=argparse.SUPPRESS)

    args = parser.parse_args()
    if args.command:
        return args

    legacy_command = "network" if args.mode == "forks-of" else "audit"
    if legacy_command == "network":
        return argparse.Namespace(
            command="network",
            repo=args.repo,
            days=args.days or 180,
            format="text",
            output=args.output,
            auth=args.auth or "auto",
            token=args.token if args.token is not None else os.getenv("GITHUB_TOKEN"),
            verbose=bool(args.verbose),
        )

    return argparse.Namespace(
        command="audit",
        days=args.days or 180,
        include_private=bool(args.include_private),
        ignore=args.ignore or [],
        format="text",
        output=args.output,
        archive_recommended=bool(args.archive),
        delete_recommended=bool(args.delete),
        yes=bool(args.yes),
        auth=args.auth or "auto",
        token=args.token if args.token is not None else os.getenv("GITHUB_TOKEN"),
        verbose=bool(args.verbose),
    )


def main() -> int:
    args = parse_args()
    try:
        client = choose_client(args.auth, args.token, args.verbose)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    ops = GitHubOps(client)
    if args.command == "network":
        if not args.repo or "/" not in args.repo:
            print("Repository must be in owner/name form.", file=sys.stderr)
            return 2
        rows = audit_network_forks(ops, args.repo, stale_days=args.days)
        if args.format == "json":
            emit_json(rows)
        else:
            print_network_text(rows, args.repo, args.days)
        if args.output:
            write_report(args.output, rows, f"Fork network audit for {args.repo}")
        return 0

    rows = audit_my_forks(
        ops,
        stale_days=args.days,
        include_private=args.include_private,
        ignore=args.ignore,
    )
    if args.format == "json":
        emit_json(rows)
    else:
        print_audit_text(rows, args.days)
    if args.output:
        write_report(args.output, rows, "Fork portfolio audit")
    maybe_apply_actions(
        ops,
        rows,
        archive_recommended=args.archive_recommended,
        delete_recommended=args.delete_recommended,
        yes=args.yes,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
