---
name: "write-agents-md"
description: "Create, edit, or audit AGENTS.md (or CLAUDE.md) files so they stay short, agent-facing, and followed. Use when creating an AGENTS.md for a repo or subdirectory, adding or changing a rule in one, or reviewing one for bloat, duplication, stale lines, or ignored instructions."
compatibility: opencode
---

# Write AGENTS.md

AGENTS.md is loaded into every session and competes for the agent's limited
instruction budget. The harness tells the agent the file "may or may not be
relevant": every line that is not universally applicable raises the odds the
whole file is ignored. Write for the agent, not a human reader. Every line
must change behaviour versus the agent's default; otherwise delete it.

## Modes

Pick the one that matches the request, run its steps, then the checker.

**Create** (no file exists for this scope)
1. Inventory the environment: build/test/lint commands, layout, config
   files, existing instruction files (`CLAUDE.md`, `.cursor/rules`, CI).
2. Ask the user only what the environment cannot answer: forbidden
   actions, approval boundaries, unwritten conventions, known gotchas.
3. Draft from the [template](references/rules.md#template). Root file
   under 60 lines where possible, hard cap 150; area files under 80.
4. Verify every command runs and every path exists. Fabrication is the
   worst failure: an agent trusts the file over its own discovery.

**Add or edit a rule**
1. Read the whole file first. Find the section the rule belongs in; an
   existing rule may already cover it or conflict.
2. Apply the [rule test](#rule-test). If the rule only applies to one
   area or task, it belongs in that area's AGENTS.md or a pointed-to doc,
   not the root.
3. Write it in the file's existing voice and format. One bullet; bold
   lead phrase; imperative; the *why* only if it is non-obvious.

**Audit**
1. Read the file and every file it points to.
2. Mark each line that fails the [rule test](#rule-test), plus any that
   is stale (path, command, or behaviour no longer exists).
3. Propose cuts and moves as a diff. Deleting a line is a change the
   human approves; do not silently drop rules.

## Rule test

Keep a line in the root file only if all four hold:

- **Universal**: applies to most sessions in this repo, not one task.
- **Behaviour-changing**: the agent would do otherwise without it.
- **Not discoverable**: not in `--help`, a config file, or the layout.
  Cache only what is expensive to find: conventions, reasons, gotchas.
- **Single source**: not already stated here or in a pointed-to file.

Fails any one → move it to an area file, a referenced doc, a linter, or
drop it.

## Writing rules

- **Positive, imperative wording.** "Run `make generate` after editing
  source" beats "don't forget to regenerate". Prohibitions only for hard
  guardrails, paired with what to do instead.
- **Commands with flags, paths exact.** `pytest -x tests/unit`, not "run
  the tests".
- **Three-tier boundaries** where destructive actions exist: always /
  ask first / never. Name the exact verbs or flags.
- **Pointers, not copies.** Name the file and the trigger: "Working in
  `api/`: load `api/AGENTS.md` first." opencode does not auto-follow
  `@file`; the sentence must be an instruction to read it.
- **Lead with the trigger word** the agent will encounter (`git-crypt`,
  `worktree`, `migrations`) so scanning finds it.
- **No linting by prose.** Style rules go to a formatter or linter; cite
  the command.
- **No narrative.** No history ("we used to…", "migrated from…"), no
  architecture tours, no explaining how a script works internally when
  the script shows it. A *why* stays only if it stops a mistake.
- **No section banners, no persona, no praise, no hedging** ("please",
  "try to", "should ideally").
- **Nested files for monorepos.** Nearest AGENTS.md wins; the root holds
  the map and repo-wide rules, area files hold the rest.

## Check

```
python3 scripts/check_agents_md.py path/to/AGENTS.md            # human output
python3 scripts/check_agents_md.py path/to/AGENTS.md --output json
```

Errors: over line cap, dead markdown links, section banners, hedging
words, duplicate bullets, `@file` references without a read instruction.
Warnings: unresolvable backtick paths, bullets over 3 lines, prose
paragraphs over 4 lines, history phrases, clusters of mutating commands
(a runbook the agent is forbidden to run). Fix or justify every finding
before presenting the file.

See [references/rules.md](references/rules.md) for the template, good/bad
examples, and rationale; [references/sources.md](references/sources.md)
for the research this distils.
