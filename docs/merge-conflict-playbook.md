# Merge conflict playbook for scaffold branches

If your feature branch and the scaffold branch both touched package entry points,
you may see conflicts around `__init__.py` exports or import wiring.

## Recommended flow

1. Update your branch from target:

   ```bash
   git fetch origin
   git checkout <your-branch>
   git rebase origin/<target-branch>
   ```

2. Apply the scaffold commit (or rebase onto it):

   ```bash
   git cherry-pick d6a394c
   # or: git rebase d6a394c
   ```

3. If conflicts occur, resolve in this order:
   - keep your stage logic implementation
   - keep scaffold directory/package layout
   - merge `__all__` exports so both symbols remain

4. Validate:

   ```bash
   pytest -q
   ```

## Why this should conflict less now

The repository configures Git's `union` merge strategy for
`src/html_to_deck/**/__init__.py` in `.gitattributes`, which helps when both
branches append exports/imports in package entry points.

> Note: `union` can keep duplicate lines. If that happens, quickly deduplicate
> imports/`__all__` in the conflicted file before committing.
