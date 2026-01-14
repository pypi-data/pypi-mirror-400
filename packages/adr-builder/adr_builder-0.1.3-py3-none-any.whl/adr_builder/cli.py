from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print as rprint
from rich.table import Table

from . import __version__
from .fs import ensure_dir, get_existing_adrs
from .generator import prepare_adr_output, write_adr, write_adr_docx
from .models import CriteriaModel, DecisionModel
from .validator import validate_criteria


def version_callback(value: bool) -> None:
    if value:
        rprint(f"adr-builder version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="adr",
    help="ADR Builder - generate Architectural Decision Records with zero coding required.",
    no_args_is_help=True,
)


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit."
    ),
) -> None:
    """ADR Builder CLI."""
    pass


def _load_criteria(path: Path) -> CriteriaModel:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text) or {}
    elif path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        raise typer.BadParameter("Input must be .yaml, .yml, or .json")
    return CriteriaModel.model_validate(data)


@app.command()
def init(
    directory: str = typer.Argument(
        ".", help="Project root where 'docs/adr/' and '.adr/' will be created if missing"
    )
) -> None:
    """
    Initialize ADR scaffolding: creates docs/adr/ and a default config directory.
    """
    root = Path(directory).resolve()
    docs = root / "docs" / "adr"
    cfg = root / ".adr"

    ensure_dir(docs)
    ensure_dir(cfg)

    # Write a basic config if not present
    cfg_file = cfg / "adr.config.yaml"
    if not cfg_file.exists():
        cfg_file.write_text(
            "template: madr\nstatus_values: [Proposed, Accepted, Superseded, Rejected]\n",
            encoding="utf-8",
        )

    rprint(f"[green]Initialized ADR directories at[/green] {root}")


@app.command()
def generate(
    input: str = typer.Option(..., "--input", "-i", help="Path to criteria YAML/JSON"),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Optional path to a custom Jinja2 template"
    ),
    directory: str = typer.Option(".", help="Project root where docs/adr/ lives"),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: md (Markdown) or docx (Word). If omitted, both are generated.",
        case_sensitive=False,
    ),
) -> None:
    """
    Generate an ADR from a criteria file.
    """
    root = Path(directory).resolve()
    criteria_path = Path(input).resolve()
    template_path = Path(template).resolve() if template else None

    criteria = _load_criteria(criteria_path)
    errors = validate_criteria(criteria, project_root=root)
    if errors:
        for e in errors:
            rprint(f"[red]- {e}[/red]")
        raise typer.Exit(code=1)

    docs_dir = root / "docs"

    if not format:
        # Generate both formats with shared index to avoid race condition
        output_info = prepare_adr_output(criteria, docs_dir)
        md_path = write_adr(criteria, docs_dir=docs_dir, template=template_path, output_info=output_info)
        docx_path = write_adr_docx(criteria, docs_dir=docs_dir, output_info=output_info)
        rprint(f"[green]ADR written to[/green] {md_path}")
        rprint(f"[green]ADR (Word) written to[/green] {docx_path}")
        return

    fmt = format.lower()
    if fmt == "md":
        output_path = write_adr(criteria, docs_dir=docs_dir, template=template_path)
        rprint(f"[green]ADR written to[/green] {output_path}")
    elif fmt == "docx":
        output_path = write_adr_docx(criteria, docs_dir=docs_dir)
        rprint(f"[green]ADR (Word) written to[/green] {output_path}")
    else:
        raise typer.BadParameter("--format must be 'md' or 'docx'")


@app.command()
def validate(
    input: str = typer.Option(..., "--input", "-i", help="Path to criteria YAML/JSON"),
    directory: str = typer.Option(".", help="Project root for config loading"),
) -> None:
    """
    Validate a criteria file for completeness and consistency.
    """
    root = Path(directory).resolve()
    criteria = _load_criteria(Path(input))
    errors = validate_criteria(criteria, project_root=root)
    if errors:
        rprint("[red]Validation failed:[/red]")
        for e in errors:
            rprint(f"- {e}")
        raise typer.Exit(code=1)
    rprint("[green]Criteria is valid.[/green]")


@app.command(name="list")
def list_adrs(directory: str = typer.Option(".", help="Project root where docs/adr/ lives")) -> None:
    """
    List existing ADRs.
    """
    root = Path(directory).resolve()
    adr_dir = root / "docs" / "adr"
    entries = get_existing_adrs(adr_dir)
    table = Table(title="ADRs")
    table.add_column("#", justify="right")
    table.add_column("Slug")
    table.add_column("Path")
    for idx, slug, path in entries:
        try:
            display_path = str(path.relative_to(root))
        except ValueError:
            display_path = str(path)
        table.add_row(str(idx), slug, display_path)
    rprint(table)


@app.command()
def new(
    directory: str = typer.Option(".", help="Project root where docs/adr/ lives"),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: md (Markdown) or docx (Word). If omitted, both are generated.",
        case_sensitive=False,
    ),
) -> None:
    """
    Create a new ADR via guided prompts (minimal fields).
    """
    title = typer.prompt("Title (e.g., Database Selection)").strip()
    status = typer.prompt("Status [Proposed|Accepted|Superseded|Rejected]", default="Proposed").strip()
    author = typer.prompt("Your name (optional)", default="").strip()
    rationale = typer.prompt("Short rationale (optional)", default="").strip()

    criteria = CriteriaModel(
        title=title,
        status=status or "Proposed",
        authors=[author] if author else None,
        decision=DecisionModel(chosen=title, rationale=rationale) if rationale else None,
    )

    docs_dir = Path(directory).resolve() / "docs"

    if not format:
        # Generate both formats with shared index
        output_info = prepare_adr_output(criteria, docs_dir)
        md_path = write_adr(criteria, docs_dir=docs_dir, output_info=output_info)
        docx_path = write_adr_docx(criteria, docs_dir=docs_dir, output_info=output_info)
        rprint(f"[green]ADR created:[/green] {md_path}")
        rprint(f"[green]ADR (Word) created:[/green] {docx_path}")
        return

    fmt = format.lower()
    if fmt == "md":
        output_path = write_adr(criteria, docs_dir=docs_dir)
        rprint(f"[green]ADR created:[/green] {output_path}")
    elif fmt == "docx":
        output_path = write_adr_docx(criteria, docs_dir=docs_dir)
        rprint(f"[green]ADR (Word) created:[/green] {output_path}")
    else:
        raise typer.BadParameter("--format must be 'md' or 'docx'")


if __name__ == "__main__":
    app()
