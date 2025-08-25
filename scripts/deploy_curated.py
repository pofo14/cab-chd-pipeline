from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path

from util import ensure_dir, latest_manifest, load_config, read_yaml, timestamp


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy curated CHDs and media to cab")
    parser.add_argument("--config", default="config.yml")
    parser.add_argument("--curated", help="Path to curated manifest", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    manifest_dir = Path("manifests")
    log_dir = Path("logs")
    ensure_dir(log_dir)

    log_file = log_dir / f"deploy_curated-{timestamp()}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")

    curated_path = Path(args.curated) if args.curated else latest_manifest(manifest_dir, "curated")
    if not curated_path or not curated_path.exists():
        raise SystemExit("Curated manifest not found")
    curated = set(read_yaml(curated_path))

    chd_root = Path(config["chd_root"])
    cab_games_root = Path(config["cab_games_root"])
    cab_media_root = Path(config["cab_media_root"])
    launchbox_root = Path(config["launchbox_root"])
    dry_run = config.get("dry_run", False)

    for system, info in config["systems"].items():
        src_dir = chd_root / info["chd_subdir"]
        dst_dir = cab_games_root / info["chd_subdir"]
        ensure_dir(dst_dir)
        for name in curated:
            src_file = src_dir / name
            if src_file.exists():
                dst_file = dst_dir / name
                logging.info("Copying %s", src_file)
                if dry_run:
                    print("DRY RUN copy", src_file, dst_file)
                else:
                    shutil.copy2(src_file, dst_file)
                # optional media
                media_src = launchbox_root / "Images" / info["chd_subdir"] / src_file.stem
                media_dst = cab_media_root / info["chd_subdir"] / src_file.stem
                if media_src.exists():
                    ensure_dir(media_dst.parent)
                    if dry_run:
                        print("DRY RUN copytree", media_src, media_dst)
                    else:
                        shutil.copytree(media_src, media_dst, dirs_exist_ok=True)


if __name__ == "__main__":
    main()
