# Contributing

## Development setup

This repository uses `mise` for local tooling and task orchestration. Assume only `mise` is installed globally.

```bash
mise install
mise run setup
```

`mise run setup` syncs locked dependencies with `uv` and installs the git pre-commit hook.

## Common tasks

| Goal | Command |
| --- | --- |
| Format project files | `mise run format` |
| Lint formatting, Actions, and shell scripts | `mise run lint` |
| Type-check the project | `mise run typecheck` |
| Run the test suite | `mise run test` |
| Build the package | `mise run build` |
| Regenerate CLI docs | `mise run docs` |
| Check generated CLI docs | `mise run docs:check` |
| Run the full local check suite | `mise run check` |
| Generate an SBOM | `mise run sbom` |

If you change command behavior or help text, run `mise run docs` and commit the updated `docs/cli.md`.

## Commits

Commits must follow Conventional Commits. Cocogitto enforces this locally and in CI.

Create commits through `mise`:

- `mise exec cocogitto -- cog commit <type> "<message>" [scope]`
- add `-B` for breaking changes
- run `mise run check:commits` to validate commit messages locally

Examples:

- `feat: add csv import preset`
- `fix: preserve budget totals for empty months`
- `docs: clarify setup flow`

## Pull requests

Before opening a pull request:

- run `mise run check`
- use a Conventional Commit title for the pull request
- update tests and docs when behavior changes
- keep changes focused and small when possible

## Releases

Releases are managed through `mise`, Cocogitto, and GoReleaser.

- `mise run release:version` creates the next version and tag
- `mise run release:check` validates release configuration
- `mise run release:verify` runs the release pipeline locally in verification mode
- push the resulting commit and `v*` tag to trigger the release workflow
