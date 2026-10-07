@echo off
REM Double-click to run on Windows. Requires Python 3 (https://www.python.org/downloads/).
cd /d "%~dp0"
python vimeo_downloader.py %*
pause
