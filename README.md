# Vimeo Downloader

A small script that downloads Vimeo videos to your computer as `.mp4` files.

## Setup (one time)

1. Install **Python 3**: https://www.python.org/downloads/ (on Windows, tick "Add Python to PATH").
2. *(Recommended)* Install **ffmpeg** to get full HD/4K with audio:
   - Windows: `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

The script installs `yt-dlp` (the download engine) automatically the first time it runs.

## Usage

**Easiest:** double-click `download_vimeo.bat` (Windows) or `download_vimeo.command` (macOS),
paste one or more Vimeo links, then press Enter on an empty line.

**Command line:**

```bash
python vimeo_downloader.py https://vimeo.com/123456789
python vimeo_downloader.py URL1 URL2 URL3            # several at once
python vimeo_downloader.py URL -q 720                # max 720p
python vimeo_downloader.py URL -o "D:\Videos"        # custom folder
python vimeo_downloader.py URL --audio-only          # audio only
python vimeo_downloader.py URL --subs                # include captions
python vimeo_downloader.py URL --list-formats        # see available qualities
```

Videos are saved to `Downloads/Vimeo` unless you choose another folder with `-o`.

### Restricted videos

| Situation | Option |
|---|---|
| Password-protected | `--password THEPASSWORD` |
| Only plays embedded on a certain website | `--referer https://that-website.com/page` |
| Private video you can watch when logged in | `--cookies-from-browser chrome` (or `firefox`, `edge`, `safari`, `brave`) |

### Troubleshooting

- **Errors after it used to work:** Vimeo changes its site regularly. Update the engine:
  `python -m pip install -U "yt-dlp[default,curl-cffi]"`
- **Video has no sound / low quality:** install ffmpeg (see Setup).

## Note

Only download videos you own, that are offered for download, or that you otherwise have
permission to save. Respect creators' rights and Vimeo's Terms of Service.
DRM-protected content (e.g. Vimeo OTT / paid streaming services) is not supported.
