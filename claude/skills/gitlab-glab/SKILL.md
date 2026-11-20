---
name: gitlab-glab
description: Use glab and git against the Charter GitLab (gitlab.spectrumflow.net). Use when the user says "pull latest", "pull the code", "update the repo", "clone", "MR", "merge request", "pipeline", "CI status", "issue", "glab", or any GitLab task.
---

# GitLab with glab

## Token and host
- The token is in `~/.zshrc` as `GITLAB_TOKEN`. The host is `gitlab.spectrumflow.net`.
- Run every `glab` command through `zsh -ic '...'` so the token loads.
- Never print the token. Never write it to another file.
- Check login: `zsh -ic 'glab auth status'`. Expect "Logged in ... (GITLAB_TOKEN)".
- On a 401, tell the user the token is expired. The user puts a new token in `~/.zshrc`.
- Git uses ssh. glab API calls use https.

## Where the code is
- Projects: `~/Desktop/projects/<name>`. Group: `effie-dev` (example: `effie-dev/dtc-recon-service`).
- Match the repo name the user says to a folder in `~/Desktop/projects`. If two match, ask.

## Pull latest
1. `git -C <repo> status -sb`. Show the branch and any local changes.
2. If there are local changes, do not discard them. Use `git pull --ff-only`. If it fails, tell the user. Offer `git stash` only if the user agrees.
3. `git -C <repo> pull --ff-only`.
4. For many repos: run the same steps in each folder. Report one line per repo: branch, up to date or updated, dirty or clean.
5. Never use `git reset --hard`, `git clean`, `git checkout .` or `--force` unless the user asks.

## Common commands
Run inside the repo folder.

| Task | Command |
|------|---------|
| My open MRs | `glab mr list --author=@me` |
| MRs to review | `glab mr list --reviewer=@me` |
| View an MR | `glab mr view <id>` |
| MR diff | `glab mr diff <id>` |
| MR comments | `glab mr view <id> --comments` |
| Create an MR | `glab mr create --fill --target-branch main` |
| Pipeline status | `glab ci status` |
| Pipeline list | `glab ci list` |
| Failed job log | `glab ci trace <job>` |
| Issue list | `glab issue list` |
| Clone | `glab repo clone effie-dev/<name> ~/Desktop/projects/<name>` |
| Any API call | `glab api projects/:id/...` |

## Safety rules
- Read commands: run them.
- Never push to `main` or `master`, merge an MR, close an MR, or delete a branch unless the user asks for that exact action.
- Before `glab mr create` or `git push`: show the branch and the title. Wait for yes.
- Never commit unless the user asks.
- Check before you commit that no `.env`, token or key file is staged.

## Report
- Short. One line per repo or MR.
- Say what was not checked.
