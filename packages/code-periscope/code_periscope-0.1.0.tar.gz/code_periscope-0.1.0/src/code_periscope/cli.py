from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from code_periscope.core.pipeline import analyze_repository
from code_periscope.core.report_model import ReportModel
from code_periscope.renderers.html import render_html
from code_periscope.renderers.markdown import render_markdown

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.command("analyze")
def analyze(
    repo: Optional[Path] = typer.Option(
        None,
        "--repo",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Path to a local Git repository.",
    ),
    git_url: Optional[str] = typer.Option(
        None,
        "--git-url",
        help="Git URL to clone (HTTPS/SSH). Clones into a local cache directory.",
    ),
    out: Path = typer.Option(
        Path("out"),
        "--out",
        file_okay=False,
        dir_okay=True,
        help="Output directory for CSVs and reports.",
    ),
    refresh: bool = typer.Option(
        False,
        "--refresh",
        help="If using --git-url, re-clone the repository even if cached.",
    ),
    max_commits: Optional[int] = typer.Option(
        None,
        "--max-commits",
        min=1,
        help="Limit number of commits to scan (useful for quick tests).",
    ),
    k: int = typer.Option(5, "--k", min=2, help="Number of clusters (KMeans)."),
    seed: int = typer.Option(42, "--seed", help="Random seed for clustering."),
    top_n: int = typer.Option(20, "--top", min=1, help="Top N risky items to show in report."),
) -> None:
    """Analyze a repository and write datasets/reports to disk."""

    if (repo is None) == (git_url is None):
        raise typer.BadParameter("Provide exactly one of --repo or --git-url")

    out.mkdir(parents=True, exist_ok=True)

    report: ReportModel = analyze_repository(
        repo=repo,
        git_url=git_url,
        refresh=refresh,
        max_commits=max_commits,
        out_dir=out,
        k=k,
        seed=seed,
        top_n=top_n,
        console=console,
    )

    report_json_path = out / "report_model.json"
    report.to_json(report_json_path)
    console.print(f"Wrote {report_json_path}")

    report_md_path = out / "risk_report.md"
    report_md_path.write_text(render_markdown(report), encoding="utf-8")
    console.print(f"Wrote {report_md_path}")

    report_html_path = out / "risk_report.html"
    report_html_path.write_text(render_html(report), encoding="utf-8")
    console.print(f"Wrote {report_html_path}")


if __name__ == "__main__":
    app()
