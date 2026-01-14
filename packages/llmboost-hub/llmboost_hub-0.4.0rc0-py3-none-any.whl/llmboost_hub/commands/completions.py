import click
import os

from llmboost_hub.commands.fetch import do_fetch


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option("0.1.0")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose mode.")
@click.pass_context
def main(ctx: click.Context, verbose):
    """LLMBoost Hub (lbh): Manage LLMBoost model containers and environments."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose


def _detect_shell() -> str:
    """
    Detect the current shell from environment variables.

    Returns:
        One of: 'bash', 'zsh', 'fish', or 'powershell' (best-effort; defaults to bash).
    """
    sh = os.environ.get("SHELL", "")
    base = os.path.basename(sh).lower()
    if "zsh" in base:
        return "zsh"
    if "fish" in base:
        return "fish"
    if "bash" in base:
        return "bash"
    # Best-effort: allow powershell if on Windows session
    if os.environ.get("PSModulePath"):
        return "powershell"
    return "bash"


def _one_liner(shell: str, prog: str = "lbh") -> str:
    """
    Return the eval one-liner to enable Click completions for a shell.

    Args:
        shell: Target shell.
        prog: CLI executable name (default: 'lbh').
    """
    var = f"_{prog.upper()}_COMPLETE"
    if shell == "bash":
        return f'eval "$({var}=bash_source {prog})"'
    if shell == "zsh":
        return f'eval "$({var}=zsh_source {prog})"'
    if shell == "fish":
        return f'eval "$({var}=fish_source {prog})"'
    if shell == "powershell":
        return f'$Env:{var}="powershell_source"; {prog} | Out-String | Invoke-Expression'
    # default bash
    return f'eval "$({var}=bash_source {prog})"'


def _default_profile_path(shell: str) -> str:
    """
    Return the default profile file path for a given shell.

    Args:
        shell: Target shell.

    Returns:
        Path to rc/profile file where completions should be persisted.
    """
    home = os.path.expanduser("~")
    if shell == "bash":
        return os.path.join(home, ".bashrc")
    if shell == "zsh":
        return os.path.join(home, ".zshrc")
    if shell == "fish":
        return os.path.join(home, ".config", "fish", "config.fish")
    if shell == "powershell":
        # Prefer $PROFILE if available
        return os.environ.get("PROFILE") or os.path.join(
            home, "Documents", "PowerShell", "Microsoft.PowerShell_profile.ps1"
        )
    return os.path.join(home, ".bashrc")


def _venv_activation_targets(venv_root: str, shell: str | None = None) -> list[tuple[str, str]]:
    """
    Return (shell_key, path) tuples for activation files in a virtualenv.

    Args:
        venv_root: Root path of the active virtualenv.
        shell: Optional single shell to target; when None, include all detected.

    Returns:
        List of (shell_key, file_path) pairs to update.
    """
    targets = []
    if shell in (None, "bash", "zsh"):
        bash_path = os.path.join(venv_root, "bin", "activate")
        zsh_path = os.path.join(venv_root, "bin", "activate.zsh")
        targets.append(("bash/zsh", bash_path))
        targets.append(("zsh", zsh_path))
    if shell in (None, "fish"):
        fish_path = os.path.join(venv_root, "bin", "activate.fish")
        targets.append(("fish", fish_path))
    if shell in (None, "powershell"):
        ps_path = os.path.join(venv_root, "Scripts", "Activate.ps1")
        targets.append(("powershell", ps_path))
    return targets


def _write_block(file_path: str, content: str, start_tag: str, end_tag: str) -> None:
    """
    Idempotently write a tagged content block to a file.

    Behavior:
        - Removes any existing block between start_tag and end_tag.
        - Appends a fresh block to the end of the file (creating the file if needed).

    Args:
        file_path: Destination file path.
        content: Text content to write between tags.
        start_tag: Start marker line.
        end_tag: End marker line.

    Raises:
        ClickException: When writing fails.
    """
    try:
        existing = ""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as fh:
                existing = fh.read()
        # Remove existing block if present
        import re as _re

        pattern = _re.compile(
            _re.escape(start_tag) + r".*?" + _re.escape(end_tag), flags=_re.DOTALL
        )
        cleaned = _re.sub(pattern, "", existing).rstrip()
        # Append new block
        new_text = (
            (cleaned + "\n\n" if cleaned else "")
            + start_tag
            + "\n"
            + content
            + "\n"
            + end_tag
            + "\n"
        )
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(new_text)
    except Exception as e:
        raise click.ClickException(f"Failed to update '{file_path}': {e}")


# completion helper for model names (uses the same source as `lbh list`)
def complete_model_names(ctx: click.Context, param: click.Parameter, query: str = r".*"):
    """
    Shell completion callback returning model names discovered by `do_fetch` (local_only, names_only).

    Behavior:
        - Regex, case-insensitive search on `query`.
    """
    try:
        model_names = do_fetch(query=query, local_only=True, verbose=False, names_only=True)[
            "model"
        ]
        return model_names.dropna().astype(str).unique().tolist()
    except Exception:
        return []


@click.command(name="completions", context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish", "powershell"]),
    default=None,
    help="Target shell (default: auto-detect).",
)
@click.option(
    "--profile",
    is_flag=True,
    help="Append completion to the detected shell profile (~/.bashrc, ~/.zshrc, fish config, or PowerShell profile).",
)
@click.option(
    "--venv",
    is_flag=True,
    help="Append completion to the active virtualenv activation file(s). If shell not specified, updates all present.",
)
@click.pass_context
def completions(ctx: click.Context, shell, profile, venv):
    """
    Manage shell completions.

    \b
    Usage:
        - Print a temporary one-liner for eval (no file modification).
        - Optionally persist to shell profile and/or virtualenv activation files.
    """
    sh = shell or _detect_shell()

    # No persistence flags -> print the one-liner for eval in the current shell
    if not profile and not venv:
        click.echo(_one_liner(sh, "lbh"))
        return

    # Profile persistence
    if profile:
        profile_path = _default_profile_path(sh)
        line = _one_liner(sh, "lbh")
        start_tag = "# >>> lbh shell completion start"
        end_tag = "# <<< lbh shell completion end"
        _write_block(os.path.expanduser(profile_path), line, start_tag, end_tag)
        click.echo(f"Updated profile: {os.path.expanduser(profile_path)}")

    # Venv persistence
    if venv:
        venv_root = os.environ.get("VIRTUAL_ENV", "")
        if not venv_root:
            raise click.ClickException("No active virtualenv detected (VIRTUAL_ENV is not set).")
        targets = _venv_activation_targets(venv_root, shell=sh if shell else None)
        updated = []
        start_tag = "# >>> lbh venv completion start"
        end_tag = "# <<< lbh venv completion end"
        for shell_key, path in targets:
            if os.path.exists(path):
                line = (
                    _one_liner("bash", "lbh")
                    if shell_key == "bash/zsh"
                    else _one_liner(shell_key, "lbh")
                )
                _write_block(path, line, start_tag, end_tag)
                updated.append(path)
        if not updated:
            raise click.ClickException(
                "No matching activation files found in the current virtualenv."
            )
        for p in updated:
            click.echo(f"Updated venv activation: {p}")
