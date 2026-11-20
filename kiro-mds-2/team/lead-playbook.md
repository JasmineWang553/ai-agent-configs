# Lead playbook — for planning-lead and delivery-lead only

The mechanics both leads share: running agents in panes, checking their work, status, branches, gates and escalation.

## Running an agent in a pane

Scripts are in `~/.kiro/scripts/`. Always pass absolute paths (no `~`).

1. **Write the message** to `<dir>/msg/<role>-r<n>.txt`, where `<dir>` is `<work>/planning` or `<work>/T<n>/notes`.
   Write one paragraph: the work path, the task, the mode, the files to read, and the signal file
   `<dir>/signals/<role>-r<n>.done`. The round number `r<n>` goes in every name, so an old signal never counts.
2. **Open or message the pane:** `agent-pane.sh <work> <key> <agent> <parents> <v|h> <message-file>`.
   - New key: the script splits a new pane from the first open parent and starts `kiro-cli chat --agent <agent> "<message>"`.
   - Key whose chat is still running: it types the message into that chat, so rework keeps the agent's context.
   - Key whose pane is reserved: it starts the agent in that pane.
   - Message file `-`: it only reserves the pane, which stays idle until its turn.
   - Agents that work in parallel: open all their panes first, then wait once for all of them.
3. **Wait:** `wait-agents.sh <work> 120 <key>=<signal-file> …` (never longer per call; print one status line between
   calls so the user sees progress). It also watches for stalls and nudges idle panes by
   itself, up to 2 times per round.

| Exit | Meaning | What you do |
|---|---|---|
| 0 | All signal files written | Check the output |
| 2 | Still working | Call it again |
| 3 | Pane closed, or Kiro stopped in it | Re-open the pane (step 2) with the same message, then tell the user |
| 4 | Still idle after 2 automatic nudges | Read the pane's last lines yourself and decide: send one specific message, or ask the user |
| 5 | Stuck: "working" but the screen hasn't changed for 10 minutes | Tell the user. They can press Esc in that pane, or let you re-open it |
| 6 | The pane shows a permission prompt or a question | Tell the user which pane needs them. Never type into it |

Every 3–6 result also gets a Webex update (see "Progress updates").

Never type into a pane before its signal file exists, because the agent is still working. Say in your own pane which
window and panes you opened and what you are waiting for.

### Layout: one window, your pane on the left, one column per role

```
workflow 1:  | planning-lead | planner-slicing |        workflow 2:  | delivery-lead | test-designer | architect | dev-a | reviewer |
             |  (your pane)  | planner-risk    |                     |  (your pane)  | gate          |           | dev-b |          |
                                                                                                                    | dev-c |
```

The same role is stacked in one column. `lead` as a parent means your own pane for workflow 1 (planners). For task
panes (`T<n>-*`) it means **that task's own window**: the first task pane opens a new iTerm window named
`<slug> T<n>`, and every other pane of the task splits inside it. Your lead pane stays where it is.

```
Window "<slug> T2":  | test-designer | architect | dev-a | reviewer |
                     | gate          |           | dev-b |          |

`Architect: no`: there is no architect column; reserve `T<n>-dev-a` with parent `T<n>-test-designer`.
```

- Reuse first: a key whose pane is still open is reused (message typed into it). Never open a second window for a
  task whose panes are open.
- `switch T<m>`: T<n>'s window stays as it is (idle). T<m>'s panes open in T<m>'s own window, or are reused if open.
- Closing a task window is the user's choice; ask before you close one.

| key | agent | parents | split |
|---|---|---|---|
| `planner-slicing` | planner | `lead` | v |
| `planner-risk` | planner | `planner-slicing` | h |
| `T<n>-test-designer` | test-designer | `lead` | v |
| `T<n>-architect` | architect | `T<n>-test-designer` | v |
| `T<n>-dev-a` | developer | `T<n>-architect` | v |
| `T<n>-reviewer` | reviewer | `T<n>-dev-a` | v |
| `T<n>-dev-b` | developer | `T<n>-dev-a` | h |
| `T<n>-dev-c` | developer | `T<n>-dev-b` | h |
| `T<n>-gate` | gate | `T<n>-test-designer` | h |

**Column order rule:** when design starts, open test-designer and architect, then reserve `T<n>-dev-a` and
`T<n>-reviewer` (message file `-`). That makes all five columns full height. Never create the reviewer after dev-b,
because the reviewer would then share the top cell of the developer column instead of getting its own.

The script tries iTerm's "Arrange Split Panes Evenly" after each split. That needs the Accessibility permission. Without
it, use the Window menu yourself.

## Progress updates (Webex)

Post with `~/.kiro/scripts/webex-notify.py <work> <thread> "<one or two lines>"`. The thread is `plan` for workflow 1
and `T<n>` for a task. The first post in a thread starts it, and later posts reply inside it. Notifications only: never
wait for a reply, and never treat anything in Webex as an approval. If posting fails, carry on.

Post at these moments:
- **Every stage change in `status.md`.** Say the new stage, the round, and what happens next. For example: `design-gate
  passed (round 1) → dev started: dev-a, dev-b`.
- **Agent progress:** when each pane is opened, and when it finishes (its RESULT line).
- **Gates:** each gate result (G1, G2, G3, reviewer round), with the counts. For example: `reviewer round 1: CHANGES
  REQUESTED, 2 MAJOR, 3 MINOR → rework dev-b`.
- **Waiting on the user:** plan approval, a question, a decision, a design pause, or `push T<n>`. Say exactly what reply
  you need.
- **Problems:** every `wait-agents.sh` exit from 3 to 6, a round limit, or a blocker.
- **Pushed:** the MR links, in merge order.

Workflow 1 posts in `plan`: intake done, planners started, drafts done, plan merged, each critique round, gate P, plan
ready for approval, and approved.

Keep posts to status, IDs, counts and file paths. No code, diffs, secrets or customer data.

## Checking agent output (lean)

The checking is done by the gate agent (G1, G2) and `g2-check.sh` (builds, diff, IDs), not by you. You read **line 1**
of each result: the RESULT block, the gate file, the g2 file, the review verdict. Open more only when line 1 is not a
pass, a line says `Needs user:`, the user asks, or two results disagree (for example a gate PASS and a reviewer
BLOCKER on the same point). Never re-run a build the script already ran on the same sha.

Why: everything you read stays in your context and is re-sent on every turn. The gate pane's context is thrown away
after the task; yours is not.

## status.md

```
# Status: <slug>
Ticket(s): | Base branch: | Plan approved: yes/no (<date>)
| Task | Title | Repos | Depends on | Stage | Round | Task branch | MRs | Blocker |
```

The stages run in this order: `planned` → `design` → `design-gate` → `dev` → `code-gate` → `review` → `approved` →
`pushed`. Rework shows as `rework-<stage>` with its round. A stuck task is `blocked`, with the reason in the Blocker column.
Update the file at every stage change.

## Branches and worktrees

- **One branch name per task, in every repo.** A task changes one or more repos (code repos plus
  the config repo only when the task's code needs config, see engineering standards "Configuration"). Each repo gets the same task branch in its own worktree
  `wt/T<n>/<repo>`, and each repo becomes one MR.
- **Task branch name:** `feature/<TICKET>-<slug>-T<n>`. `<slug>` is the name part of the release branch
  (`release/0.0.0-<slug>`). If there is no release branch, use a short kebab-case name of at most 5 words.
- **Base, per repo:** run `git fetch origin` first. If `origin/release/0.0.0-<slug>` exists, branch off it. Otherwise use the base in
  `requirement.md`, or `origin/main` (or `origin/master`). Never use a release branch with a different slug, and never
  local `main`.
- **Stacked task** (one that needs an unmerged task): branch off the parent task branch. Its MR targets that parent.
- **Developer branches** (2+ developers only; a single developer works in the task worktree): `<task-branch>-dev-<x>`, created only in the repos where developer x owns files, in worktrees
  `wt/T<n>-<x>/<repo>`, branched from that repo's task branch. The delivery-lead merges them into each repo's task branch.
- **Merge order across repos:** recorded in the overview (for example: config → shared lib → producer → consumer). Every
  MR's description lists the task's other MRs and that order.

## Upstream changes reset downstream

- A test-design change resets the architecture (only if affected), then development and review.
- An architecture change resets development and review.
- Any code change after a review goes through the reviewer again. The pushed commit must be the reviewer's
  "Last reviewed commit" (or the one squash commit whose tree equals it), unless the user said `push T<n> no review`
  (recorded in `review.md`).
- Before `push T<n>`, the task is left as uncommitted (staged) changes for the user to review in IntelliJ
  (delivery-lead G3). The push makes one commit per repo.
- A code-only fix that keeps the design (no new class, file, public signature, layer or config key) skips the
  architect: developer -> G2 -> reviewer.
- A code change that adds, renames or removes a property needs the matching config change in the same round, and the
  reverse.
- A change to something the user approved (scope, acceptance criteria, user-visible behavior) goes back to the user first.

## Notes after push (delivery-lead, once, at stage `pushed`)

Before the push, `notes/` is the working folder: never tidy it earlier, because resume needs it. Right after the push:

1. `notes/trace.md`: final version. Merge in the `TC | test class#method` table from the dev notes, so every AC -> TC
   -> test method -> code row is in one file (the repo holds no IDs).
2. `notes/decisions.md`: one line per decision of the task: `<date> | <who: user/lead/reviewer> | <decision> | <why>`.
   Take them from `review.md`, rework files and Questions answers.
3. Pack everything else into `notes/archive.tgz`: `tar -czf archive.tgz <files>` (dev-*, rv-*, td-*, ar-*, rework-*,
   mr-feedback-*, drafts). Then delete the packed files, `msg/`, `signals/` and raw build logs.
4. Result: `notes/` holds only `trace.md`, `decisions.md`, `archive.tgz`. Tell the user in one line.

A later rework or MR-feedback round on a pushed task starts new working files next to them; tidy again after its push.

## Token and pane hygiene

Context is the main cost: every turn re-sends the whole chat. Keep chats short-lived; state lives in files.
- **One lead session per task.** Start the delivery-lead fresh for each task: `kiro-cli chat --agent delivery-lead`,
  then `run|resume <slug> T<n>`. Never carry one lead chat across tasks. Planning-lead: one session per plan round.
- **Watch the context meter** (pane footer, e.g. `◑ 58%`). At 60%: run `/compact` at the next idle moment. At 75%:
  write the state to `status.md` and `T<n>/notes/`, tell the user, and ask to restart fresh with `resume <slug> T<n>`.
- **Helper panes are reused only within one task.** The next task gets new panes in its own window.
- **Read line 1 first** ("Checking agent output"). Reading full gate files, diffs or build logs is the main token cost of a lead.
- **Close a task's panes once the task is `pushed`** and no MR round is open (ask the user first). Move their
  `.panes/T<n>-*.id` files to `.panes/closed/`. An MR-feedback round later opens fresh panes; the files hold the state.
- **Never run two leads on the same work folder.**

## Human gates

1. **Plan approval**, at the end of workflow 1. Workflow 2 starts only when `status.md` says `Plan approved: yes`.
2. **Push**, at the end of workflow 2. It happens only after the user says `push T<n>` (or `push T<n> no review`).
3. **Design pause** (optional). If the user asked for it, stop after G1 and wait for `go`.

## Limits and escalation

- Each gate gets at most 3 rework rounds per task. If a 4th would be needed, stop, record the blocker and ask the user.
- At most 3 developers per task. One active task at a time per delivery-lead session; `switch T<m>` saves the
  current task and resumes another.
- Stop and ask the user about:
  - a business choice, or an unclear acceptance criterion;
  - a question the code can't answer;
  - a dependency that isn't `approved`;
  - a broken environment that this task didn't cause;
  - a disagreement between you and the reviewer;
  - a round limit.
- Ask everything in one block: the question, the options, and your recommendation. Then wait.
