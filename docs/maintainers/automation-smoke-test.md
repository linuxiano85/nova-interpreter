# Automation smoke test

This file exists to validate that repository automation works end-to-end:

- Label sync: labels are present in the repository
- Auto-labeling by path (`docs/**`) and by title (`docs:` prefix)
- Directive-driven labeling via PR body
- Auto-merge when `automerge` is present and checks are green

No functional code changes.

## Example directive block used in the PR body

```
<!-- automation-directives -->
labels: automerge, priority:low
<!-- /automation-directives -->
```