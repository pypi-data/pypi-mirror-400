import click
import subprocess

from llmboost_hub.utils.container_utils import (
    container_name_for_model,
    is_container_running,
)
from llmboost_hub.commands.run import do_run
from llmboost_hub.commands.completions import complete_model_names


def do_chat(model: str, verbose: bool = False) -> dict:
    """
    Ensure a container is running, then exec `llmboost chat --model_name <model>`.

    Args:
        model: Target model identifier.
        verbose: If True, echo docker exec command.

    Returns:
        Dict: {returncode: int, container_name: str, error: str|None}
    """
    cname = container_name_for_model(model)
    if not is_container_running(cname):
        if verbose:
            click.echo(f"[chat] No running container for {model}; starting via lbh run...")
        res = do_run(model, lbh_workspace=None, docker_args=(), verbose=verbose)
        if res["returncode"] != 0:
            return {"returncode": res["returncode"], "container_name": "", "error": res["error"]}
    # Re-check after attempting to start container
    if not is_container_running(cname):
        return {
            "returncode": 1,
            "container_name": "",
            "error": "Failed to start container for chat.",
        }

    exec_cmd = ["docker", "exec", "-it", cname, "llmboost", "chat", "--model_name", model]
    if verbose:
        click.echo("[chat] " + " ".join(exec_cmd))
    try:
        subprocess.run(exec_cmd, check=True)
        return {"returncode": 0, "container_name": cname, "error": None}
    except subprocess.CalledProcessError as e:
        return {
            "returncode": e.returncode,
            "container_name": cname,
            "error": f"Failed to start chat (exit {e.returncode})",
        }


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("model", required=True, shell_complete=complete_model_names)
@click.pass_context
def chat(ctx: click.Context, model):
    """
    Start an interactive chat session inside the model container.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    res = do_chat(model, verbose=verbose)
    if res["returncode"] != 0:
        raise click.ClickException(res["error"] or "Chat failed")
