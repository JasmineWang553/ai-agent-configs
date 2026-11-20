#!/usr/bin/env python3
"""Safe delete (port of the Kiro `safe-delete` hook) as a Claude Code PreToolUse hook on Bash.

- Copies rm / mv source targets to /tmp/claude-trash/<timestamp>/ before the command runs.
- Blocks: git reset --hard, git clean -f, force push, rm of / or $HOME (or their direct children via wildcard).
"""
import glob
import json
import os
import re
import shlex
import shutil
import sys
import time

TRASH = "/tmp/claude-trash"
HOME = os.path.realpath(os.path.expanduser("~"))

BLOCK = [
    (re.compile(r"\bgit\b(\s+-C\s+\S+)?\s+reset\s+.*--hard\b|\bgit\b(\s+-C\s+\S+)?\s+reset\s+--hard\b"), "git reset --hard"),
    (re.compile(r"\bgit\b(\s+-C\s+\S+)?\s+clean\b.*\s-[a-zA-Z]*f"), "git clean -f"),
    (re.compile(r"\bgit\b(\s+-C\s+\S+)?\s+push\b.*(\s--force(-with-lease)?\b|\s-f\b|\s\+\S+)"), "force push"),
]


def block(reason):
    print(f"safe-delete: blocked {reason}. Ask the user to run it themselves if it is really needed.", file=sys.stderr)
    sys.exit(2)


def parts(command):
    for part in re.split(r"&&|\|\||;|\||\n", command):
        try:
            words = shlex.split(part)
        except ValueError:
            continue
        while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
            words.pop(0)
        if words and words[0] == "sudo":
            words.pop(0)
        if words:
            yield words


def targets(words, cwd):
    """Paths an rm/mv command would remove or move away."""
    args = [w for w in words[1:] if not w.startswith("-")]
    if words[0] == "mv":
        args = args[:-1]  # last arg is the destination
    for a in args:
        a = os.path.expanduser(a)
        a = a if os.path.isabs(a) else os.path.join(cwd, a)
        matches = glob.glob(a) or [a]
        for m in matches:
            yield os.path.realpath(m), a


def main():
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        sys.exit(0)
    command = (data.get("tool_input") or {}).get("command", "")
    cwd = data.get("cwd") or os.getcwd()

    for rx, name in BLOCK:
        if rx.search(command):
            block(name)

    to_backup = []
    for words in parts(command):
        if words[0] not in ("rm", "mv", "unlink", "rmdir"):
            continue
        for real, raw in targets(words, cwd):
            if words[0] != "mv" and (real in ("/", HOME) or os.path.dirname(real) in ("/",) or
                                     (raw.endswith("*") and os.path.dirname(real) in ("/", HOME))):
                block(f"rm of {raw}")
            if os.path.lexists(real):
                to_backup.append(real)

    if to_backup:
        dest_root = os.path.join(TRASH, time.strftime("%Y%m%d-%H%M%S"))
        for src in to_backup:
            dest = dest_root + src
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                if os.path.isdir(src) and not os.path.islink(src):
                    shutil.copytree(src, dest, symlinks=True, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dest, follow_symlinks=False)
            except OSError as e:
                print(f"safe-delete: backup of {src} failed ({e}); not running the command.", file=sys.stderr)
                sys.exit(2)
        print(json.dumps({"systemMessage": f"safe-delete: backed up {len(to_backup)} path(s) to {dest_root}"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
