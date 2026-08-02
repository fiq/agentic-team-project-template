---
name: git-worktree-workflow
description: Start, work in and clean up an isolated agent worktree under .worktrees/.
---

# Git Worktree Workflow

## Purpose

Keep parallel agent implementation isolated while the main checkout stays the
coordination and integration surface. Pairs with `worktree-status` (what is
currently active) and `backlog-status` (what is currently claimed).

## Start Work

1. From the main checkout, inspect `AGENTS.md`, `HANDOFF.toon` and
   `PROJECT_PROFILE.toon`, and run `project worktree-status` to confirm no
   other worktree already claims the same scope.
2. Choose a short lowercase slug for the task.
3. Create the worktree from the intended integration base:

   ```sh
   git worktree add -b <agent>/<slug> .worktrees/<agent>-<slug> HEAD
   ```

4. Add a short line to `in_progress:` in `HANDOFF.toon` naming the branch and
   worktree before implementation, so `worktree-status` and `backlog-status`
   agree with git.

## During Work

- Keep changes inside the claimed scope; if it must grow, update
  `HANDOFF.toon` first or record the open question instead.
- Validate with repository commands (`project lint`, `project test`, ...),
  not ad hoc tooling.
- Keep `HANDOFF.toon` semantic and compact — see `handoff-maintenance`.

## Integration

1. Run the cheapest meaningful validation first, then broader checks.
2. Commit on the agent branch, push it, and open a PR per the branch/PR
   workflow in `AGENTS.md`.
3. Human or lead agent owns merge — do not merge your own worktree branch.
4. After merge, remove the `in_progress:` entry and update the main checkout.

## Cleanup

Never remove a dirty worktree. Confirm state first:

```sh
git -C .worktrees/<agent>-<slug> status --short
```

If clean and the branch is integrated (or intentionally abandoned):

```sh
git worktree remove .worktrees/<agent>-<slug>
git branch -d <agent>/<slug>
```

Use `git branch -D` only when the project lead has explicitly chosen to
discard the branch, and record why in `HANDOFF.toon`.
