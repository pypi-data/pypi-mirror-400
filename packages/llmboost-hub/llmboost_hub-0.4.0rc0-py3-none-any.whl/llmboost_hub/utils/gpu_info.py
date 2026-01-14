# Copyright 2024, MangoBoost, Inc. All rights reserved.

import subprocess
import re
import math
from collections import defaultdict


def get_nvidia_gpus():
    """
    Detects available NVIDIA GPUs using `nvidia-smi`.
    Returns list like ['NVIDIA_A100-SXM4_40'].
    """
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            encoding="utf-8",
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    gpus = []
    for line in output.strip().splitlines():
        name, mem = [x.strip() for x in line.split(",")]
        mem_gb = int(mem) // 1024
        name_clean = re.sub(r"^(NVIDIA-)+", "", name.replace(" ", "-"), flags=re.IGNORECASE)
        name_clean = re.sub(r"-\d+GB", "", name_clean, flags=re.IGNORECASE)
        gpus.append(f"NVIDIA_{name_clean}_{mem_gb}")

    return gpus


def get_amd_gpus():
    """
    Detects available AMD GPUs using `rocm-smi`.
    Returns list like ['AMD_MI300X_128'].
    """
    amd_gpu_map = {
        "0x74a5": "MI325X",
        "0x74a1": "MI300X",
        "0x74a0": "MI300A",
        "0x7408": "MI250X",
        "0x740c": "MI250X/MI250",
        "0x740f": "MI210",
        "0x6860": "MI25/MI25x2/V340/V320",
        "0x7551": "Radeon9700",
    }

    try:
        output = subprocess.check_output(
            ["rocm-smi", "--showproductname", "--showmeminfo", "vram"],
            encoding="utf-8",
            errors="ignore",
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    gpus = defaultdict(dict)
    current_gpu = None

    for line in output.splitlines():
        gpu_match = re.match(r"GPU\[(\d+)\]", line)
        if gpu_match:
            current_gpu = int(gpu_match.group(1))

        if current_gpu is None:
            continue

        if "VRAM Total Memory (B):" in line:
            mem_match = re.search(r"VRAM Total Memory \(B\):\s*(\d+)", line)
            if mem_match:
                gpus[current_gpu]["vram_bytes"] = int(mem_match.group(1))

        if "Card Model:" in line:
            model_match = re.search(r"0x[0-9a-fA-F]+", line)
            if model_match:
                gpus[current_gpu]["model_id"] = model_match.group(0).lower()

    results = []
    for gpu_index, info in sorted(gpus.items()):
        model_id = info.get("model_id", "unknown")
        model_name = amd_gpu_map.get(model_id, f"UnknownGPU_{model_id}")
        vram_bytes = info.get("vram_bytes", 0)
        vram_gb = math.ceil(vram_bytes / (1024**3)) if vram_bytes else 0
        results.append(f"AMD_{model_name}_{vram_gb}")

    return results


def get_gpus():
    """Return a list of all detected GPUs in the format <VENDOR>_<MODEL>_<SIZE>."""
    return get_nvidia_gpus() + get_amd_gpus()


def get_gpu_count() -> int:
    """Return the number of detected GPUs."""
    return len(get_gpus())


def gpu_name2family(s: str) -> str:
    """
    Normalize various GPU strings to a comparable 'family' token, e.g.:
        - 'AMD_MI300X_192' -> 'MI300X'
        - 'NVIDIA A100-SXM4-80GB' -> 'A100'
        - 'RTX4090' -> 'RTX4090'
    """
    s = str(s or "").strip()
    s = re.sub(r"^(NVIDIA|AMD)[ _-]*", "", s, flags=re.IGNORECASE)  # drop vendor
    s = re.sub(r"[_ -]?\d+GB$", "", s, flags=re.IGNORECASE)  # drop trailing GB suffix
    s = re.sub(r"[_-]\d+$", "", s)  # drop trailing _<mem>
    # take the first token split by space/underscore/hyphen
    token = re.split(r"[ _-]+", s)[0]
    return token.upper()


def get_curr_gpu_size():
    """Return the VRAM size (in GB) of the first detected GPU."""
    try:
        output = subprocess.check_output(
            ["rocm-smi", "--showmeminfo", "vram"], text=True, stderr=subprocess.DEVNULL
        )
        match = re.search(r"VRAM Total Memory \(B\):\s*(\d+)", output)
        if match:
            mem_bytes = int(match.group(1))
            return round(mem_bytes / (1024**3))
    except Exception:
        pass

    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        mem_mb = int(output.strip().split("\n")[0])
        return round(mem_mb / 1024)
    except Exception:
        pass

    raise ValueError("No GPU detected or unsupported platform for VRAM query.")


def get_curr_gpu_name():
    """Return the GPU model name of the first detected GPU."""
    try:
        output = subprocess.check_output(["rocminfo"], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            if "Marketing Name:" in line:
                return line.split(":", 1)[1].strip()
    except Exception:
        pass

    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name",
                "--format=csv,noheader",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return output.strip().split("\n")[0]
    except Exception:
        pass

    try:
        output = subprocess.check_output(["lspci"], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            if any(x in line for x in ["VGA", "3D controller", "Processing accelerators"]):
                return line.split(":")[-1].strip()
    except Exception:
        pass

    raise ValueError("No GPU detected or unsupported platform for name query.")


def any_gpu_in_use() -> bool:
    """
    Return True if any detected GPU shows non-zero compute or VRAM usage.

    NVIDIA:
        - Uses nvidia-smi to check utilization.gpu (%), utilization.memory (%), and memory.used (MiB).
    AMD:
        - Uses rocm-smi to check GPU use (%) and VRAM Used (B).
    """
    # NVIDIA check
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,utilization.memory,memory.used",
                "--format=csv,noheader,nounits",
            ],
            encoding="utf-8",
            stderr=subprocess.DEVNULL,
        )
        for line in output.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                util_gpu = int(parts[0] or 0)
                util_mem = int(parts[1] or 0)
                mem_used = int(parts[2] or 0)
                if util_gpu > 0 or util_mem > 0 or mem_used > 0:
                    return True
    except Exception:
        pass

    # AMD compute usage (%)
    try:
        out_use = subprocess.check_output(
            ["rocm-smi", "--showuse"],
            encoding="utf-8",
            errors="ignore",
            stderr=subprocess.DEVNULL,
        )
        # Look for lines like "GPU use (%): 12"
        for line in out_use.splitlines():
            m = re.search(r"GPU use\s*\(%\)\s*:\s*(\d+)", line, flags=re.IGNORECASE)
            if m and int(m.group(1)) > 0:
                return True
    except Exception:
        pass

    # AMD VRAM used (bytes)
    try:
        out_mem = subprocess.check_output(
            ["rocm-smi", "--showmeminfo", "vram"],
            encoding="utf-8",
            errors="ignore",
            stderr=subprocess.DEVNULL,
        )
        for line in out_mem.splitlines():
            m = re.search(r"VRAM Used \(B\):\s*(\d+)", line)
            if m and int(m.group(1)) > 0:
                return True
    except Exception:
        pass

    return False
