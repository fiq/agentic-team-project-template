---
id: INBOX-001
type: inbox
title: Hide template tooling from project domain folders
status: proposed
summary: Boilerplate command and validation tools should live under a custom hidden folder to avoid collisions with application conventions.
proposal_type: pattern
relates_to: []
evidence:
  - .agentic-template/bin/project
  - removal of top-level scripts and Makefile
created_during: add repository-local knowledge layer
recommended_action: review for promotion to pattern
expires_after: 2026-10-11
---

# Hide Template Tooling From Project Domain Folders

## Proposal

Agentic boilerplate commands should live under a custom hidden folder such as
`.agentic-template/bin/` rather than reserving top-level names like `scripts/`
or `Makefile`.

## Evidence

- The current template moved command dispatch and validation to
  `.agentic-template/bin/`.
- This leaves generated projects free to use framework or domain-specific
  folders and build files.

## Curator Notes

- Promote to `patterns/` if this convention holds after the first real project
  instantiation.
