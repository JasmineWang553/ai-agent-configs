# kiro: original Kiro team setup

The original Kiro CLI config: 7 agents, steering, hooks, skills, the lead playbook and templates. The lean version
of the same workflow is in `../kiro-mds-2/`.

Install: copy the folders over `~/.kiro/` (`agents`, `steering`, `team`, `hooks`, `skills`). The pane scripts
(`agent-pane.sh`, `wait-agents.sh`), `webex-notify.py`, `safe-delete.py` and `git-hooks/commit-msg` are not in this
folder; they live in your `~/.kiro/scripts/`.

## How it runs

### Workflow 1: planning (`kiro-cli chat --agent planning-lead`)

```mermaid
flowchart TB
  U(["You: requirement, ticket, repos"]) --> PL["planning-lead · Opus<br/>intake Q and A, requirement.md"]
  PL --> S["planner-slicing · Opus<br/>own pane"]
  PL --> R["planner-risk · Opus<br/>own pane"]
  S --> M["planning-lead merges drafts<br/>plan.md"]
  R --> M
  M --> C["Critique round<br/>both planners, same panes"]
  C --> P{"Gate P<br/>checks P1-P10"}
  P -- FAIL --> C
  P -- PASS --> A{"You: approve?"}
  A -- changes --> M
  A -- approve --> O["T1..Tn overview.md<br/>status.md: Plan approved"]
```

### Workflow 2: one task (`kiro-cli chat --agent delivery-lead`, then `run <slug> T<n>`)

```mermaid
flowchart TB
  DL["delivery-lead · Opus<br/>worktrees per repo"] --> TD["test-designer · Opus<br/>test-design.md"]
  DL --> AR["architect · Opus<br/>architecture.md"]
  TD --> G1{"G1 design gate<br/>lead checks itself"}
  AR --> G1
  G1 -- FAIL: rework --> TD
  G1 -- FAIL: rework --> AR
  G1 -- PASS --> DEV["developers 1-3 · Sonnet<br/>strict TDD, own worktrees"]
  DEV --> MG["lead merges dev branches"]
  MG --> G2{"G2 code gate<br/>lead runs full build"}
  G2 -- FAIL --> DEV
  G2 -- PASS --> RV["reviewer · Opus<br/>11 aspects, review.md"]
  RV -- CHANGES REQUESTED --> DEV
  RV -- APPROVED --> G3{"G3<br/>lead re-reads full diff"}
  G3 --> IJ["Staged changes<br/>you review in IntelliJ"]
  IJ --> PUSH(["You: push Tn<br/>one commit per repo, MRs"])
```

### How the lead runs an agent (iTerm panes)

```mermaid
sequenceDiagram
  participant L as delivery-lead (your pane)
  participant P as agent-pane.sh
  participant A as role agent (its own pane)
  participant W as wait-agents.sh
  L->>L: write msg/role-rN.txt
  L->>P: key, agent, message file, parent pane, split
  P->>A: open pane, start kiro-cli with the message
  L->>W: wait for signals/role-rN.done
  A->>A: work, narrate in pane
  A->>A: write output file, then signal file (RESULT block)
  W-->>L: exit 0 (or 3-6: closed, stalled, nudged, timeout)
  L->>L: check output, route rework into the same pane
```

Each agent's limits (which files it may write, which shell commands it may run) are in its `agents/<name>.json`
under `permissions.rules`. The `safe-delete` hook backs up deletes and blocks destructive git commands for every agent.
