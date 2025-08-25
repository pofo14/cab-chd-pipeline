from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml


def load_config(config_path: str = "config.yml") -> dict:
    """Load YAML configuration file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def sha1sum(path: Path, chunk_size: int = 1 << 20) -> str:
    """Compute SHA1 hash for a file."""
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_yaml(data: dict, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(cmd: List[str], dry_run: bool = False) -> subprocess.CompletedProcess:
    """Run a command returning CompletedProcess. Honors dry-run."""
    if dry_run:
        print("DRY RUN:", " ".join(cmd))
        return subprocess.CompletedProcess(cmd, 0, b"", b"")
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def latest_manifest(manifest_dir: Path, prefix: str) -> Optional[Path]:
    """Return latest manifest file matching prefix."""
    files = sorted(manifest_dir.glob(f"{prefix}-*.yml"))
    return files[-1] if files else None
