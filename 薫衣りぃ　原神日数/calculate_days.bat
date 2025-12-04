@echo off
chcp 65001 > nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "$start = Get-Date '2023-12-16'; $end = Get-Date; $days = ($end - $start).Days + 1; Write-Host ('2023年12月16日から今日(' + $end.ToString('yyyy年MM月dd日') + ')までの日数:毎日ログインしてたら' + $days + '日')"
pause
