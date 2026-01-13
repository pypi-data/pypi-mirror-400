<p align="center">
	<img src="https://github.com/code-periscope/code-periscope/blob/main/assets/logo.png" alt="Code Periscope" width="180" />
</p>

# Code Periscope

Code Periscope analyzes a Git repository’s history and generates a **risk-focused report** that highlights “hot files/modules” (high churn, low ownership, fix-heavy change patterns, etc.).

By default it keeps the output folder small: it writes a stable `report_model.json` plus one report (`report.md` or `report.html`) and deletes intermediate CSVs. Use `--debug` to keep all CSV artifacts.

It’s designed for quick, local exploration during engineering planning:

- “What parts of this repo look risky right now?”
- “Where is change volume accelerating?”
- “Which files/modules behave like hot spots vs stable areas?”

## What this is *not*

Code Periscope is **not** a static code analysis / linting tool.

In particular, it is not:

- a security scanner (SAST)
- a dependency vulnerability scanner
- a code quality gate meant to fail CI
- a replacement for linters/formatters/type checkers

It focuses on **repository history signals** (churn, ownership concentration, fix-heavy patterns, trending hotspots) to help you prioritize where to look.

For the technical deep dive (pipeline, datasets, metrics, report model), see: **[`how-it-works.md`](https://github.com/code-periscope/code-periscope/blob/main/how-it-works.md)**.

## Prerequisites

- **Python 3.11+**
- Network access if you want to analyze remote repos via `--git-url`

## Install

From PyPI:

```bash
python3 -m pip install -U pip
python3 -m pip install code-periscope
```

## Quickstart

Analyze a local repo:

```bash
code-periscope --repo /path/to/repo --out out/

# Keep intermediate CSV artifacts (datasets) too:
code-periscope --repo /path/to/repo --out out/ --debug

# Emit HTML instead of Markdown:
code-periscope --repo /path/to/repo --out out/ --out-format html

# If you're running from source without installing (e.g. CI), use the module entrypoint:
python3 -m code_periscope --repo /path/to/repo --out out/
```

Analyze a remote repo URL (it will clone into a local cache directory):

```bash
code-periscope --git-url https://github.com/OWNER/REPO.git --out out/

# From source without installing
python3 -m code_periscope --git-url https://github.com/OWNER/REPO.git --out out/
```

## Project

- License: **MIT** (see [`LICENSE`](./LICENSE))
- Contributing: see [`CONTRIBUTING.md`](./CONTRIBUTING.md)
- Code of Conduct: see [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md)

## Development

### Repository layout

This repository is a **single-package** project:

- `src/code_periscope/core` — analytics engine (ingest, metrics, clustering, scoring) **and repository cloning/caching**
- `src/code_periscope/renderers` — Markdown/HTML renderers for the stable report model
- `src/code_periscope/cli.py` — CLI adapter (Typer/Rich)

### Install (editable)

```bash
python3 -m venv .venv
source .venv/bin/activate

make install
```

### Test

```bash
make test
```

### Build wheels

```bash
python3 -m pip install -U build
make build
```

## Versioning

This project currently uses a single version for the `code-periscope` package.

## Releasing (PyPI)

Publishing is handled by `.github/workflows/publish.yml`.

1) Bump `version = "..."` in `pyproject.toml`.
2) Commit the version bump.
3) Create and push a tag:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

The workflow will build and publish the distribution.

### Required GitHub secrets

- `PYPI_API_TOKEN`: PyPI API token for the `code-periscope` project.
- (Optional) `TEST_PYPI_API_TOKEN`: token for TestPyPI, used when manually dispatching the workflow for `testpypi`.
