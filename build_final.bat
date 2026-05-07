@echo off
cd /d "F:\workbuddy\2026-05-07-task-10"
"C:\Users\13670\.workbuddy\binaries\python\versions\3.13.12\python.exe" -m PyInstaller --clean --onefile --windowed --noconsole --name "MengbaoClip" --distpath "dist_release" --add-data "icon_r.png;." --icon "icon_r.png" clipboard_single.py
pause
