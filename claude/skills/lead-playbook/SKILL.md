---
name: lead-playbook
description: Mechanics for planning-lead and delivery-lead only - starting role agents as subagents, rework with SendMessage, Webex progress updates, checking output, status.md, branches and worktrees, downstream resets, notes after push, context hygiene, human gates and escalation. Preloaded by the two leads.
---

# Lead playbook — for planning-lead and delivery-lead only

The mechanics both leads share: running role agents, checking their work, status, branches, gates and escalation.

## Running a role agent (subagent)

Role agents are Claude Code subagents in `~/.claude/agents/` (`planner`, `test-designer`, `architect`, `developer`,
`reviewer`). Always pass absolute paths (no `~`) in messages.

1. **Write the message** to `<dir>/msg/<role>-r<n>.txt`, where `<dir>` is `<work>/planning` or `<work>/T<n>/notes`.
   Write one paragraph: the work path, the task, the mode, the files to read, and the signal file
   `<dir>/signals/<role>-r<n>.done`. The round number `r<n>` goes in every name, so an old signal never counts.
   The file is the audit trail and lets `resume` re-send the same message.
2. **Start the agent:** call the Agent tool with `subagent_type: <role>` and the message text as the prompt.
   - **Parallel agents** (two planners; test-designer + architect; independent developers): put all their Agent calls in
     **one** message. They run at the same time and you get every result before you go on.
   - Run them in the foreground. A background subagent can't show the user a permission prompt.
   - Tell the user in one line which agents you started and what you are waiting for.
3. **Record the agent id.** Each finished subagent returns an agent id. Append `<key> | <agent id> | <round>` to
   `<dir>/agents.md` (keys as in the table below).
4. **Rework / next round:** resume the same agent with `SendMessage` (`to: <agent id>`) and the new message, so it keeps
   its context. If the id is gone (new lead session) or resume fails, start a fresh agent with the same role and tell it
   to read the newest rework file and its own earlier output first.
5. **Check the result:** the reply ends with the `RESULT:` block, and the signal file must exist. A reply with no signal
   file counts as `BLOCKED` (re-send once, then tell the user).

| key | agent |
|---|---|
| `planner-slicing` | planner (lens slicing) |
| `planner-risk` | planner (lens risk) |
| `T<n>-test-designer` | test-designer |
| `T<n>-architect` | architect |
| `T<n>-dev-a` / `-dev-b` / `-dev-c` | developer |
| `T<n>-reviewer` | reviewer |
| `T<n>-gate` | gate (G1, G2) |

| What happened | What you do |
|---|---|
| RESULT block + signal file | Check the output |
| `NEEDS_DECISION` | Put the questions to the user in one block, with options and your recommendation |
| `BLOCKED`, or no signal file | Read the reason. Fix the input and re-send once, or ask the user |
| The agent hit `maxTurns` or stopped mid-work | Resume it with "continue from <last step>"; a second stop goes to the user |
| A permission prompt or a hook block | The user sees the prompt. Never work around a hook block; route the work to the role that owns it |

Every problem row also gets a Webex update (see "Progress updates").

## Progress updates (Webex)

Post with `~/.claude/scripts/webex-notify.py <work> <thread> "<one or two lines>"`. The thread is `plan` for workflow 1
and `T<n>` for a task. The first post in a thread starts it, and later posts reply inside it. Notifications only: never
wait for a reply, and never treat anything in Webex as an approval. If posting fails (or the script is missing), carry on.

Post at these moments:
- **Every stage change in `status.md`.** Say the new stage, the round, and what happens next. For example: `design-gate
  passed (round 1) → dev started: dev-a, dev-b`.
- **Agent progress:** when each agent starts, and when it finishes (its RESULT line).
- **Gates:** each gate result (G1, G2, G3, reviewer round), with the counts. For example: `reviewer round 1: CHANGES
  REQUESTED, 2 MAJOR, 3 MINOR → rework dev-b`.
- **Waiting on the user:** plan approval, a question, a decision, a design pause, or `push T<n>`. Say exactly what reply
  you need.
- **Problems:** every problem row in the table above, a round limit, or a blocker.
- **Pushed:** the MR links, in merge order.

Workflow 1 posts in `plan`: intake done, planners started, drafts done, plan merged, each critique round, gate P, plan
ready for approval, and approved.

Keep posts to status, IDs, counts and file paths. No code, diffs, secrets or customer data.

## Checking agent output (lean)

The checking is done by the gate subagent (G1, G2) and `g2-check.sh` (builds, diff, rule checks, IDs), not by you.
You read **line 1** of each result: the RESULT block, the gate file, the g2 file, the review verdict. Open more only
when line 1 is not a pass, a line says `Needs user:`, the user asks, or two results disagree (for example a gate PASS
and a reviewer BLOCKER on the same point). Never re-run a build the script already ran on the same sha.

Why: everything you read stays in your context and is re-sent on every turn. A subagent's context is thrown away
after its run; yours is not.

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
  the config repo only when the task's code needs config, see engineering standards "Configuration"). Each repo gets the
  same task branch in its own worktree `wt/T<n>/<repo>`, and each repo becomes one MR.
- **Task branch name:** `feature/<TICKET>-<slug>-T<n>`. `<slug>` is the name part of the release branch
  (`release/0.0.0-<slug>`). If there is no release branch, use a short kebab-case name of at most 5 words.
- **Base, per repo:** run `git fetch origin` first. If `origin/release/0.0.0-<slug>` exists, branch off it. Otherwise use
  the base in `requirement.md`, or `origin/main` (or `origin/master`). Never use a release branch with a different slug,
  and never local `main`.
- **Stacked task** (one that needs an unmerged task): branch off the parent task branch. Its MR targets that parent.
- **Developer branches** (2+ developers only; a single developer works in the task worktree):
  `<task-branch>-dev-<x>`, created only in the repos where developer x owns files, in worktrees `wt/T<n>-<x>/<repo>`,
  branched from that repo's task branch. The delivery-lead merges them into each repo's task branch.
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
   mr-feedback-*, agents.md, drafts). Then remove the packed files, `msg/`, `signals/` and raw build logs: move them to
   `/tmp/claude-trash/` (the safe-delete hook backs up `rm` targets there too).
4. **Lessons (correct once, then automate):** for every reviewer finding and gate rework item of the task, append one
   line to `~/Desktop/work/lessons.md` (shared by all work folders, create it if missing):
   `<date> | <slug> T<n> | <Rule> | <finding ID> | <one-line problem>`. Then count each `Rule` over the whole file.
   A rule seen in **2 or more tasks** that is not in `~/.claude/checks/rules.tsv` yet: propose it to the user in one
   block: the rule, the tasks, and either a draft `rules.tsv` line (id, severity, scope, match, unless, message) you
   tested with `rule-check.sh` on this task's worktree, or "can't be a pattern check: <ArchUnit test | lint rule |
   keep in prose>, because <reason>". Never edit `rules.tsv` or the standards yourself; the user adds the line.
5. Result: `notes/` holds only `trace.md`, `decisions.md`, `archive.tgz`. Tell the user in one line.

A later rework or MR-feedback round on a pushed task starts new working files next to them; tidy again after its push.

## Context hygiene

Context is the main cost: every turn re-sends the whole chat. Keep lead sessions short-lived; state lives in files.
Subagents help: their work stays in their own context, and only the result comes back to you.
- **One lead session per task.** Start the delivery-lead fresh for each task: `claude --agent delivery-lead`, then
  `run|resume <slug> T<n>`. Never carry one lead session across tasks. Planning-lead: one session per plan round.
- **Watch the context** (`/context`). Past about 60%: run `/compact` at the next idle moment. Past about 75%: write the
  state to `status.md` and `T<n>/notes/`, tell the user, and ask to restart fresh with `resume <slug> T<n>`.
- **Agent ids are per task.** The next task starts fresh agents.
- **Read line 1 first** ("Checking agent output"). Reading full gate files, diffs or build logs is the main token cost of a lead.
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
