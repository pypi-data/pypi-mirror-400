import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import yaml

_DEFAULT_HOME = "~/.llmboost_hub"
_CONFIG_FILENAME = "config.yaml"

log = logging.getLogger("CONFIG")


def expand_path(p: str) -> str:
    """
    Expand a path containing `~` to the user home directory.

    Args:
        p: Path string that may contain a leading `~`.

    Returns:
        The expanded absolute or relative path string.
    """
    return os.path.expanduser(p)


def ensure_home() -> str:
    """
    Ensure `LBH_HOME` exists and return its absolute path.

    Resolution order:
    - ENV `LBH_HOME` (if set)
    - built-in default `~/.llmboost_hub`

    Returns:
        Absolute path to `LBH_HOME` (created if missing).
    """
    home_env = os.getenv("LBH_HOME", _DEFAULT_HOME)
    home = expand_path(home_env)
    os.makedirs(home, exist_ok=True)
    return os.path.abspath(home)


def _get_home() -> str:
    """Internal helper to return `LBH_HOME` (ensures existence)."""
    return ensure_home()


def _config_path() -> str:
    """Absolute path to `config.LBH_HOME`/`config.yaml`."""
    return os.path.join(_get_home(), _CONFIG_FILENAME)


class _Constants:
    # LLMBOOST paths are always inside container
    CONTAINER_LBH_HOME = "/llmboost_hub"  # container lbh home
    CONTAINER_USER_WORKSPACE = "/user_workspace"  # container user workspace mount point
    LLMBOOST_WORKSPACE = "/workspace"  # container workspace dir
    LLMBOOST_MODELS_DIR = f"{LLMBOOST_WORKSPACE}/models"  # container models dir
    LLMBOOST_LOGS_DIR = f"{LLMBOOST_WORKSPACE}/logs"  # container logs dir
    LLMBOOST_LICENSE_PATH = f"{LLMBOOST_WORKSPACE}/license.skm"  # container license path
    LLMBOOST_TUNER_DB_PATH = f"{LLMBOOST_WORKSPACE}/data/inference.db"  # container tuner DB path
    LLMBOOST_TUNER_DB_BACKUP_PATH = (
        f"{LLMBOOST_WORKSPACE}/data/inference.db.bak"  # container tuner DB backup path
    )
    TUNER_DB_BACKUPS_DIRNAME = "tuner_db_backups"  # tuner DB backup dir name (host and container)
    LBH_HELM_RELEASE_NAME = "llmboost"  # Helm release name
    # Kubernetes CRD constants
    KUBE_CRD_GROUP = "mangoboost.io"  # Kubernetes CRD group
    KUBE_CRD_API_VERSION = KUBE_CRD_GROUP + "/v1"  # Kubernetes CRD API version
    KUBE_CRD_KIND = "LLMBoostDeployment"  # Kubernetes CRD kind
    KUBE_CRD_RESOURCE_NAME = "llmboostdeployment"  # Kubernetes CRD resource name
    KUBE_DOCKER_REGISTRY_SECRET_NAME = (
        "docker-registry-key"  # Kubernetes secret name for Docker registry credentials
    )
    KUBE_DOCKER_SERVER = "https://index.docker.io/v1/"  # Docker registry server URL


class _Defaults:
    # LBH is always on host
    LBH_HOME = _get_home()  # host lbh home
    LBH_MODELS = os.path.join(_get_home(), "models")  # host models dir
    LBH_MODELS_STAGING = os.path.join(_get_home(), "models", ".tmp")  # host staging dir
    LBH_LICENSE_PATH = os.path.join(_get_home(), "license.skm")  # host license path
    LBH_WORKSPACE = os.path.join(_get_home(), "workspace")  # host workspace dir
    LBH_LOOKUP_URL = "https://docs.google.com/spreadsheets/d/1f8FTgGDJkI6hnJQsd-RhHtlGhYTx_p8AAvDLNbRRTV8/export?format=csv"  # lookup URL
    LBH_LOOKUP_CACHE = os.path.join(_get_home(), "lookup_cache.csv")  # host lookup cache
    LBH_LOOKUP_CACHE_TTL = 60  # seconds between cache refreshes
    LBH_SERVE_PORT = 8011  # Serve port
    LBH_GUI_PORT = 8080  # GUI port
    LBH_TUNER_DB_PATH = os.path.join(
        _get_home(), f"{os.path.basename(_Constants.LLMBOOST_TUNER_DB_PATH)}"
    )  # host tuner DB path
    LBH_AUTO_PREP = True  # whether to auto-prepare missing models on run
    LBH_HELM_REPO_URL = "https://mangoboost.github.io/llmboost-helm"  # Helm repository URL
    LBH_HELM_REPO_NAME = "llmboost"  # Helm repository name
    LBH_HELM_CHART_NAME = "llmboost"  # Helm chart name
    LBH_KUBE_NAMESPACE = "llmboost"  # Kubernetes namespace
    LBH_CLUSTER_CONFIG_PATH = os.path.join(
        _get_home(), "cluster_config.json"
    )  # Cluster configuration file path
    LBH_KUBE_MODEL_DEPLOYMENTS_PATH = os.path.join(
        _get_home(), "model_deployments"
    )  # Kubernetes model deployment manifests directory
    LBH_MODEL_PATHS = os.path.join(_get_home(), "model_paths.yaml")  # Model paths mapping file
    LBH_DOCKER_CONFIG = os.path.join(
        os.path.expanduser("~"), ".docker", "config.json"
    )  # Docker config file path


# Coerce env/config values to the expected type (handles bools, ints, floats)
def _to_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if s in {"0", "false", "f", "no", "n", "off", ""}:
            return False
    raise ValueError(f"Cannot parse boolean from: {v!r}")


def _coerce_to_type(value: Any, default: Any) -> Any:
    # Note: bool is a subclass of int, so handle bool before int.
    if isinstance(default, bool):
        try:
            return _to_bool(value)
        except Exception:
            return default
    if isinstance(default, int) and not isinstance(default, bool):
        try:
            return int(value)
        except Exception:
            return default
    if isinstance(default, float):
        try:
            return float(value)
        except Exception:
            return default
    return value


class _Config(_Defaults, _Constants):
    _loaded_cfg = None

    @staticmethod
    def _resolve(cfg: Dict, key):
        """
        Resolve a config value for 'key'.

        Resolution order:
            1) Environment variable (if set, even if "0"/"false")
            2) config.yaml (if present, even if False/0)
            3) Defaults (_Defaults)
        """
        # 1) ENV (use presence, not truthiness; coerce type)
        v = os.getenv(key)
        if v is not None:
            return _coerce_to_type(v, getattr(_Defaults, key))

        # 2) config.yaml (do not use truthiness; coerce type)
        if key in cfg:
            val = cfg.get(key)
            if val is not None and val != "":
                return _coerce_to_type(val, getattr(_Defaults, key))

        # 3) update config.yaml with default if missing
        if key not in cfg:
            _write_config({**cfg, key: getattr(_Defaults, key)})
        return getattr(_Defaults, key)

    def __init__(self):
        """Load config on instantiation and populate attributes from resolved values."""
        loaded_cfg = _load_config(create_if_missing=True)
        for key in dir(_Defaults):
            if not key.startswith("_"):
                setattr(self, key, self._resolve(loaded_cfg, key))


def _write_config(cfg: Dict[str, Any]) -> None:
    """
    Write the given config mapping to `config.LBH_HOME`/`config.yaml`.

    Args:
        cfg: Mapping of key -> value to persist.
    """
    path = _config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(cfg, fh, sort_keys=True)


def _load_config(create_if_missing: bool = True) -> Dict[str, Any]:
    """
    Load `config.LBH_HOME`/`config.yaml` with safe defaults.

    Behavior:
    - If file is missing and `create_if_missing=True`: create with defaults and return those defaults.
    - If file exists but is not a mapping: warn and rewrite defaults.
    - On read error: warn and rewrite defaults.

    Args:
        create_if_missing: Whether to create a default config file if missing.

    Returns:
        The loaded config mapping (possibly defaults).
    """
    path = _config_path()
    if not os.path.exists(path):
        if create_if_missing:
            # Bootstrap with defaults
            cfg = {}
            for key in dir(_Defaults):
                if not key.startswith("_"):
                    cfg[key] = getattr(_Defaults, key)
            _write_config(cfg)
            log.info(f"Created default config at {path}")
            return cfg
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
            if not isinstance(data, dict):
                log.warning(f"Config at {path} is not a mapping. Rewriting defaults.")
                cfg = {}
                for key in dir(_Defaults):
                    if not key.startswith("_"):
                        cfg[key] = getattr(_Defaults, key)
                # Note: rewrite defaults to recover from invalid content
                _write_config(data)
            return data
    except Exception as e:
        # Any error reading or parsing: recover by writing defaults
        log.warning(f"Failed to read config at {path}: {e}. Rewriting defaults.")
        cfg = {}
        for key in dir(_Defaults):
            if not key.startswith("_"):
                cfg[key] = getattr(_Defaults, key)
        _write_config(cfg)
        return cfg


config = _Config()
