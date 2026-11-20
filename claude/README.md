# Claude Code port of the Kiro team setup

Everything in this folder goes into `~/.claude/` (user scope, like `~/.kiro/`).

## Install

```bash
cd claude
mkdir -p ~/.claude
cp -R agents skills rules team hooks scripts ~/.claude/
# Merge, don't overwrite, if you already have these:
cat CLAUDE.md          # append to ~/.claude/CLAUDE.md
cat settings.json      # merge the "hooks" block into ~/.claude/settings.json
chmod +x ~/.claude/hooks/*.py ~/.claude/scripts/git-hooks/commit-msg
```

Copy your own `~/.kiro/scripts/webex-notify.py` to `~/.claude/scripts/` (it was not in the zip). The leads skip the
Webex posts if the script is missing.

## Use

| Kiro | Claude Code |
|---|---|
| `kiro-cli chat --agent planning-lead` | `claude --agent planning-lead`, then give the requirement or `resume <slug>` |
| `kiro-cli chat --agent delivery-lead` | `claude --agent delivery-lead`, then `run <slug> T<n>` / `resume <slug> T<n>` / `push T<n>` |
| `kiro-cli chat --agent developer` (direct) | `claude --agent developer` (direct mode: questions → plan → `go` → code) |

Approval words, gates, the work-folder layout, templates and IDs are unchanged.

## What maps to what

| Kiro | Claude Code (this folder) |
|---|---|
| `agents/<name>.json` + `<name>-prompt.md` | `agents/<name>.md`: frontmatter (`model`, `skills`, `hooks`, `disallowedTools`) + the same prompt |
| `model: claude-opus-5.5` / `claude-sonnet-5.5` | `model: opus` / `sonnet` (developer stays on Sonnet) |
| `resources: ~/.kiro/steering/team/**` + `lead-playbook.md` | skills `team-workflow`, `engineering-standards`, `lead-playbook`, preloaded through `skills:` |
| always-on steering (`ponytail`, `short`, `maven-charter-cert`, `project-sync`) | `rules/*.md`, imported by `CLAUDE.md`. Subagents load CLAUDE.md as well |
| `permissions.rules` (per-agent fs_write / shell allow, deny, ask) | `hooks/agent-guard.py`: same rules, per role (frontmatter hook + global hook keyed on `agent_type`) |
| `hooks/safe-delete.json` → `safe-delete.py` | `hooks/safe-delete.py` (rewritten for Claude's hook format; backups go to `/tmp/claude-trash`) |
| `~/.kiro/scripts/git-hooks/commit-msg` | `scripts/git-hooks/commit-msg` (rewritten from the G2.8 regex) |
| iTerm panes + `agent-pane.sh` + `wait-agents.sh` + signal polling | native subagents: parallel Agent calls in one message, results come back directly, rework with `SendMessage` (the agent keeps its context). Signal files are still written, for `resume` |
| `team/templates/*`, `team/migration-rules.md` | `team/templates/*`, `team/migration-rules.md` (unchanged) |
| other skills | `skills/*`, paths changed to `~/.claude/...`. `iterm-split-agents` now starts `claude` instead of `kiro-cli` |

## Changes you should know about

- **No panes.** You can't type into a worker mid-run. To see what an agent is doing, open its transcript
  (`/tasks` / agent view). Permission prompts from subagents show up in the lead session.
- **Webex `wait-agents` exit codes** (3–6, stalls, nudges) are replaced by the "What happened / What you do" table in the
  `lead-playbook` skill.
- **Context hygiene:** the Kiro context meter is now `/context`. The 60% `/compact` and 75% restart rules are kept.
- **`iterm-split-agents`** no longer answers every prompt with "yes" / "create allow rule" blindly: Claude's menus
  differ, so it reads the options first. Put your old wording back if you want the full-trust behavior.
- **agent-guard limit:** Bash commands are checked by prefix (same as Kiro), so a Bash redirect (`>`), `cp` or `sed -i`
  is not path-checked. Noted in the script as a `shortcut:`.
- **Notes after push:** files are moved to `/tmp/claude-trash` instead of being deleted, because `rm -rf` is denied.

## Optional: agent teams instead of subagents

A ready-made agent-teams version is in `../claude-team/` (see its README). Background:

Agent teams come closest to the Kiro pane setup: each teammate is a full session, can sit in its own iTerm2 split pane,
and you can message it directly. To try them:

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" }, "teammateMode": "auto" }
```

(split panes in iTerm2 need the `it2` CLI and Settings → General → Magic → Enable Python API.)

What you give up (as of the current docs): the feature is experimental; teammates don't get the definition's `skills`
(the agents load them with the Skill tool instead, this is already in each prompt); per-agent frontmatter `hooks` are not
listed as applied to teammates, so only the global `agent-guard` hook (keyed on `agent_type`) protects them, which is
not verified; `/resume` doesn't restore teammates; one team per session; much higher token use. For this gated,
lead-driven workflow, subagents are the recommended default.
