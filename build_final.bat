@echo off
cd /d "G:\私人文件\开发\萌宝剪贴板"
"C:\Users\13670\.workbuddy\binaries\python\versions\3.13.12\python.exe" -m PyInstaller --clean --onefile --windowed --noconsole --name "MengbaoClip" --distpath "dist_release" --add-data "icon_r.png;." --icon "icon_r.png" clipboard_single.py
pause
