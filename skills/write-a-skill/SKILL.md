---
name: "write-a-skill"
description: "Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, build, or author a new skill."
compatibility: opencode
---

# Writing Skills

> Derived from [Matt Pocock's write-a-skill](https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill) (MIT). Matt's voice and 3-phase workflow preserved verbatim. Additions: validation scripts + references.

## Process

1. **Gather requirements** - ask user about:
   - What task/domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

2. **Draft the skill** - create:
   - SKILL.md with concise instructions
   - Additional reference files if content exceeds 500 lines
   - Utility scripts if deterministic operations needed

3. **Review with user** - present draft and ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── REFERENCE.md       # Detailed docs (if needed)
├── EXAMPLES.md        # Usage examples (if needed)
└── scripts/           # Utility scripts (if needed)
    └── helper.js
```

## SKILL.md Template

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files: See [REFERENCE.md](REFERENCE.md)]
```

## Description Requirements

The description is **the only thing your agent sees** when deciding which skill to load. Max 1024 chars, third person, first sentence says what it does, second sentence is "Use when [specific triggers]".

See [references/description_design_patterns.md](references/description_design_patterns.md) for good/bad examples and trigger patterns.

## When to Add Scripts

Add utility scripts when the operation is deterministic (validation, formatting), the same code would be generated repeatedly, or errors need explicit handling. Scripts save tokens and improve reliability vs generated code.

## When to Split Files

Split when SKILL.md exceeds 100 lines, content has distinct domains (finance vs sales schemas), or advanced features are rarely needed. See [references/progressive_disclosure_principles.md](references/progressive_disclosure_principles.md).

## Review Checklist

After drafting, verify:

- [ ] Description includes triggers ("Use when...")
- [ ] SKILL.md under 100 lines
- [ ] No time-sensitive info
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] References one level deep

## Validation Scripts

Stdlib-only; each accepts `--output json` and exits non-zero on failure:

```
python scripts/skill_review_checklist_runner.py path/to/skill-folder  # all 6 checklist items
python scripts/skill_description_validator.py path/to/SKILL.md
python scripts/skill_structure_validator.py path/to/skill-folder
```
