from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Set

from lxml import etree

from util import ensure_dir, load_config, timestamp, write_yaml


def parse_playlist(path: Path) -> Set[str]:
    tree = etree.parse(str(path))
    names: Set[str] = set()
    for node in tree.findall(".//Game/ApplicationPath"):
        if node.text:
            name = Path(node.text).name
            if name.lower().endswith(".chd"):
                names.add(name)
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse LaunchBox playlists")
    parser.add_argument("--config", default="config.yml")
    args = parser.parse_args()

    config = load_config(args.config)
    manifest_dir = Path("manifests")
    log_dir = Path("logs")
    ensure_dir(manifest_dir)
    ensure_dir(log_dir)

    log_file = log_dir / f"playlist_filter-{timestamp()}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")

    launchbox_root = Path(config["launchbox_root"])
    playlists = set()
    for name in config.get("playlists", []):
        path = launchbox_root / "Playlists" / f"{name}.xml"
        if path.exists():
            logging.info("Parsing %s", path)
            playlists.update(parse_playlist(path))
        else:
            logging.warning("Playlist not found: %s", path)

    out_path = manifest_dir / f"curated-{timestamp()}.yml"
    write_yaml(sorted(playlists), out_path)
    logging.info("Wrote %s entries to %s", len(playlists), out_path)


if __name__ == "__main__":
    main()
