from __future__ import annotations

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from util import ensure_dir, latest_manifest, load_config, read_yaml, run, timestamp


def chd_command(chdman: str, input_type: str, src: Path, dst: Path) -> list:
    if input_type == "cd":
        return [chdman, "createcd", "-i", str(src), "-o", str(dst)]
    if input_type == "dvd":
        return [chdman, "createdvd", "-i", str(src), "-o", str(dst)]
    if input_type == "gdrom":
        return [chdman, "creategd", "-i", str(src), "-o", str(dst)]
    raise ValueError(f"Unsupported input type {input_type}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build CHDs for changed sources")
    parser.add_argument("--config", default="config.yml")
    parser.add_argument("--delta", help="Path to delta manifest", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    manifest_dir = Path("manifests")
    log_dir = Path("logs")
    ensure_dir(log_dir)

    log_file = log_dir / f"build_chd-{timestamp()}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")

    delta_path = Path(args.delta) if args.delta else latest_manifest(manifest_dir, "delta")
    if not delta_path or not delta_path.exists():
        raise SystemExit("Delta manifest not found")
    delta = read_yaml(delta_path)

    raw_root = Path(config["raw_root"])
    chd_root = Path(config["chd_root"])
    chdman = config["chdman_path"]
    dry_run = config.get("dry_run", False)
    verify = config.get("verify_after_build", False)
    jobs = int(config.get("parallel_jobs", 1))

    tasks = []
    for system, files in delta.items():
        sys_conf = config["systems"][system]
        for rel in files.keys():
            src = raw_root / rel
            dst_dir = chd_root / sys_conf["chd_subdir"]
            ensure_dir(dst_dir)
            dst = dst_dir / (Path(rel).stem + ".chd")
            cmd = chd_command(chdman, sys_conf["input_type"], src, dst)
            tasks.append((system, rel, cmd, dst))

    def worker(task):
        system, rel, cmd, dst = task
        logging.info("Building %s", rel)
        run(cmd, dry_run)
        if verify:
            run([chdman, "info", "-i", str(dst)], dry_run)

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        ex.map(worker, tasks)

    built_manifest = {sys: list(files.keys()) for sys, files in delta.items()}
    out_manifest = manifest_dir / f"built-{timestamp()}.yml"
    ensure_dir(manifest_dir)
    with out_manifest.open("w", encoding="utf-8") as f:
        import yaml
        yaml.safe_dump(built_manifest, f, sort_keys=False)


if __name__ == "__main__":
    main()
