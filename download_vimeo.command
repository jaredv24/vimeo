#!/bin/bash
# Double-click to run on macOS (or run ./download_vimeo.command on Linux).
cd "$(dirname "$0")"
python3 vimeo_downloader.py "$@"
