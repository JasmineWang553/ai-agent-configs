#!/usr/bin/env python3
"""Per-role write and shell limits for the team agents (port of the Kiro agent `permissions.rules`).

Claude Code PreToolUse hook. Role = argv[1] (set in each agent's frontmatter), else the `agent_type`
field of the hook input (set inside subagents and `claude --agent` sessions). Unknown role: no decision.

Order per rule set: deny (exit 2) -> ask -> allow-list. A write outside a worker's allow-list asks the user.
shortcut: Bash file writes (redirects, sed -i, cp) are not path-checked, only command prefixes; add checks if roles misuse it.
"""
import fnmatch
import json
import os
import re
import shlex
import sys

HOME = os.path.expanduser("~")
WORK = f"{HOME}/Desktop/work"
PROJECTS = f"{HOME}/Desktop/projects"

DESTRUCTIVE = [
    "git push --force*", "git push -f*", "git push * --force*", "git push * -f*", "rm -rf *", "rm -fr *", "sudo *",
    "git branch -D*", "git -C * branch -D*", "git reset --hard*", "git -C * reset --hard*",
    "git -C * push --force*", "git -C * push -f*", "git clean*", "git -C * clean*",
]
INTEGRATE = [
    "git push*", "git -C * push*", "git -C * merge*", "git -C * rebase*", "git -C * worktree*",
    "glab mr create*", "gh pr create*", "git merge*", "git rebase*", "git worktree*",
]
NO_COMMIT_NO_BUILD = [
    "git commit*", "git -C * commit*", "git checkout*", "git -C * checkout*", "git switch*", "git -C * switch*",
    "git reset*", "git -C * reset*", "git stash*", "git cherry-pick*", "git revert*", "git tag*", "mvn*", "./mvnw*",
]


def T(*names):
    return [f"{WORK}/*/T*/{n}" for n in names]


ROLES = {
    "planning-lead": dict(
        write_allow=[f"{WORK}/**"],
        write_deny=[f"{PROJECTS}/**", f"{WORK}/*/wt/**"],
        shell_deny=DESTRUCTIVE + INTEGRATE + ["git commit*", "git checkout*", "git switch*", "git reset*"],
    ),
    "planner": dict(
        write_allow=[f"{WORK}/*/planning/**"],
        write_deny=[f"{WORK}/*/*.md", f"{WORK}/*/T*/**", f"{WORK}/*/wt/**", f"{PROJECTS}/**"],
        shell_deny=DESTRUCTIVE + INTEGRATE + NO_COMMIT_NO_BUILD,
    ),
    "delivery-lead": dict(
        write_allow=[f"{WORK}/**"],
        write_deny=[f"{PROJECTS}/**"],
        shell_deny=DESTRUCTIVE,
        shell_ask=["git push*", "git -C * push*", "glab mr create*", "gh pr create*",
                   "git worktree remove*", "git -C * worktree remove*"],
    ),
    "test-designer": dict(
        write_allow=T("test-design.md", "notes/td-*.md", "notes/signals/**"),
        write_deny=T("overview.md", "architecture.md", "review.md") + [f"{PROJECTS}/**", f"{WORK}/*/wt/**"],
        shell_deny=DESTRUCTIVE + INTEGRATE + NO_COMMIT_NO_BUILD,
    ),
    "architect": dict(
        write_allow=T("architecture.md", "notes/ar-*.md", "notes/signals/**"),
        write_deny=T("overview.md", "test-design.md", "review.md") + [f"{PROJECTS}/**", f"{WORK}/*/wt/**"],
        shell_deny=DESTRUCTIVE + INTEGRATE + NO_COMMIT_NO_BUILD,
    ),
    "developer": dict(
        write_allow=[f"{WORK}/*/wt/**"] + T("notes/dev-*.md", "notes/signals/**"),
        write_deny=T("*.md") + [f"{WORK}/*/*.md", f"{PROJECTS}/**"],
        shell_deny=DESTRUCTIVE + INTEGRATE + ["git checkout*", "git -C * checkout*", "git switch*", "git -C * switch*"],
    ),
    "gate": dict(
        write_allow=T("review.md", "trace.md", "notes/gate-*.md", "notes/rework-*.md", "notes/trace.md", "notes/signals/**"),
        write_deny=T("overview.md", "test-design.md", "architecture.md") + [f"{PROJECTS}/**", f"{WORK}/*/wt/**"],
        shell_deny=DESTRUCTIVE + INTEGRATE + NO_COMMIT_NO_BUILD,
    ),
    "reviewer": dict(
        write_allow=T("review.md", "notes/rv-*.md", "notes/signals/**"),
        write_deny=T("overview.md", "test-design.md", "architecture.md") + [f"{PROJECTS}/**", f"{WORK}/*/wt/**"],
        shell_deny=DESTRUCTIVE + INTEGRATE + ["git commit*", "git -C * commit*", "git checkout*", "git switch*",
                                              "git reset*", "git -C * reset*", "git stash*", "git cherry-pick*",
                                              "git revert*"],
    ),
}
WORKERS = {"planner", "test-designer", "architect", "developer", "reviewer", "gate"}


def path_glob(pattern):
    """Kiro-style glob: ** spans folders, * stays inside one folder."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + r"\Z")


def path_hits(path, patterns):
    return any(path_glob(p).match(path) for p in patterns)


ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$")


def segments(command):
    """Each simple command in a compound line, with leading VAR=x and wrappers removed."""
    for part in re.split(r"&&|\|\||;|\||\n|\$\(|`", command):
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        while words and (ENV_ASSIGN.match(words[0]) or words[0] in ("env", "command", "exec", "nohup", "time")):
            words.pop(0)
        if words:
            yield " ".join(words)
            # look inside zsh -ic '...' / bash -c '...'
            if len(words) >= 3 and words[0] in ("zsh", "bash", "sh") and words[1].startswith("-") and "c" in words[1]:
                yield from segments(words[2])


def cmd_hits(command, patterns):
    for seg in segments(command):
        for p in patterns:
            if fnmatch.fnmatchcase(seg, p) or fnmatch.fnmatchcase(seg, p.rstrip("*")):
                return seg, p
    return None


def decide(kind, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": kind,
                                              "permissionDecisionReason": reason}}))
    sys.exit(0)


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def main():
    data = json.load(sys.stdin)
    role = sys.argv[1] if len(sys.argv) > 1 else (data.get("agent_type") or "")
    role = role.split(":")[-1]  # plugin-scoped names look like plugin:role
    rules = ROLES.get(role)
    if not rules:
        sys.exit(0)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}

    if tool == "Bash":
        command = inp.get("command", "")
        hit = cmd_hits(command, rules.get("shell_deny", []))
        if hit:
            block(f"agent-guard: role '{role}' may not run `{hit[0]}` (rule `{hit[1]}`). "
                  "Record it under Questions for the owner (team-workflow, 'Rework and routing').")
        hit = cmd_hits(command, rules.get("shell_ask", []))
        if hit:
            decide("ask", f"agent-guard: '{role}' wants to run `{hit[0]}`. Approve only after you said `push T<n>`.")
        sys.exit(0)

    path = inp.get("file_path") or inp.get("notebook_path")
    if not path:
        sys.exit(0)
    path = os.path.realpath(os.path.join(data.get("cwd") or os.getcwd(), os.path.expanduser(path)))
    if path_hits(path, rules.get("write_deny", [])):
        block(f"agent-guard: role '{role}' may not write {path}. Nobody edits another role's file; "
              "record the change under Questions with its owner.")
    if path_hits(path, rules.get("write_allow", [])):
        sys.exit(0)
    if role in WORKERS:
        decide("ask", f"agent-guard: {path} is outside what role '{role}' normally writes.")
    sys.exit(0)


if __name__ == "__main__":
    main()
