# kiro-mds-2: lean Kiro team setup

Same workflow and the same quality gates as `../kiro/`, with less expensive work. The Opus delivery lead stops checking
details itself: a Sonnet gate agent runs G1 and G2, and a script runs builds and mechanical checks.

```
                      kiro/ (current)                            kiro-mds-2/ (lean)
lead (Opus)           reads code, diffs, builds                  reads line 1 of each result only
test-designer         Opus                                       Sonnet
architect             Opus, every task                           Opus, only when overview says Architect: yes
G1 design gate        lead opens every path:line                 gate agent (Sonnet) -> PASS/FAIL file
developers            Sonnet, strict TDD                         unchanged
G2 code gate          lead runs build, reads output              g2-check.sh (0 tokens) + gate agent (Sonnet)
reviewer              Opus, 11 aspects                           unchanged (reuses g2-check numbers)
G3                    lead re-reads the full diff                lead checks first lines; you read the diff in IntelliJ
push                  you say push T<n>                          unchanged
standards             one 17.6 KB file in every agent            5 role slices, each agent loads only its parts
```

## Install

Copy over your `~/.kiro/` (back it up first):

```bash
cp -R ~/.kiro ~/.kiro.bak
cd kiro-mds-2
cp -R agents team hooks skills ~/.kiro/
mkdir -p ~/.kiro/steering/team/standards ~/.kiro/scripts
cp steering/*.md ~/.kiro/steering/
cp steering/team/workflow.md ~/.kiro/steering/team/
cp steering/team/standards/*.md ~/.kiro/steering/team/standards/
cp scripts/g2-check.sh ~/.kiro/scripts/ && chmod +x ~/.kiro/scripts/g2-check.sh
# the old single file and the symlinks must go, or agents load them again via the old globs:
rm ~/.kiro/steering/team/engineering-standards.md ~/.kiro/steering/team/maven-charter-cert.md ~/.kiro/steering/team/project-sync.md
```

Your existing scripts (`agent-pane.sh`, `wait-agents.sh`, `webex-notify.py`, `safe-delete.py`, `git-hooks/commit-msg`)
are still used and are not in this folder; keep them in `~/.kiro/scripts/`.

## What changed, file by file

| File | Change |
|---|---|
| `agents/gate.json`, `gate-prompt.md` | **New** Sonnet agent. G1 and the judgment part of G2. Writes the gate section of `review.md`, `notes/trace.md`, rework items, and `notes/gate-G<1|2>-r<n>.md` whose first 3 lines are `GATE … PASS|FAIL`, `Rework: …`, `Needs user: …` |
| `scripts/g2-check.sh` | **New.** G2.1 full build and tests per repo in merge order (with the Charter trust store), G2.4 files not named in the design, G2.8 internal IDs in added lines and commit messages. Writes `notes/g2-r<n>.md` (line 1 `G2-SCRIPT: PASS|FAIL`) |
| `agents/delivery-lead-prompt.md` | Rewritten gates: routes on first lines, no code reading, no own builds, G3 without a full-diff read |
| `agents/test-designer.json` | Model → `claude-sonnet-5.5` |
| `team/templates/overview.md` | New field `Architect: yes/no — reason` |
| `agents/planning-lead-prompt.md` | Gate check **P11**: sets `Architect`. `no` only if S, one repo, one developer, and no new class, public signature, config key, contract, DB query or external call. When unsure: `yes` |
| `agents/architect-prompt.md`, `developer-prompt.md`, `test-designer-prompt.md`, `reviewer-prompt.md` | Handle `Architect: no` (the overview's touch points and patterns are the design; the reviewer flags any new class or contract as MAJOR). The reviewer writes one `### Follow-ups` list for the lead |
| `steering/team/standards/es-*.md` | `engineering-standards.md` split into core, code, config, release, tests. The text is unchanged |
| `agents/*.json` resources | Explicit slices per role instead of `steering/team/**`. `maven-charter-cert.md` and `project-sync.md` are read on demand |
| `team/lead-playbook.md` | Gate pane (`T<n>-gate`, under the test-designer), "read line 1" rule, layout without an architect |
| `steering/team/workflow.md` | Roles table (gate, Sonnet test designer, optional architect), "Reading results" rule |

## Fixed prompt per agent (measured: resources + prompt, before any work)

| Agent | kiro/ | kiro-mds-2/ |
|---|---|---|
| `planning-lead` | 48 KB | 36 KB |
| `planner` | 34 KB | 20 KB |
| `delivery-lead` | 57 KB | 40 KB |
| `test-designer` | 34 KB | 25 KB (and Sonnet) |
| `architect` | 36 KB | 27 KB (skipped on small tasks) |
| `developer` | 35 KB | 34 KB |
| `reviewer` | 38 KB | 37 KB |
| `gate` | — | 37 KB (Sonnet) |

The bigger saving is not in this table. It is what the delivery lead no longer reads (code, diffs, build logs), because
that stays in the lead's context and is re-sent on every turn for the rest of the task. Measure one real task on each
version before you decide.

## Not tested

- `g2-check.sh` was tested on throwaway git repos (config-repo path, unnamed-file list, ID detection). The Maven path
  (JDK pick, trust store, `clean install`, the `Tests run:` line) has not been run against a real DTC repo. Run it once by
  hand on a finished task and compare with your own `mvn` output.
- The full lean flow has not been run end to end in Kiro.

## If quality drops

- Test cases miss edge cases often (G1 or the reviewer catch them): set `test-designer.json` back to `claude-opus-5.5`.
- Small tasks without an architect come back with design findings: make P11 stricter, or always `Architect: yes`.
- Gate PASSes that the reviewer then fails on the same point: put the gate on Opus for that check, or let the lead
  open the gate file on every PASS.
