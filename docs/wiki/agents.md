# Agents

`AGENTS.md` is canonical. Claude, Codex, Copilot and other model instructions
should point back to it.

Use persistent roles for continuing responsibility and subagents for bounded
work. Keep context focused and compress outputs.

Before planning or implementation, agents should search `.agents/knowledge/`
through the `knowledge-search` skill. After meaningful work, use
`knowledge-capture` to decide whether discoveries belong in `HANDOFF.toon`,
the knowledge inbox, questions, learnings, decisions, patterns, risks or no
durable record.

Superpowers remains the preferred workflow layer for brainstorming, planning,
TDD, debugging, implementation, review and verification when it is available.
It is optional: Claude, Codex, Copilot and CI must still be able to start from
`AGENTS.md`, `PROJECT_PROFILE.toon`, `HANDOFF.toon` and repository commands
without Superpowers.
