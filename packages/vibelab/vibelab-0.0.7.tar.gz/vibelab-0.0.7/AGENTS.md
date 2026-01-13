# VibeLab - Instructions for AI Coding Agents

Instructions specifically for AI coding agents (Claude Code, Codex, Cursor, etc.) working on the VibeLab codebase. This file contains agent-specific guidance that supplements the other documentation.

## Before You Start

1. **Read DEVELOPMENT.md first** - Architecture decisions, workflows, and how to add features
2. **Read SPEC.md** - Terse product requirements
3. **Skim README.md** - User-facing behavior and CLI usage

## Fresh Implementation Notice

This is a **fresh implementation**. The existing `llm_compare` code in this repository is a prototype used for exploration. Use it as reference/inspiration for patterns (harnesses, git worktrees, React UI), but implement VibeLab from scratch following the specifications.

## Things to Avoid

- **Over-engineering**: Keep it minimal. Don't add features that aren't needed yet. The user strongly prefers simplicity.
- **Backwards-compat shims**: Do **not** add backwards-compatible aliases/wrappers/shims “just in case”. This is a new project with no external deps—**update the callers** unless the user explicitly asks for compatibility.
- **Polluting target repos**: Never modify the repositories being evaluated. Use git worktrees for isolation.
- **Skipping tests**: Write tests first or alongside implementation. Follow the layering approach in DEVELOPMENT.md.
- **Ignoring type hints**: All Python code should be fully typed. Use Pydantic models.
- **Large changes**: Break work into small, focused changes.
- **Hardcoded paths**: Use `VIBELAB_HOME` environment variable for storage paths.
- **Print statements**: Use `logging` module, not `print()`.
- **Guessing at architecture**: When uncertain, check DEVELOPMENT.md or ask.
- **Tile/grid views**: The user prefers table/list views for data display. Use tables for lists of items (scenarios, runs, executors, etc.) rather than card/tile layouts.

## Agent-Specific Tips

### When Reading Code
- The prototype in this repo demonstrates working patterns - review `src/llm_compare/harnesses/` for harness examples
- Check `web/src/components/` for React patterns used in the prototype
- Note: UI components use table views for data lists (see `Dashboard.tsx`, `Scenarios.tsx`, `Runs.tsx`, `Executors.tsx` for examples)

### When Writing Code
- Always run `make check` before considering code complete
- Use the exact tool versions specified: `uv` for Python, `bun` for TypeScript, `ruff` for formatting
- Follow the protocol patterns in `src/vibelab/drivers/` and `src/vibelab/harnesses/`

### When Debugging
```bash
export VIBELAB_LOG_LEVEL=DEBUG
uv run pytest tests/unit/test_models.py -v -s
sqlite3 ~/.vibelab/data.db ".schema"
```

## Quick Reference

| Need | Location |
|------|----------|
| What to build | SPEC.md |
| How to build it | DEVELOPMENT.md |
| Dev setup & workflows | DEVELOPMENT.md |
| User-facing docs | README.md |
| Architecture decisions | DEVELOPMENT.md + `src/vibelab/` |
| Data models | `src/vibelab/models/` |
| API endpoints | `src/vibelab/api/` |
| CLI commands | `src/vibelab/cli/` |
| Real-time updates | DEVELOPMENT.md + `src/vibelab/engine/streaming.py` |
| Frontend polling | DEVELOPMENT.md § Real-time Updates & Polling |

## Status Values (Important!)

**Always use lowercase** when comparing result status values:

```typescript
// ✅ Correct
if (result.status === 'running') { ... }

// ❌ Wrong - API returns lowercase
if (result.status === 'RUNNING') { ... }
```

Valid status values: `queued`, `running`, `completed`, `failed`, `timeout`
