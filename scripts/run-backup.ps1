# Daily SQLite backup (scheduled by register-tasks.ps1).
. "$PSScriptRoot\common.ps1"

$code = Invoke-Python @('-m', 'bot.backup')
if ($code -ne 0) { Send-Alert 'Daily database backup failed (see data/runs.log).' }
else { Write-Log 'backup: done' }
