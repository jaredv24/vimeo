#!/usr/bin/env python3
"""
Vimeo Downloader
================

Download Vimeo videos to your computer.

Usage:
    python vimeo_downloader.py                       # interactive: paste URLs when asked
    python vimeo_downloader.py URL [URL ...]         # download one or more videos
    python vimeo_downloader.py URL -q 720            # cap quality at 720p
    python vimeo_downloader.py URL -o ~/Videos       # choose output folder
    python vimeo_downloader.py URL --password secret # password-protected video
    python vimeo_downloader.py URL --referer https://site-where-it-is-embedded.com
    python vimeo_downloader.py URL --cookies-from-browser chrome   # private videos you can view
    python vimeo_downloader.py URL --audio-only      # save just the audio (m4a)

Works with vimeo.com/<id>, unlisted links (vimeo.com/<id>/<hash>),
player.vimeo.com/video/<id>, showcases, channels and user pages.

Under the hood this uses yt-dlp, which is installed automatically on first run.
ffmpeg is recommended (needed to merge the separate video + audio streams
Vimeo serves for most HD videos). Without it, the best single-file version is used.
"""

import argparse
import importlib
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_yt_dlp():
    """Import yt-dlp, installing it with pip if it is missing."""
    try:
        return importlib.import_module("yt_dlp")
    except ImportError:
        print("yt-dlp not found - installing it now (one-time setup)...")
        pip = [sys.executable, "-m", "pip", "install", "--upgrade", "--user"]
        # curl-cffi lets yt-dlp impersonate a browser, which Vimeo often requires.
        if subprocess.call(pip + ["yt-dlp[default,curl-cffi]"]) != 0:
            subprocess.check_call(pip + ["yt-dlp"])
        importlib.invalidate_caches()
        return importlib.import_module("yt_dlp")


def build_format(quality, audio_only, have_ffmpeg):
    if audio_only:
        return "bestaudio[ext=m4a]/bestaudio/best"
    cap = f"[height<={quality}]" if quality else ""
    if have_ffmpeg:
        # Best separate video + audio (merged by ffmpeg), falling back to a single file.
        return f"bestvideo{cap}+bestaudio/best{cap}/best"
    # No ffmpeg: only formats that already contain both video and audio.
    return f"best{cap}[vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]/best"


def progress_hook(d):
    if d["status"] == "downloading":
        pct = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"\r  {pct:>7}  {speed:>12}  ETA {eta:<8}", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\r  downloaded: {Path(d['filename']).name}" + " " * 20)


def parse_args():
    p = argparse.ArgumentParser(description="Download Vimeo videos to your computer.")
    p.add_argument("urls", nargs="*", help="Vimeo video URL(s)")
    p.add_argument(
        "-o", "--output",
        default=str(Path.home() / "Downloads" / "Vimeo"),
        help="folder to save videos in (default: ~/Downloads/Vimeo)",
    )
    p.add_argument("-q", "--quality", type=int, metavar="HEIGHT",
                   help="maximum video height, e.g. 1080, 720, 480 (default: best available)")
    p.add_argument("--password", help="password for password-protected videos")
    p.add_argument("--referer",
                   help="page URL where the video is embedded (for embed-only/domain-restricted videos)")
    p.add_argument("--cookies-from-browser", metavar="BROWSER",
                   help="use your logged-in session from chrome/firefox/edge/safari/brave/opera")
    p.add_argument("--audio-only", action="store_true", help="download audio only")
    p.add_argument("--subs", action="store_true", help="also download subtitles/captions if available")
    p.add_argument("--list-formats", action="store_true", help="show available qualities and exit")
    return p.parse_args()


def main():
    args = parse_args()

    urls = args.urls
    if not urls:
        print("Paste Vimeo URL(s), one per line. Press Enter on an empty line to start.")
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if not line:
                break
            urls.append(line)
    if not urls:
        print("No URLs given. Nothing to do.")
        return 1

    yt_dlp = ensure_yt_dlp()
    have_ffmpeg = shutil.which("ffmpeg") is not None
    if not have_ffmpeg and not args.audio_only:
        print("Note: ffmpeg not found. HD videos may be limited to lower quality.\n"
              "      Install ffmpeg for the best results: https://ffmpeg.org/download.html\n")

    out_dir = Path(args.output).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    opts = {
        "format": build_format(args.quality, args.audio_only, have_ffmpeg),
        "outtmpl": str(out_dir / "%(title)s [%(id)s].%(ext)s"),
        "progress_hooks": [progress_hook],
        "noprogress": True,
        "quiet": True,
        "no_warnings": False,
        "restrictfilenames": False,
        "windowsfilenames": True,
        "ignoreerrors": True,
        "retries": 10,
        "fragment_retries": 10,
    }
    if have_ffmpeg and not args.audio_only:
        opts["merge_output_format"] = "mp4"
    if args.password:
        opts["videopassword"] = args.password
    if args.referer:
        opts["http_headers"] = {"Referer": args.referer}
    if args.cookies_from_browser:
        opts["cookiesfrombrowser"] = (args.cookies_from_browser.lower(),)
    if args.subs:
        opts.update({"writesubtitles": True, "subtitleslangs": ["all"]})
    if args.list_formats:
        opts["listformats"] = True
        opts["quiet"] = False

    failed = []
    with yt_dlp.YoutubeDL(opts) as ydl:
        for url in urls:
            print(f"\n==> {url}")
            try:
                code = ydl.download([url])
                if code:
                    failed.append(url)
            except yt_dlp.utils.DownloadError as e:
                print(f"  error: {e}")
                failed.append(url)

    if args.list_formats:
        return 0
    print(f"\nSaved to: {out_dir}")
    if failed:
        print("\nThese could not be downloaded:")
        for u in failed:
            print(f"  - {u}")
        print("Tips: private video -> --cookies-from-browser chrome; "
              "password -> --password; embedded only -> --referer <page url>")
        return 1
    print("All done!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
