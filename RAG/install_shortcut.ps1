$TargetFile = "d:\薫衣りぃ\RAG\run_app.bat"
$ShortcutFile = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\薫衣りぃ検索.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = "d:\薫衣りぃ\RAG"
$Shortcut.IconLocation = "d:\薫衣りぃ\RAG\app.py" 
# Note: Python files don't have icons, but we can just leave it default or point to an ico if we had one. 
# Let's just not set IconLocation to let it use the default batch file icon, or set it to shell32.dll for a generic search icon.
$Shortcut.IconLocation = "shell32.dll,22" 
$Shortcut.Save()

Write-Host "Shortcut created successfully."
Pause
