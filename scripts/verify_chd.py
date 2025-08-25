from __future__ import annotations

import argparse
import logging
from pathlib import Path

from util import ensure_dir, load_config, run, timestamp


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate CHDs with chdman info")
    parser.add_argument("--config", default="config.yml")
    args = parser.parse_args()

    config = load_config(args.config)
    chd_root = Path(config["chd_root"])
    chdman = config["chdman_path"]
    dry_run = config.get("dry_run", False)

    log_dir = Path("logs")
    ensure_dir(log_dir)
    log_file = log_dir / f"verify_chd-{timestamp()}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")

    for path in chd_root.rglob("*.chd"):
        logging.info("Verifying %s", path)
        run([chdman, "info", "-i", str(path)], dry_run)


if __name__ == "__main__":
    main()
