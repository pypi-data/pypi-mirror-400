import os
import hashlib


def path_has_files(path: str) -> bool:
    """
    Return True if path exists and contains at least one file in the subtree.
    """
    if not os.path.isdir(path):
        return False
    for _, _, files in os.walk(path):
        if files:
            return True
    return False


def dir_size_bytes(path: str) -> int:
    """
    Compute total size in bytes of all files under the given directory (best-effort).
    """
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass
    return total


def sha256_file(path: str, bufsize: int = 1024 * 1024) -> str:
    """
    Compute SHA-256 for a file, streaming in chunks.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()
