@echo off
echo Uninstalling ClipboardManager...
taskkill /f /im ClipboardManager.exe >nul 2>&1
ping 127.0.0.1 -n 2 >nul

del "%USERPROFILE%\Desktop\ClipboardManager.lnk" >nul 2>&1
rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\ClipboardManager" >nul 2>&1
rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MengbaoClip" >nul 2>&1
rmdir /s /q "%LOCALAPPDATA%\Programs\ClipboardManager" >nul 2>&1
rmdir /s /q "C:\Program Files\ClipboardManager" >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipboardManager" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\MengbaoClip" /f >nul 2>&1

echo Uninstall complete.
pause
