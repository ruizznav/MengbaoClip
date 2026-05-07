@echo off
cd /d "F:\workbuddy\2026-05-07-task-10"
if not exist "dist_release\MengbaoClip.exe" (
    "C:\Users\13670\.workbuddy\binaries\python\versions\3.13.12\python.exe" -m PyInstaller --clean --onefile --windowed --noconsole --name "MengbaoClip" --distpath "dist_release" --add-data "icon_r.png;." --icon "icon_r.ico" clipboard_single.py
    if errorlevel 1 (pause & exit /b 1)
)
set DEF=%LOCALAPPDATA%\Programs\ClipboardManager
echo Install path [%DEF%]:
set /p "P="
if "%P%"=="" set "P=%DEF%"
if not exist "%P%" mkdir "%P%"
copy /Y "dist_release\MengbaoClip.exe" "%P%\MengbaoClip.exe" >nul
copy /Y "icon_r.png" "%P%\icon_r.png" >nul
set SM=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ClipboardManager
if not exist "%SM%" mkdir "%SM%"
cscript //nologo "%~dp0make_shortcuts.vbs" "%P%\MengbaoClip.exe" "%SM%" "%USERPROFILE%\Desktop"
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipboardManager" /v "DisplayName" /t REG_SZ /d "ClipboardManager v3" /f >nul 2>&1
echo Done.
pause
