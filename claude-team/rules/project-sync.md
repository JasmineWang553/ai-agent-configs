# Project Sync (before reading a repo)

All repos live in `~/Desktop/projects/*`.
Before you read or search code in one of them, sync it. Do this once per repo per session.
Load the skill `gitlab-glab` and use `glab` and `git` as it says.

## Steps

```
[repo] -> dirty? --yes--> STOP sync, read as is, tell user
            |no
            v
        on main? --yes--> git pull
            |no
            v
        branch merged? --yes--> git checkout main -> git pull
            |no
            v
        leave branch, read as is (work in progress)
```

1. `git status --porcelain`: if not empty, skip sync. Say "dirty, not synced".
2. `git branch --show-current`: if `main` (or `master`), run `git pull`.
3. Else check merged:
   - `git fetch origin`
   - `git merge-base --is-ancestor HEAD origin/main` (exit 0 = merged), or
   - `glab mr list --source-branch <branch> --merged` returns an MR (covers squash merges).
4. Merged: `git checkout main` then `git pull`.
5. Not merged: do not switch. Read the branch as is.

## Rules

- Never `stash`, `reset`, `clean` or `checkout -- .` to force a sync.
- Never delete the old branch.
- Never sync a repo that has a worktree under `<work>/status.md` for the current task. Use that worktree.
- Pull fails (conflict, auth, network): stop, report the error, read as is.
- Report one line per repo: `repo: branch -> action`.
