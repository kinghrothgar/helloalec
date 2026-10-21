# AGENTS.md rules: template, examples, rationale

Read when drafting a new file or when a finding needs justification.

## Why these rules

- **Instruction budget.** Frontier models follow roughly 150–200 instructions
  with reasonable consistency; the harness system prompt already spends ~50.
  As the count rises, adherence degrades *uniformly*, not just for the lines
  at the bottom. Every line you add weakens every other line.
- **Relevance gate.** Claude Code and opencode wrap AGENTS.md in a reminder
  that it "may or may not be relevant" and to ignore it unless highly
  relevant. A file full of task-specific detail is judged irrelevant more
  often, and then *all* of it is skipped, including the guardrails.
- **Statelessness.** The agent knows nothing at session start except what is
  in context. AGENTS.md is the only file guaranteed to be there, so it must
  carry the map and the hard rules, and nothing that can be looked up.
- **Negation primes the banned behaviour.** "Don't use `git push --force`"
  puts the command in context. Prefer "Plain `git push` only; `--force` needs
  explicit authorisation" — the prohibition stays but the positive action
  leads.
- **Pointers are instructions.** opencode does not parse `@file` references.
  "See `docs/foo.md`" is decoration; "Load `docs/foo.md` before editing
  `tf/`" is a rule the agent follows.

## Template (root file)

```md
# Repo: <one-line purpose>

<Areas and their AGENTS.md files, one line each. Tell the agent to load
the area file when working there.>

## Repo-wide rules

- **<Trigger phrase>.** <Imperative rule>. <Why, only if non-obvious.>
- ...

## <Domain with destructive actions, e.g. Git operations>

Allowed without asking: <verbs>.
Ask first: <verbs>.
Never: <verbs/flags>.

## Repo map

<Tree, one comment per entry, pointing to area AGENTS.md where they exist.>

## Common tasks

| Intent | Entry point |
|---|---|
| <what the user asks for> | <script or doc> → <area AGENTS.md> |
```

Omit any section that would be empty. Add sections only when the content
passes the rule test.

## Template (area file)

```md
# <area>/

<One line: what lives here and what it generates or controls.>

## Commands

- Build: `<exact command>`
- Test: `<exact command>`
- Lint/format: `<exact command>`

## Rules

- **<Trigger>.** <Rule>.

## Gotchas

- <Non-obvious failure and its fix.>
```

## Good vs bad

| Bad | Good | Why |
|---|---|---|
| "Please try to keep commits small." | "**Small, focused commits.** One logical change per commit." | Imperative, no hedge, bold trigger. |
| "Run the tests before committing." | "`make test` must pass before `git commit`." | Exact command, checkable criterion. |
| "Don't edit generated files." | "**Generated output is committed, never hand-edited.** Edit source in `tk/`, run `make generate`, commit both." | Positive action leads; names the path and command. |
| "See the Terraform docs for conventions." | "**Working in `tf/`:** load `tf/AGENTS.md` first." | Pointer is an instruction with a trigger. |
| "Use 2-space indentation, trailing commas, single quotes…" | "`jsonnetfmt -i` before commit." | Linter's job, one line. |
| "You are an expert DevOps engineer who…" | *(delete)* | Persona is a no-op for a coding agent. |
| "Originally this used X; in 2024 we moved to Y because…" | *(delete, or one clause of why if it prevents reverting)* | History changes no behaviour. |
| "The init container first seeds config, then imports the GPG key, then writes SSH keys…" | "Init crashloop ⇒ `gpgPrivateKey` missing from 1Password." | Script walkthrough is in the script; keep the failure signal only. |
| Layout tree mirroring `ls` | *(delete, keep annotated entries only)* | The environment is the source of truth. |
| "# ---- Git section ----" | "## Git operations" | Banners are noise; headings are structure. |
| Same rule in root and `tk/AGENTS.md`. | Root points to `tk/AGENTS.md`; rule lives there. | Single source of truth. |

## Boundaries pattern

Use when the repo has actions that are destructive, costly, or need human
approval. Name verbs and flags, not categories.

```md
**Allowed:** `status`, `diff`, `log`, `add`, `commit`, `merge --ff-only`.
**Ask first (single-use):** `rebase`, `reset --hard`, `branch -D`, any `--force`.
**Never:** `filter-branch`, `push --mirror`, committing `*.key`.
```

Per-session grants ("push is allowed once the user says push") should say
what the grant covers and that it does not carry across sessions.

## Audit checklist

For each line:

1. **No-op?** Would the agent do this anyway? ("Write clean code", "be
   careful with secrets".) Delete.
2. **Duplicate?** Same meaning elsewhere in the file, in an area file, or in
   the environment (`Makefile` targets, `--help`)? Keep one, point to it.
3. **Stale?** Path, command, tool, or behaviour no longer exists? Fix or
   delete. Check with `ls`, `which`, `grep`.
4. **Misplaced?** Needed only for one area or task? Move to that area's
   AGENTS.md or a doc with a pointer.
5. **Hedged or negated?** Rewrite imperative and positive.
6. **Narrative?** History, migration notes, architecture tours, "how it
   works" walkthroughs of a script or container. Delete; the code and git
   log hold it. Keep a *why* only if it prevents a specific mistake.
7. **Too long?** Over 3 lines for one rule usually means it is explaining
   the *what*; keep the *why* and cut the rest, or move detail behind a
   pointer.

Files that fail 4 and 6 repeatedly are READMEs wearing the wrong name.
Rename to `README.md`, start a fresh AGENTS.md with only the rules, and
point to the README once.

Present findings as a diff. Never silently delete a rule; the human
confirms each cut.

## Size guidance

| File | Target | Hard cap |
|---|---|---|
| Root AGENTS.md | < 60 lines | 150 |
| Area AGENTS.md | < 80 lines | 150 |
| Any single rule | 1–2 lines | 3 |

Lines are the proxy; instruction count is the real budget. A 40-line file
with 60 bullets is worse than an 80-line file with 25.
