' make_shortcuts.vbs
Dim ws, exePath, smDir, desktopDir
exePath = WScript.Arguments(0)
smDir = WScript.Arguments(1)
desktopDir = WScript.Arguments(2)
Set ws = CreateObject("WScript.Shell")

Dim s1
Set s1 = ws.CreateShortcut(smDir & "\ClipboardManager.lnk")
s1.TargetPath = exePath
s1.WorkingDirectory = Left(exePath, InStrRev(exePath, "\"))
s1.Save

Dim s2
Set s2 = ws.CreateShortcut(desktopDir & "\ClipboardManager.lnk")
s2.TargetPath = exePath
s2.WorkingDirectory = Left(exePath, InStrRev(exePath, "\"))
s2.Save

WScript.Echo "OK"
