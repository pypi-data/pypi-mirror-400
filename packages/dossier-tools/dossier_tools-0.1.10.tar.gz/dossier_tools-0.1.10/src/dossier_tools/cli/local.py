"""Local CLI commands for dossier-tools."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click
import frontmatter

from ..core import (
    ChecksumStatus,
    ParseError,
    calculate_checksum,
    parse_content,
    parse_file,
    update_checksum,
    validate_file,
    validate_frontmatter,
    verify_checksum,
)
from ..signing import (
    SignatureStatus,
    ensure_dossier_dir,
    key_exists,
    load_signer,
    save_key_pair,
    sign_dossier,
    verify_dossier_signature,
)
from ..signing.ed25519 import Ed25519Signer
from . import display_metadata, main

# Hook configuration for automatic dossier discovery in Claude Code
# Pattern to match workflow-related prompts
DOSSIER_HOOK_PATTERN = (
    r"(?i)(workflow|setup|deploy|migrate|refactor|ci[/-]?cd|pipeline|"
    r"create.*(script|automation|process)|sync.*worktree|onboard|initialize|configure)"
)

# Command that reads prompt from stdin and conditionally outputs dossier list
DOSSIER_HOOK_COMMAND = "dossier prompt-hook"

# Unique identifier to find our hook (since we can't use matcher)
DOSSIER_HOOK_ID = "dossier-discovery-hook"


def install_claude_hook() -> bool:
    """Install UserPromptSubmit hook for automatic dossier discovery.

    This hook injects available dossiers as context when users ask about
    workflow-related tasks, helping Claude suggest relevant dossiers.

    Note: Hooks must be in settings.json (not settings.local.json) to work.

    Returns:
        True if hook was installed, False if already exists
    """
    settings_path = Path.home() / ".claude" / "settings.json"

    # Load existing settings or create new
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except json.JSONDecodeError:
            settings = {}
    else:
        settings = {}

    # Ensure hooks structure exists
    if "hooks" not in settings:
        settings["hooks"] = {}
    if "UserPromptSubmit" not in settings["hooks"]:
        settings["hooks"]["UserPromptSubmit"] = []

    # Define the dossier discovery hook (no matcher - UserPromptSubmit doesn't support it)
    # The filtering is done inside the prompt-hook command
    dossier_hook = {
        "id": DOSSIER_HOOK_ID,
        "hooks": [{"type": "command", "command": DOSSIER_HOOK_COMMAND}],
    }

    # Check if hook already exists (by id)
    existing_hooks = settings["hooks"]["UserPromptSubmit"]
    for hook in existing_hooks:
        if hook.get("id") == DOSSIER_HOOK_ID:
            return False  # Already installed

    # Add the hook
    existing_hooks.append(dossier_hook)

    # Write back with proper formatting
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n")

    return True


def remove_claude_hook() -> bool:
    """Remove the dossier discovery hook from Claude settings.

    Returns:
        True if hook was removed, False if not found
    """
    settings_path = Path.home() / ".claude" / "settings.json"

    if not settings_path.exists():
        return False

    try:
        settings = json.loads(settings_path.read_text())
    except json.JSONDecodeError:
        return False

    if "hooks" not in settings or "UserPromptSubmit" not in settings["hooks"]:
        return False

    original_count = len(settings["hooks"]["UserPromptSubmit"])
    settings["hooks"]["UserPromptSubmit"] = [
        hook for hook in settings["hooks"]["UserPromptSubmit"] if hook.get("id") != DOSSIER_HOOK_ID
    ]

    if len(settings["hooks"]["UserPromptSubmit"]) < original_count:
        settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        return True

    return False


@main.command()
@click.option("--skip-hooks", is_flag=True, help="Skip installing Claude Code hooks")
def init(skip_hooks: bool) -> None:
    """Initialize dossier and install Claude Code discovery hook.

    Creates the ~/.dossier directory and installs the discovery hook
    for Claude Code integration.

    The discovery hook automatically shows available dossiers when you ask
    Claude about workflow-related tasks (setup, deploy, migrate, etc.).

    \b
    Examples:
        dossier init              # Initialize and install hook
        dossier init --skip-hooks # Initialize without hook
    """
    dossier_dir = ensure_dossier_dir()
    click.echo(f"Initialized dossier directory: {dossier_dir}")

    if not skip_hooks:
        click.echo()
        if install_claude_hook():
            click.echo("Installed dossier discovery hook for Claude Code")
            click.echo("  Hook triggers on: workflow, setup, deploy, migrate, refactor, CI/CD, etc.")
        else:
            click.echo("Dossier discovery hook already installed")


@main.command("reset-hooks")
def reset_hooks() -> None:
    """Remove dossier hooks from Claude Code settings.

    Removes the dossier discovery hook that was installed by 'dossier init'.
    Use this if you want to disable automatic dossier suggestions.

    \b
    Examples:
        dossier reset-hooks  # Remove the discovery hook
    """
    if remove_claude_hook():
        click.echo("Removed dossier discovery hook from Claude Code settings")
    else:
        click.echo("No dossier hook found to remove")


# Cache TTL for dossier list (5 minutes)
DOSSIER_LIST_CACHE_TTL_SECONDS = 300


def _get_dossier_list_cache_path() -> Path:
    """Get path to the dossier list cache file."""
    return Path.home() / ".dossier" / "dossier-list-cache.json"


def _get_cached_dossier_list() -> list[dict[str, Any]] | None:
    """Get dossier list from cache if fresh.

    Returns:
        List of dossiers if cache is valid, None otherwise.
    """
    from datetime import datetime, timezone  # noqa: PLC0415

    cache_path = _get_dossier_list_cache_path()
    if not cache_path.exists():
        return None

    try:
        cache_data = json.loads(cache_path.read_text())
        cached_at = datetime.fromisoformat(cache_data.get("cached_at", ""))
        age_seconds = (datetime.now(timezone.utc) - cached_at).total_seconds()

        if age_seconds < DOSSIER_LIST_CACHE_TTL_SECONDS:
            return cache_data.get("dossiers", [])
    except (json.JSONDecodeError, ValueError, OSError):
        pass

    return None


def _cache_dossier_list(dossiers: list[dict[str, Any]]) -> None:
    """Cache the dossier list to disk."""
    from datetime import datetime, timezone  # noqa: PLC0415

    cache_path = _get_dossier_list_cache_path()
    cache_data = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "dossiers": dossiers,
    }

    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache_data))
    except OSError:
        pass  # Ignore cache write errors


def _fetch_all_dossiers_for_hook() -> list[dict[str, Any]]:
    """Fetch all dossiers with caching and pagination support.

    Returns:
        List of all dossiers, or empty list on error.
    """
    # Try cache first
    cached = _get_cached_dossier_list()
    if cached is not None:
        return cached

    # Fetch from registry with pagination
    from ..registry import RegistryError, get_client  # noqa: PLC0415

    try:
        all_dossiers: list[dict[str, Any]] = []
        page = 1
        per_page = 100

        with get_client() as client:
            while True:
                result = client.list_dossiers(page=page, per_page=per_page)
                dossiers = result.get("dossiers", [])
                all_dossiers.extend(dossiers)

                pagination = result.get("pagination", {})
                total = pagination.get("total", 0)

                if len(all_dossiers) >= total or not dossiers:
                    break

                page += 1

    except RegistryError:
        return []
    else:
        # Cache the results
        _cache_dossier_list(all_dossiers)
        return all_dossiers


@main.command("prompt-hook", hidden=True)
def prompt_hook() -> None:
    """Hook command for Claude Code UserPromptSubmit integration.

    Reads JSON from stdin (with 'prompt' field), checks if prompt matches
    workflow-related keywords, and outputs available dossiers if matched.

    This command is designed to be called by Claude Code hooks, not directly.
    """
    import re  # noqa: PLC0415

    # Read JSON from stdin
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            return  # No input, exit silently
        data = json.loads(stdin_data)
    except (json.JSONDecodeError, OSError):
        return  # Invalid input, exit silently

    prompt = data.get("prompt", "")
    if not prompt:
        return  # No prompt, exit silently

    # Check if prompt matches our workflow-related pattern
    if not re.search(DOSSIER_HOOK_PATTERN, prompt):
        return  # No match, exit silently

    # Prompt matches - fetch and display dossiers (with caching)
    dossiers = _fetch_all_dossiers_for_hook()

    if not dossiers:
        return  # No dossiers available

    # Output formatted dossier list
    click.echo("## Available Dossier Workflows")
    click.echo()
    click.echo("Consider using one of these dossiers for your task:")
    for dossier in sorted(dossiers, key=lambda d: d.get("name", ""))[:15]:
        name = dossier.get("name", "unknown")
        title = dossier.get("title", "Untitled")
        click.echo(f"- **{name}**: {title}")
    click.echo()
    click.echo("Use `dossier run <name>` to execute a workflow.")


@main.command("generate-keys")
@click.option("--name", default="default", help="Key name (default: 'default')")
@click.option("--force", is_flag=True, help="Overwrite existing keys")
def generate_keys(name: str, force: bool) -> None:
    """Generate a new Ed25519 key pair."""
    if key_exists(name) and not force:
        click.echo(f"Error: Key '{name}' already exists. Use --force to overwrite.", err=True)
        sys.exit(1)

    signer = Ed25519Signer.generate()
    private_path, public_path = save_key_pair(signer, name)

    click.echo(f"Generated key pair '{name}':")
    click.echo(f"  Private key: {private_path}")
    click.echo(f"  Public key:  {public_path}")
    click.echo()
    click.echo("Public key (for sharing):")
    click.echo(f"  {signer.get_public_key()}")


def _validate_create_frontmatter(fm: dict[str, Any]) -> None:
    """Validate frontmatter for create command, exit on error."""
    required = [("name", "--name"), ("title", "--title"), ("objective", "--objective")]
    for field, flag in required:
        if field not in fm:
            click.echo(f"Error: {flag} is required (or provide in --meta)", err=True)
            sys.exit(1)

    if "authors" not in fm or not fm["authors"]:
        click.echo("Error: --author is required (or provide in --meta)", err=True)
        sys.exit(1)

    for i, author in enumerate(fm["authors"]):
        if isinstance(author, str):
            click.echo(f"Error: authors[{i}] must be an object with 'name', not a string", err=True)
            click.echo('  Example: --meta with {"authors": [{"name": "Alice"}]}', err=True)
            sys.exit(1)
        if isinstance(author, dict) and "name" not in author:
            click.echo(f"Error: authors[{i}] missing required 'name' field", err=True)
            sys.exit(1)


@main.command("from-file")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), help="Output file (default: .ds.md extension)")
@click.option("--meta", type=click.Path(exists=True, path_type=Path), help="JSON file with frontmatter fields")
@click.option("--name", "dossier_name", help="Dossier slug (lowercase, hyphens, e.g., 'my-workflow')")
@click.option("--title", help="Dossier title")
@click.option("--version", "doc_version", default="1.0.0", help="Version (default: 1.0.0)")
@click.option("--status", default="draft", help="Status (default: draft)")
@click.option("--objective", help="Objective description")
@click.option("--author", "authors", multiple=True, help="Author name (can be repeated)")
@click.option("--sign", "do_sign", is_flag=True, help="Sign the dossier after creation")
@click.option("--key", "key_name", default="default", help="Key name for signing (default: 'default')")
@click.option("--signed-by", help="Signer identity (required if --sign)")
def from_file(
    input_file: Path,
    output: Path | None,
    meta: Path | None,
    dossier_name: str | None,
    title: str | None,
    doc_version: str,
    status: str,
    objective: str | None,
    authors: tuple[str, ...],
    do_sign: bool,
    key_name: str,
    signed_by: str | None,
) -> None:
    """Create a dossier from a text file and metadata."""
    # Read body content
    body = input_file.read_text(encoding="utf-8")

    # Build frontmatter from meta file and/or options
    fm: dict[str, Any] = {}

    if meta:
        fm = json.loads(meta.read_text(encoding="utf-8"))

    # CLI options override meta file
    if dossier_name:
        fm["name"] = dossier_name
    if title:
        fm["title"] = title
    if objective:
        fm["objective"] = objective
    if authors:
        # Convert CLI author strings to objects with 'name'
        fm["authors"] = [{"name": a} for a in authors]

    # Set defaults
    fm.setdefault("schema_version", "1.0.0")
    fm["version"] = doc_version
    fm["status"] = status

    # Validate required fields and authors format
    _validate_create_frontmatter(fm)

    # Build dossier content with placeholder checksum
    # We need to do a round-trip through frontmatter to normalize the body
    # (e.g., trailing newlines may be stripped), then calculate the checksum
    fm["checksum"] = {"algorithm": "sha256", "hash": ""}
    post = frontmatter.Post(body, **fm)
    content = frontmatter.dumps(post)

    # Recalculate checksum after frontmatter normalization
    content = update_checksum(content)

    # Optionally sign
    if do_sign:
        if not signed_by:
            click.echo("Error: --signed-by is required when using --sign", err=True)
            sys.exit(1)
        if not key_exists(key_name):
            click.echo(f"Error: Key '{key_name}' not found. Run 'dossier generate-keys' first.", err=True)
            sys.exit(1)

        # Warn if signed_by doesn't match any author
        author_names = [a["name"] for a in fm.get("authors", []) if isinstance(a, dict)]
        if signed_by not in author_names:
            click.echo(
                f"Warning: --signed-by '{signed_by}' does not match any author. "
                "Note: signed_by is a self-reported label; trust is based on the public key in trusted-keys.txt.",
                err=True,
            )

        signer = load_signer(key_name)
        content = sign_dossier(content, signer, signed_by)

    # Determine output path
    if output is None:
        output = input_file if input_file.name.endswith(".ds.md") else input_file.with_suffix(".ds.md")

    output.write_text(content, encoding="utf-8")
    click.echo(f"Created: {output}")


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def validate(file: Path, as_json: bool) -> None:
    """Validate dossier schema."""
    result = validate_file(file)

    if as_json:
        click.echo(json.dumps({"valid": result.valid, "errors": result.errors}))
    elif result.valid:
        click.echo(f"Valid: {file}")
    else:
        click.echo(f"Invalid: {file}", err=True)
        for error in result.errors:
            click.echo(f"  - {error}", err=True)

    sys.exit(0 if result.valid else 1)


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--update", "do_update", is_flag=True, help="Update checksum in file (default: verify)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def checksum(file: Path, do_update: bool, as_json: bool) -> None:
    """Verify or update dossier checksum."""
    content = file.read_text(encoding="utf-8")

    try:
        parsed = parse_content(content)
    except ParseError as e:
        if as_json:
            click.echo(json.dumps({"error": str(e)}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if do_update:
        # Calculate and update checksum
        new_hash = calculate_checksum(parsed.body)
        parsed.frontmatter.setdefault("checksum", {})
        parsed.frontmatter["checksum"]["algorithm"] = "sha256"
        parsed.frontmatter["checksum"]["hash"] = new_hash

        post = frontmatter.Post(parsed.body, **parsed.frontmatter)
        file.write_text(frontmatter.dumps(post), encoding="utf-8")

        if as_json:
            click.echo(json.dumps({"updated": True, "hash": new_hash}))
        else:
            click.echo(f"Updated checksum: {new_hash}")
        sys.exit(0)

    # Verify mode
    result = verify_checksum(parsed.body, parsed.frontmatter)

    if as_json:
        click.echo(
            json.dumps(
                {
                    "status": result.status.value,
                    "valid": result.valid,
                    "expected": result.expected,
                    "actual": result.actual,
                }
            )
        )
    elif result.status == ChecksumStatus.VALID:
        click.echo(f"Checksum valid: {file}")
    elif result.status == ChecksumStatus.MISSING:
        click.echo(f"Checksum missing: {file}", err=True)
    else:
        click.echo(f"Checksum invalid: {file}", err=True)
        click.echo(f"  Expected: {result.expected}", err=True)
        click.echo(f"  Actual:   {result.actual}", err=True)

    sys.exit(0 if result.valid else 1)


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--key", "key_name", default="default", help="Key name from ~/.dossier/ (default: 'default')")
@click.option("--key-file", type=click.Path(exists=True, path_type=Path), help="Path to PEM key file")
@click.option("--signed-by", required=True, help="Signer identity (e.g., email). Note: self-reported, not verified.")
@click.option("-o", "--output", type=click.Path(path_type=Path), help="Output file (default: modify in place)")
def sign(file: Path, key_name: str, key_file: Path | None, signed_by: str, output: Path | None) -> None:
    """Sign a dossier."""
    # Load signer
    if key_file:
        signer = Ed25519Signer.from_pem_file(key_file)
    else:
        if not key_exists(key_name):
            click.echo(f"Error: Key '{key_name}' not found. Run 'dossier generate-keys' first.", err=True)
            sys.exit(1)
        signer = load_signer(key_name)

    # Read and parse file
    content = file.read_text(encoding="utf-8")
    try:
        parsed = parse_content(content)
    except ParseError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Warn if signed_by doesn't match any author
    author_names = [a["name"] for a in parsed.frontmatter.get("authors", []) if isinstance(a, dict)]
    if signed_by not in author_names:
        click.echo(
            f"Warning: --signed-by '{signed_by}' does not match any author. "
            "Note: signed_by is a self-reported label; trust is based on the public key in trusted-keys.txt.",
            err=True,
        )

    # Sign
    signed_content = sign_dossier(content, signer, signed_by)

    # Write output
    output_path = output or file
    output_path.write_text(signed_content, encoding="utf-8")

    if output:
        click.echo(f"Signed: {file} -> {output}")
    else:
        click.echo(f"Signed: {file}")


def _display_schema_result(schema_result: Any) -> None:
    """Display schema validation result."""
    if schema_result.valid:
        click.echo("Schema:    valid")
    else:
        click.echo("Schema:    invalid", err=True)
        for error in schema_result.errors:
            click.echo(f"  - {error}", err=True)


def _display_checksum_result(checksum_result: Any) -> None:
    """Display checksum verification result."""
    status_display = {
        ChecksumStatus.VALID: ("Checksum:  valid", False),
        ChecksumStatus.MISSING: ("Checksum:  missing", False),
    }
    message, is_error = status_display.get(checksum_result.status, ("Checksum:  invalid", True))
    click.echo(message, err=is_error)


def _display_signature_result(sig_result: Any) -> None:
    """Display signature verification result."""
    if sig_result.status == SignatureStatus.VALID:
        click.echo(f"Signature: valid (signed by: {sig_result.signed_by})")
    elif sig_result.status == SignatureStatus.UNSIGNED:
        click.echo("Signature: unsigned")
    else:
        click.echo(f"Signature: invalid ({sig_result.error})", err=True)


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def verify(file: Path, as_json: bool) -> None:
    """Verify dossier checksum and signature."""
    content = file.read_text(encoding="utf-8")

    try:
        parsed = parse_content(content)
    except ParseError as e:
        if as_json:
            click.echo(json.dumps({"error": str(e)}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Validate schema
    schema_result = validate_frontmatter(parsed.frontmatter)

    # Verify checksum
    checksum_result = verify_checksum(parsed.body, parsed.frontmatter)

    # Verify signature
    sig_result = verify_dossier_signature(content)

    # Determine overall validity
    all_valid = (
        schema_result.valid
        and checksum_result.valid
        and sig_result.status in (SignatureStatus.VALID, SignatureStatus.UNSIGNED)
    )

    if as_json:
        output_data = {
            "valid": all_valid,
            "schema": {"valid": schema_result.valid, "errors": schema_result.errors},
            "checksum": {
                "status": checksum_result.status.value,
                "valid": checksum_result.valid,
            },
            "signature": {
                "status": sig_result.status.value,
                "valid": sig_result.valid,
                "signed_by": sig_result.signed_by,
                "timestamp": sig_result.timestamp.isoformat() if sig_result.timestamp else None,
            },
        }
        click.echo(json.dumps(output_data))
    else:
        click.echo(f"File: {file}")
        click.echo()
        _display_schema_result(schema_result)
        _display_checksum_result(checksum_result)
        _display_signature_result(sig_result)

    sys.exit(0 if all_valid else 1)


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def info(file: Path, as_json: bool) -> None:
    """Display local dossier metadata."""
    try:
        parsed = parse_file(file)
    except ParseError as e:
        if as_json:
            click.echo(json.dumps({"error": str(e)}))
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    display_metadata(parsed.frontmatter, str(file), as_json)
