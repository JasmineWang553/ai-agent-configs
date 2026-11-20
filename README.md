# ai-agent-configs

Agent setups for the DTC Java/Spring Boot delivery workflow: planning council, then a gated design → TDD dev →
review → push flow per task.

| Folder | What | Install to |
|---|---|---|
| `kiro/` | Original Kiro config: agents, steering, hooks, skills, team playbook and templates | `~/.kiro/` |
| `claude/` | Claude Code port with **subagents**. The leads run as `claude --agent <lead>` and start role agents inside their own session. Stable, recommended | `~/.claude/` |
| `claude-team/` | Claude Code port with **agent teams** (experimental). Each role agent is a teammate in its own iTerm pane, and teammates can message each other | `~/.claude/` |

Install either `claude/` or `claude-team/`, not both: they use the same paths. Each folder's README has the
install steps and the Kiro → Claude mapping.

Not in this repo: `webex-notify.py` and the Kiro pane scripts (`agent-pane.sh`, `wait-agents.sh`, `safe-delete.py`).
The Claude versions don't need the pane scripts and ship their own `safe-delete.py`.
