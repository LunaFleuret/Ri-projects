$TargetFile = "d:\薫衣りぃ\RAG\run_app.bat"
$ShortcutFile = "$env:USERPROFILE\Desktop\薫衣りぃ検索.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = "d:\薫衣りぃ\RAG"
$Shortcut.IconLocation = "shell32.dll,22"
$Shortcut.Save()
