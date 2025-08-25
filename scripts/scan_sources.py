from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict

from util import ensure_dir, latest_manifest, load_config, read_yaml, sha1sum, timestamp, write_yaml


SUPPORTED_EXTS = {".cue", ".iso", ".gdi", ".toc"}


def build_snapshot(config: dict) -> Dict[str, Dict[str, str]]:
    raw_root = Path(config["raw_root"])
    snapshot: Dict[str, Dict[str, str]] = {}
    for system, info in config["systems"].items():
        system_dir = raw_root / info["raw_subdir"]
        files = {}
        for path in system_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTS:
                rel = str(path.relative_to(raw_root))
                files[rel] = sha1sum(path)
        snapshot[system] = files
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Index raw sources and detect changes")
    parser.add_argument("--config", default="config.yml")
    args = parser.parse_args()

    config = load_config(args.config)
    manifest_dir = Path("manifests")
    log_dir = Path("logs")
    ensure_dir(manifest_dir)
    ensure_dir(log_dir)

    log_file = log_dir / f"scan_sources-{timestamp()}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")

    snapshot = build_snapshot(config)
    snapshot_path = manifest_dir / f"sources-{timestamp()}.yml"
    write_yaml(snapshot, snapshot_path)
    logging.info("Wrote snapshot %s", snapshot_path)

    prev_manifest = latest_manifest(manifest_dir, "sources")
    delta: Dict[str, Dict[str, str]] = {}
    if prev_manifest:
        prev = read_yaml(prev_manifest)
        for system, files in snapshot.items():
            prev_files = prev.get(system, {})
            changed = {rel: h for rel, h in files.items() if prev_files.get(rel) != h}
            if changed:
                delta[system] = changed
    else:
        delta = snapshot

    delta_path = manifest_dir / f"delta-{timestamp()}.yml"
    write_yaml(delta, delta_path)
    logging.info("Detected %d systems with changes", len(delta))
    for system, files in delta.items():
        logging.info("%s: %d changed", system, len(files))


if __name__ == "__main__":
    main()
