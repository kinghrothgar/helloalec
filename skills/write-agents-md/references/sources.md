# Sources

Research distilled into this skill (October 2026). Read when a rule needs
provenance or when updating the skill against newer guidance.

## Skills

- **mattpocock/skills — `writing-for-agents`**
  <https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents>
  The theory this skill leans on: context pointers (wording decides whether
  the agent reaches the target), the two loads (context vs. human cognitive),
  information hierarchy (step → in-file reference → disclosed reference),
  completion criteria, leading words, negation priming, pruning for no-ops and
  sediment, environment as source of truth.
- **netresearch/agent-rules-skill**
  <https://github.com/netresearch/agent-rules-skill>
  Script-driven generator. Borrowed: thin root (< 150 lines) + scoped files,
  "never fabricate — verify every command and path", pointer principle,
  freshness checks.

## Guidance

- **HumanLayer — Writing a good CLAUDE.md** (Nov 2025)
  <https://www.humanlayer.dev/blog/writing-a-good-claude-md>
  Instruction budget (~150–200), uniform degradation, the
  "may or may not be relevant" system reminder, < 300 lines (theirs < 60),
  progressive disclosure, pointers over copies, not a linter, don't
  auto-generate.
- **GitHub Blog — How to write a great agents.md: lessons from 2,500+
  repositories** (Nov 2025)
  <https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/>
  Commands early with flags; always / ask first / never boundaries; specific
  stack; six areas: commands, testing, structure, style, git, boundaries.
- **agents.md specification**
  <https://agents.md/>
  Plain Markdown, no required fields; nearest file wins; nested files per
  subproject; explicit chat prompts override.
- **opencode — Rules**
  <https://opencode.ai/docs/rules/>
  Precedence (local → global → Claude fallback); `@file` is not auto-loaded,
  pointers must be read instructions; `opencode.json` `instructions` globs as
  the alternative for monorepos.
- **Anthropic — Claude Code best practices**
  <https://code.claude.com/docs/en/best-practices>
  Context window is the scarce resource; keep CLAUDE.md short; load detail on
  demand.
- **AI Hero — A Complete Guide To AGENTS.md**
  <https://www.aihero.dev/a-complete-guide-to-agents-md>
  One-liner project description; move language-specific rules to separate
  files behind a one-line pointer.
