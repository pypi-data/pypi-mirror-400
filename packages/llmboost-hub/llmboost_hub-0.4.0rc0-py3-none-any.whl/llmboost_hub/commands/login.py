import click
import os
from llmboost_hub.utils.config import config
from llmboost_hub.utils.license_wrapper import is_license_valid, save_license


def do_login(license_file: str | None, verbose: bool = False) -> dict:
    """
    Validate and register an LLMBoost license.

    Flow:
    - If an existing license file validates, return success immediately.
    - Otherwise, prompt interactively for a key (hidden input), write to target path, and re-validate.
    - On failure, remove the newly written file and return an error.

    Args:
        license_file: Optional override for the license file save path; defaults to `config.LBH_LICENSE_PATH`.
        verbose: Reserved for future detailed logging.

    Returns:
        Dict with keys:
            validated: Whether validation succeeded.
            path: Path to the saved/validated license file (if any).
            error: Error string on failure; None on success.
    """
    license_path = config.LBH_LICENSE_PATH

    # If license exists and is valid, short-circuit.
    if os.path.exists(license_path) and is_license_valid():
        return {"validated": True, "path": license_path, "error": None}

    # Prompt for license key (hidden input); normalize whitespace.
    try:
        key = click.prompt("Enter your LLMBoost license key", hide_input=True).strip()
    except Exception:
        return {"validated": False, "path": None, "error": "No license key entered."}
    if not key:
        return {"validated": False, "path": None, "error": "No license key entered."}

    target_path = license_file or license_path
    saved_path = save_license(target_path, key)

    # Re-validate after saving; remove file on failure.
    if is_license_valid():
        return {"validated": True, "path": saved_path, "error": None}
    else:
        try:
            os.remove(saved_path)
        except Exception:
            pass
        return {
            "validated": False,
            "path": saved_path,
            "error": "License validation failed after saving.",
        }


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--license-file", type=click.Path(), help="Path to license file to save (optional).")
@click.pass_context
def login(ctx: click.Context, license_file):
    """
    Validates LLMBoost license.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    res = do_login(license_file, verbose=verbose)

    if res["validated"]:
        click.echo(f"License validated and saved to {res['path']}")
        return

    raise click.ClickException(res["error"] or "License validation failed")
