---
name: iterm-split-agents
description: Open a split pane in the current iTerm2 window and run another Claude Code session there (optionally as a named agent), then send it a task and read the answer. Use when the user says "split", "open another agent", "delegate to a second Claude", "new pane" or "run an agent on the right".
---

# iTerm2 split agents

> Team runs (planning-lead / delivery-lead) do NOT use this skill. They spawn role agents as agent-team teammates
> (skill `lead-playbook`). Use this only when the user wants a separate, visible Claude session in its own pane.

## Check first
- Run `echo $TERM_PROGRAM`. It must be `iTerm.app`.
- If not, tell the user and stop. Apple Terminal needs Accessibility permission and cannot split right.

## Pick agent and model
- Agents: `claude agents` (or list `~/.claude/agents/*.md` and `.claude/agents/*.md`).
- Models: aliases `opus`, `sonnet`, `haiku`, or a full model ID (e.g. `claude-opus-5-5`).
- If the name is unclear (for example "sonnet 5" or "sonnet 5.5"), ask.

## Pick the split
- Never use `current session` or session numbers. They change when the user clicks or a pane closes. Find panes by `tty` (your own: walk up `ps -o tty=` from `$$`).
- First pane, on the right: `split vertically` on your own session.
- Next panes, stacked in the right column: `split horizontally` on the last right pane.
- Sessions are numbered by `sessions of current tab`. Read the count after each split.

## Start the agent
- Add `--agent <name>` and `--model <model>` only if the user names them.
- Add `cd <dir> &&` only if the user names a directory. Default: no `cd` (the pane opens in the home root).
- Pass the task as the last quoted argument. Escape inner quotes.
- Do not add `--dangerously-skip-permissions` unless the user asks for it in this chat.

```applescript
tell application "iTerm2"
  tell session N of current tab of current window
    set s to (split horizontally with default profile)
  end tell
  tell s to write text "claude --agent A --model M \"TASK\""
end tell
```

## Read the answer
- Wait with `sleep`, then read all panes:

```applescript
tell application "iTerm2" to tell current window to tell current tab to repeat with s in sessions
  log (name of s) & " | " & (text of s)
end repeat
```

- Use `name of s & " | " & text of s`. A bare `log (text of s)` fails.
- The last pane in the list is the newest.
- Pipe the output through `grep -v '^\s*$' | tail -30`.

## Prompts
- The first start in a folder shows a "trust this folder" screen. Read the options on screen and pick the "yes / trust" one (arrow keys: `write text (ASCII character 27) & "[B" newline no`, then `write text ""` for Enter).
- Permission prompts (Bash, Edit, ...): read the options on screen first. Pick the allow option the user has said is fine. If the user has not said, tell the user which pane waits and stop.
- After each answer, wait and read the pane again. Repeat until the prompt is gone or the agent shows its result.
- Never pick an option you have not read on screen.

## Report
- Show the pane layout and the pane count.
- Give the result of the task.
- Say what was not checked.
