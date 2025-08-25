# CAB CHD Pipeline

Automates rebuilding and deploying curated CHD collections for an arcade cabinet. The
pipeline is driven by `config.yml` and consists of several scripts found in the
`scripts/` directory.

## Setup

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```
2. Configure paths, systems and playlists in `config.yml`.

## Workflow

1. **Scan sources** – index raw Redump/No-Intro sets and detect changed discs.
   ```
   python scripts/scan_sources.py
   ```
2. **Build CHDs** – run `chdman` only for new/changed sources.
   ```
   python scripts/build_chd.py
   ```
3. **Filter playlists** – read LaunchBox playlists and produce include lists.
   ```
   python scripts/playlist_filter.py
   ```
4. **Deploy curated set** – copy curated CHDs (and optional artwork/media) to the
   cabinet folders.
   ```
   python scripts/deploy_curated.py
   ```
5. **Verify CHDs** *(optional)* – validate built CHDs using `chdman info`.
   ```
   python scripts/verify_chd.py
   ```

Each step writes dated manifests under `manifests/` and logs under `logs/` for
reproducibility.

## Options

Most behaviour (parallel jobs, dry-run, verification, etc.) is controlled via
`config.yml`.
