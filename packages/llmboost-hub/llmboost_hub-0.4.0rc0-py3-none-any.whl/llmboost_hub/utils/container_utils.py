import socket
import subprocess
import re
from llmboost_hub.utils.config import config


def container_name_for_model(model_id: str) -> str:
    """
    Derive the container name used by lbh run from a model id.
    """
    return str(model_id or "").replace(":", "_").replace("/", "_")


def _port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    """
    Return True if TCP connection to host:port succeeds.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def _llmboost_proc_and_port(cname: str) -> tuple[bool, int | None]:
    """
    Inspect running processes and detect llmboost serve and its port.
    Returns (running, port) where:
        - running=True if a 'llmboost serve' command is found
        - port is the integer parsed from '--port <n>' or '--port=<n>' if present; otherwise None
    """
    try:
        cmd = ["docker", "exec", cname, "sh", "-lc", "ps -eo pid,cmd"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            return False, None
        port = None
        running = False
        for line in (res.stdout or "").splitlines():
            # Look for llmboost serve specifically
            if "llm" in line and "serve" in line:
                running = True
                # Prefer explicit --port flags; support '--port config.LBH_SERVE_PORT' or '--port=config.LBH_SERVE_PORT'
                m = re.search(r"--port(?:\s*=\s*|\s+)(\d+)", line)
                if m:
                    try:
                        port = int(m.group(1))
                    except Exception:
                        port = None
                # Do not break; last occurrence wins in case of multiple matches
        return running, port
    except Exception:
        return False, None


def is_container_running(container_name: str) -> bool:
    """
    Return True if the given container is running.
    """
    try:
        out = subprocess.check_output(
            ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out.lower() == "true"
    except Exception:
        return False


def _llmboost_tuner_running(cname: str) -> bool:
    """
    Return True if a 'llmboost tuner' process is found inside the container.
    """
    try:
        cmd = ["docker", "exec", cname, "sh", "-lc", "ps -eo pid,cmd"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            return False
        for line in (res.stdout or "").splitlines():
            if "llmboost" in line and "tuner" in line:
                return True
        return False
    except Exception:
        return False


def is_model_tuning(container_name: str) -> bool:
    """
    Return True if the given container is running and a llmboost tuner process is active.
    """
    if not is_container_running(container_name):
        return False
    return _llmboost_tuner_running(container_name)


def is_model_initializing(container_name: str, host: str = "127.0.0.1") -> bool:
    """
    A model is initializing when:
        - container is running
        - llmboost serve process IS running
        - the expected port is NOT open yet (derived from ps --port, or defaults to config.LBH_SERVE_PORT)
    """
    if not is_container_running(container_name):
        return False
    running, detected_port = _llmboost_proc_and_port(container_name)
    if not running:
        return False
    port = detected_port or config.LBH_SERVE_PORT
    return not _port_open(host, port, timeout=0.2)


def is_model_ready2serve(
    container_name: str, host: str = "127.0.0.1", port: int | None = None
) -> bool:
    """
    A model is serving when:
        - llmboost serve process is running inside the container AND
        - the TCP port is open on the host
    Port selection: prefer '--port' parsed from the process command. If missing, use provided 'port',
    otherwise default to config.LBH_SERVE_PORT. Host defaults to 127.0.0.1 for local checks.
    """
    running, detected_port = _llmboost_proc_and_port(container_name)
    if not running:
        return False
    eff_port = detected_port or port or config.LBH_SERVE_PORT
    return _port_open(host, eff_port, timeout=0.2)
