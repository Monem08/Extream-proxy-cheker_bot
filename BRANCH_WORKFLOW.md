# Auto Conflict Prevention Workflow

This repository follows a strict branch workflow to reduce merge conflicts and keep history clean:

1. Attempt to recreate work branch from `origin/main`:
   - `git fetch origin`
   - `git checkout -B pro origin/main`
2. Never reuse stale branch state.
3. If conflict risk is detected, discard the branch and recreate it from main before reapplying changes.
4. Never merge conflicting code.
5. Keep changes minimal and clean.
6. Never commit directly to `main`.
7. Commit only to `pro`.

## Local fallback when no remote exists

If no `origin` remote or `main` branch is available locally, recreate `pro` from the current default working branch and proceed with the same clean-history rules.
