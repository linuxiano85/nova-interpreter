# Repository automation

This repository uses labels and GitHub Actions to automate PR triage and merging.

## Labels
- `automerge`: automatically merge when all required checks pass
- `do-not-merge`: prevent automatic merging
- `blocked`: blocked by external dependency or decision
- `docs`, `tests`, `dependencies`, `feat`, `fix`, `chore`, `refactor`, `security`, `priority:*`

Labels are synchronized from `.github/labels.yml` by the "Sync labels" workflow.

## Auto-labeling
Two mechanisms apply labels to PRs:

1. By path patterns using `.github/labeler.yml` (e.g., docs, tests, dependencies)
2. By title/body using the "Auto label PRs" workflow. Conventional title keywords are supported and a special directive block in the PR body can be used to request labels explicitly:

```
<!-- copilot:labels
automerge
priority:high
docs
-->
```

Only labels that exist in the repository are applied.

## Auto-merge
PRs with the `automerge` label are merged automatically (squash) when:
- All required checks are successful
- The PR is not in Draft
- Neither `do-not-merge` nor `blocked` labels are present

This is implemented by `.github/workflows/auto-merge.yml` and runs on `pull_request_target` for safe operation on forked PRs. Required checks and branch protections are respected.

## Maintenance
- To adjust labels, edit `.github/labels.yml` and push; the sync workflow will reconcile.
- To change path matching, edit `.github/labeler.yml`.
- To disable auto-merge temporarily, add `do-not-merge` or remove `automerge`.