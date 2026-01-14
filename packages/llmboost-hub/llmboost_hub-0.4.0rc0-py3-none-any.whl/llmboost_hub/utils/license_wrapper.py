import os
import sys
import logging
from pathlib import Path

# Try importing the internal license checker
from llmboost_hub.utils import license_checker as _license_checker
from llmboost_hub.utils.config import config

log = logging.getLogger("LICENSE_WRAPPER")
logging.basicConfig(level=logging.INFO)


def is_license_valid() -> bool:
    """
    Validate the current license.

    Behavior:
    - Resolves the license file path from config (ENV -> `config.yaml` -> defaults).
    - If the file exists, attempts to validate via the internal checker.
        - On success: returns True.
        - On failure: logs a warning and removes the invalid file.
    - If the file does not exist: logs and returns False.

    Returns:
        True if a valid license is present and verified; False otherwise.
    """
    # Resolve path using config (ENV -> `config.yaml` -> defaults)
    license_path = Path(config.LBH_LICENSE_PATH)

    if license_path.exists():
        log.info(f"Checking existing license at {license_path}...")
        try:
            # Attempt verification via the internal checker
            if _license_checker.validate_license():
                log.info("License is valid.")
                return True
            else:
                # Invalid license; remove file to prevent repeated failures
                log.warning("License invalid or expired.")
                try:
                    license_path.unlink(missing_ok=True)
                except Exception:
                    pass
        except Exception as e:
            # Any unexpected error validating license: surface and bail
            log.error(f"Error validating existing license: {e}")
            print(e, file=sys.stderr)
            return False
    else:
        log.info(f"No license file found at {license_path}.")
    return False


def require_license(func):
    """Decorator for CLI commands that require a valid license."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Gate the wrapped function on the license check
        if not is_license_valid():
            log.error("License required. Please login using `lbh login`.")
            sys.exit(1)
        return func(*args, **kwargs)

    return wrapper


def save_license(path: str, key: str) -> str:
    """
    Write the license key to disk at the specified path with secure permissions.

    Args:
        path: Absolute or relative file path to write the license to.
        key: The license key string; surrounding whitespace will be stripped.

    Returns:
        The absolute path where the license was written.

    Notes:
        Sets file mode to `0o600` (user read/write).
    """
    license_path = Path(path)
    # Ensure containing directory exists
    license_path.parent.mkdir(parents=True, exist_ok=True)
    with open(license_path, "w") as f:
        f.write(key.strip() + "\n")
    # Set file permissions to read/write for user only
    os.chmod(license_path, 0o600)
    return str(license_path)
