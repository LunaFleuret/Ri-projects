$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("d:\コーディング\薫衣りぃ　原神日数\日数計算.lnk")
$Shortcut.TargetPath = "C:\Windows\System32\cmd.exe"
$Shortcut.Arguments = '/c "d:\コーディング\薫衣りぃ　原神日数\calculate_days.bat"'
$Shortcut.Save()
