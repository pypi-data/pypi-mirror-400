from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print as rprint
from rich.table import Table

from . import __version__
from .config import AdrConfig
from .fs import (
    ensure_dir,
    find_adr_by_index,
    format_index,
    get_existing_adrs,
    parse_adr_filename,
    read_adr_status,
    search_adrs,
    update_adr_status,
)
from .generator import prepare_adr_output, resolve_builtin_template, write_adr, write_adr_docx
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
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(text) or {}
        elif path.suffix.lower() == ".json":
            data = json.loads(text)
        else:
            raise typer.BadParameter("Input must be .yaml, .yml, or .json")
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"Failed to parse {path.name}: {exc}") from exc

    try:
        return CriteriaModel.model_validate(data)
    except Exception as exc:
        raise typer.BadParameter(f"Invalid criteria: {exc}") from exc


def _resolve_template(
    template: Optional[str],
    config: AdrConfig,
    project_root: Path,
) -> Optional[Path]:
    """
    Resolve template path from CLI option or config.

    Supports:
    - Built-in templates: "madr", "hld", "lld"
    - Custom template paths (absolute or relative to project root)
    """
    template_name = template or config.template

    # Check for built-in templates first
    if template_name:
        builtin_path = resolve_builtin_template(template_name)
        if builtin_path and builtin_path.exists():
            return builtin_path

    # Handle explicit template path from CLI
    if template:
        return Path(template).resolve()

    # Handle custom template path from config
    if config.template and config.template not in ("madr", "hld", "lld"):
        config_path = Path(config.template)
        if not config_path.is_absolute():
            candidate = (project_root / config_path).resolve()
            if candidate.exists():
                config_path = candidate
            else:
                config_path = (project_root / ".adr" / "templates" / config_path).resolve()
        if not config_path.exists():
            raise typer.BadParameter(f"Template not found: {config_path}")
        return config_path

    return None


def _handle_docx_error(exc: RuntimeError) -> None:
    rprint(f"[red]{exc}[/red]")
    raise typer.Exit(code=1)


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
    config = AdrConfig.load(project_root=root)
    criteria_path = Path(input).resolve()
    template_path = _resolve_template(template, config, root)

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
        try:
            docx_path = write_adr_docx(criteria, docs_dir=docs_dir, output_info=output_info)
        except RuntimeError as exc:
            _handle_docx_error(exc)
        rprint(f"[green]ADR written to[/green] {md_path}")
        rprint(f"[green]ADR (Word) written to[/green] {docx_path}")
        return

    fmt = format.lower()
    if fmt == "md":
        output_path = write_adr(criteria, docs_dir=docs_dir, template=template_path)
        rprint(f"[green]ADR written to[/green] {output_path}")
    elif fmt == "docx":
        try:
            output_path = write_adr_docx(criteria, docs_dir=docs_dir)
        except RuntimeError as exc:
            _handle_docx_error(exc)
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
    root = Path(directory).resolve()
    config = AdrConfig.load(project_root=root)
    status_choices = "|".join(config.status_values)

    title = typer.prompt("Title (e.g., Database Selection)").strip()
    status = typer.prompt(f"Status [{status_choices}]", default=config.status_values[0]).strip()
    author = typer.prompt("Your name (optional)", default="").strip()
    rationale = typer.prompt("Short rationale (optional)", default="").strip()

    if status and not config.is_valid_status(status):
        allowed = ", ".join(config.status_values)
        rprint(f"[red]Invalid status '{status}'. Allowed: {allowed}[/red]")
        raise typer.Exit(code=1)

    criteria = CriteriaModel(
        title=title,
        status=status or config.status_values[0],
        authors=[author] if author else None,
        decision=DecisionModel(chosen=title, rationale=rationale) if rationale else None,
    )

    docs_dir = root / "docs"
    template_path = _resolve_template(None, config, root)

    if not format:
        # Generate both formats with shared index
        output_info = prepare_adr_output(criteria, docs_dir)
        md_path = write_adr(criteria, docs_dir=docs_dir, template=template_path, output_info=output_info)
        try:
            docx_path = write_adr_docx(criteria, docs_dir=docs_dir, output_info=output_info)
        except RuntimeError as exc:
            _handle_docx_error(exc)
        rprint(f"[green]ADR created:[/green] {md_path}")
        rprint(f"[green]ADR (Word) created:[/green] {docx_path}")
        return

    fmt = format.lower()
    if fmt == "md":
        output_path = write_adr(criteria, docs_dir=docs_dir, template=template_path)
        rprint(f"[green]ADR created:[/green] {output_path}")
    elif fmt == "docx":
        try:
            output_path = write_adr_docx(criteria, docs_dir=docs_dir)
        except RuntimeError as exc:
            _handle_docx_error(exc)
        rprint(f"[green]ADR (Word) created:[/green] {output_path}")
    else:
        raise typer.BadParameter("--format must be 'md' or 'docx'")


@app.command()
def quick(
    title: str = typer.Argument(..., help="ADR title"),
    status: str = typer.Option("Proposed", "--status", "-s", help="ADR status"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Author name"),
    decision: Optional[str] = typer.Option(
        None, "--decision", "-d", help="Short decision rationale"
    ),
    directory: str = typer.Option(".", help="Project root"),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: md or docx. If omitted, both are generated.",
        case_sensitive=False,
    ),
) -> None:
    """Create a quick ADR with minimal input."""
    root = Path(directory).resolve()
    config = AdrConfig.load(project_root=root)

    # Validate status
    if not config.is_valid_status(status):
        allowed = ", ".join(config.status_values)
        rprint(f"[red]Invalid status '{status}'. Allowed: {allowed}[/red]")
        raise typer.Exit(code=1)

    # Build minimal criteria
    criteria = CriteriaModel(
        title=title,
        status=status,
        authors=[author] if author else None,
        decision=DecisionModel(chosen=title, rationale=decision) if decision else None,
    )

    docs_dir = root / "docs"
    template_path = _resolve_template(None, config, root)

    if not format:
        # Generate both formats with shared index
        output_info = prepare_adr_output(criteria, docs_dir)
        md_path = write_adr(
            criteria, docs_dir=docs_dir, template=template_path, output_info=output_info
        )
        try:
            docx_path = write_adr_docx(criteria, docs_dir=docs_dir, output_info=output_info)
        except RuntimeError as exc:
            _handle_docx_error(exc)
        rprint(f"[green]ADR created:[/green] {md_path}")
        rprint(f"[green]ADR (Word) created:[/green] {docx_path}")
        return

    fmt = format.lower()
    if fmt == "md":
        output_path = write_adr(criteria, docs_dir=docs_dir, template=template_path)
        rprint(f"[green]ADR created:[/green] {output_path}")
    elif fmt == "docx":
        try:
            output_path = write_adr_docx(criteria, docs_dir=docs_dir)
        except RuntimeError as exc:
            _handle_docx_error(exc)
        rprint(f"[green]ADR (Word) created:[/green] {output_path}")
    else:
        raise typer.BadParameter("--format must be 'md' or 'docx'")


@app.command()
def status(
    number: str = typer.Argument(..., help="ADR number (e.g., 001 or 1)"),
    new_status: Optional[str] = typer.Argument(None, help="New status to set"),
    directory: str = typer.Option(".", help="Project root"),
) -> None:
    """View or change the status of an ADR."""
    root = Path(directory).resolve()
    config = AdrConfig.load(project_root=root)
    adr_dir = root / "docs" / "adr"

    # Parse index
    try:
        index = int(number)
    except ValueError:
        rprint(f"[red]Invalid ADR number: {number}[/red]")
        raise typer.Exit(code=1) from None

    # Find ADR
    adr_path = find_adr_by_index(adr_dir, index)
    if not adr_path:
        rprint(f"[red]ADR {format_index(index)} not found[/red]")
        raise typer.Exit(code=1)

    # If no new status, just show current
    if new_status is None:
        current = read_adr_status(adr_path)
        rprint(f"ADR {format_index(index)}: [cyan]{current}[/cyan]")
        return

    # Validate new status
    if not config.is_valid_status(new_status):
        allowed = ", ".join(config.status_values)
        rprint(f"[red]Invalid status '{new_status}'. Allowed: {allowed}[/red]")
        raise typer.Exit(code=1)

    # Update status
    old_status = read_adr_status(adr_path)
    update_adr_status(adr_path, new_status)
    rprint(f"ADR {format_index(index)}: [yellow]{old_status}[/yellow] → [green]{new_status}[/green]")


@app.command()
def search(
    keyword: str = typer.Argument(..., help="Keyword to search for"),
    directory: str = typer.Option(".", help="Project root"),
    limit: int = typer.Option(0, "--limit", "-n", help="Max results (0 = unlimited)"),
    context: int = typer.Option(0, "--context", "-C", help="Lines of context"),
) -> None:
    """Search ADRs for a keyword."""
    root = Path(directory).resolve()
    adr_dir = root / "docs" / "adr"

    if not adr_dir.exists():
        rprint("[red]No ADR directory found. Run 'adr init' first.[/red]")
        raise typer.Exit(code=1)

    results = search_adrs(adr_dir, keyword, context)

    if not results:
        rprint(f"[yellow]No results found for '{keyword}'[/yellow]")
        return

    # Apply limit
    if limit > 0:
        results = results[:limit]

    # Display results
    rprint(f"[green]Found {len(results)} match(es) for '{keyword}':[/green]\n")

    for path, line_num, line, ctx in results:
        parsed = parse_adr_filename(path.name)
        if parsed:
            idx, slug, _ = parsed
            rprint(f"[cyan]{format_index(idx)}[/cyan] {path.name}:{line_num}")
        else:
            rprint(f"[cyan]{path.name}[/cyan]:{line_num}")

        if context > 0 and ctx:
            for ctx_line in ctx:
                rprint(f"    {ctx_line}")
        else:
            rprint(f"    {line}")
        rprint()


# Central repository for community ADRs
COMMUNITY_REPO = "LighthouseGlobal/adr-builder"
COMMUNITY_ADR_PATH = "community-adrs"


def _run_gh_command(args: list[str]) -> tuple[bool, str]:
    """Run a gh CLI command and return (success, output)."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except FileNotFoundError:
        return False, "GitHub CLI (gh) not found. Install from https://cli.github.com/"


def _get_gh_username() -> str | None:
    """Get the authenticated GitHub username."""
    success, output = _run_gh_command(["api", "user", "--jq", ".login"])
    return output if success else None


@app.command()
def publish(
    number: str = typer.Argument(..., help="ADR number to publish (e.g., 001 or 1)"),
    namespace: Optional[str] = typer.Option(
        None, "--namespace", "-n",
        help="Namespace for the ADR (default: your GitHub username)"
    ),
    directory: str = typer.Option(".", help="Project root"),
    message: Optional[str] = typer.Option(
        None, "--message", "-m", help="Description for the pull request"
    ),
) -> None:
    """
    Publish an ADR to the community repository.

    This creates a pull request to add your ADR to the central adr-builder
    repository under community-adrs/{namespace}/.

    Requires GitHub CLI (gh) to be installed and authenticated.
    """
    root = Path(directory).resolve()
    adr_dir = root / "docs" / "adr"

    # Parse ADR number
    try:
        index = int(number)
    except ValueError:
        rprint(f"[red]Invalid ADR number: {number}[/red]")
        raise typer.Exit(code=1) from None

    # Find local ADR
    adr_path = find_adr_by_index(adr_dir, index)
    if not adr_path:
        rprint(f"[red]ADR {format_index(index)} not found locally[/red]")
        raise typer.Exit(code=1)

    # Check gh CLI is available and authenticated
    rprint("[dim]Checking GitHub CLI authentication...[/dim]")
    username = _get_gh_username()
    if not username:
        rprint("[red]GitHub CLI not authenticated. Run 'gh auth login' first.[/red]")
        raise typer.Exit(code=1)

    # Use namespace or default to username
    ns = namespace or username
    rprint(f"[dim]Publishing as namespace: {ns}[/dim]")

    # Read ADR content
    adr_content = adr_path.read_text(encoding="utf-8")
    adr_filename = adr_path.name

    # Create unique branch name
    branch_name = f"community-adr/{ns}/{adr_filename.replace('.md', '')}-{int(time.time())}"

    # Target path in the community repo
    target_path = f"{COMMUNITY_ADR_PATH}/{ns}/{adr_filename}"

    rprint(f"[dim]Creating branch: {branch_name}[/dim]")

    # Fork the repo if needed (gh handles this automatically)
    # Create a new branch and add the file via GitHub API
    success, error = _run_gh_command([
        "api", f"repos/{COMMUNITY_REPO}/forks", "--method", "POST", "--silent"
    ])
    # Ignore fork errors (might already exist)

    # Get the default branch
    success, default_branch = _run_gh_command([
        "api", f"repos/{COMMUNITY_REPO}", "--jq", ".default_branch"
    ])
    if not success:
        rprint(f"[red]Failed to get repository info: {default_branch}[/red]")
        raise typer.Exit(code=1)

    # Get the latest commit SHA from the default branch
    success, base_sha = _run_gh_command([
        "api", f"repos/{username}/adr-builder/git/refs/heads/{default_branch}",
        "--jq", ".object.sha"
    ])
    if not success:
        # Try to sync fork first
        rprint("[dim]Syncing fork with upstream...[/dim]")
        _run_gh_command(["repo", "sync", f"{username}/adr-builder", "--force"])
        success, base_sha = _run_gh_command([
            "api", f"repos/{username}/adr-builder/git/refs/heads/{default_branch}",
            "--jq", ".object.sha"
        ])
        if not success:
            rprint(f"[red]Failed to get base SHA: {base_sha}[/red]")
            raise typer.Exit(code=1)

    # Create/update file in the fork using contents API
    encoded_content = base64.b64encode(adr_content.encode()).decode()

    # Create branch reference first
    rprint("[dim]Creating branch in fork...[/dim]")
    ref_payload = json.dumps({"ref": f"refs/heads/{branch_name}", "sha": base_sha})

    # Write payload to temp file for gh api
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(ref_payload)
        ref_file = f.name

    success, result = _run_gh_command([
        "api", f"repos/{username}/adr-builder/git/refs",
        "--method", "POST",
        "--input", ref_file,
    ])
    os.unlink(ref_file)

    if not success and "Reference already exists" not in result:
        rprint(f"[red]Failed to create branch: {result}[/red]")
        raise typer.Exit(code=1)

    # Now create the file in the new branch
    rprint("[dim]Uploading ADR to fork...[/dim]")
    file_payload = json.dumps({
        "message": f"Add community ADR: {ns}/{adr_filename}",
        "content": encoded_content,
        "branch": branch_name,
    })

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(file_payload)
        file_file = f.name

    success, result = _run_gh_command([
        "api", f"repos/{username}/adr-builder/contents/{target_path}",
        "--method", "PUT",
        "--input", file_file,
    ])
    os.unlink(file_file)

    if not success:
        rprint(f"[red]Failed to upload ADR: {result}[/red]")
        raise typer.Exit(code=1)

    # Create pull request
    rprint("[dim]Creating pull request...[/dim]")
    pr_title = f"Add community ADR: {ns}/{adr_filename}"
    pr_body = message or f"This PR adds a community ADR from @{username}.\n\n**ADR:** `{adr_filename}`\n**Namespace:** `{ns}`"

    pr_payload = json.dumps({
        "title": pr_title,
        "body": pr_body,
        "head": f"{username}:{branch_name}",
        "base": default_branch,
    })

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(pr_payload)
        pr_file = f.name

    success, result = _run_gh_command([
        "api", f"repos/{COMMUNITY_REPO}/pulls",
        "--method", "POST",
        "--input", pr_file,
    ])
    os.unlink(pr_file)

    if not success:
        rprint(f"[red]Failed to create pull request: {result}[/red]")
        raise typer.Exit(code=1)

    # Parse PR URL from response
    try:
        pr_data = json.loads(result)
        pr_url = pr_data.get("html_url", "")
        rprint("\n[green]Successfully published ADR![/green]")
        rprint(f"[green]Pull request created: {pr_url}[/green]")
        rprint(f"\n[dim]Your ADR will be available at:[/dim]")
        rprint(f"[cyan]{COMMUNITY_ADR_PATH}/{ns}/{adr_filename}[/cyan]")
        rprint(f"\n[dim]Once the PR is merged, others can reference your ADR.[/dim]")
    except json.JSONDecodeError:
        rprint(f"[green]Pull request created successfully![/green]")
        rprint(f"[dim]Check {COMMUNITY_REPO} for your PR.[/dim]")


if __name__ == "__main__":
    app()
