# Weekly synthesis: compress logs and progress into short digests. Task Scheduler runs this Fridays.
# Manual testing: -Force (run even if this ISO week already ran)
param([switch]$Force)

. "$PSScriptRoot\common.ps1"
. "$PSScriptRoot\schedule.ps1"

Push-Location $Root
$week = (& $Py -m bot.weekly week | Select-Object -First 1).Trim()
Pop-Location

if (-not $Force -and (Invoke-Python @('-m', 'bot.weekly', 'check')) -eq 3) {
    Write-Log "[weekly $week] skipped: already done this week"
    exit 0
}

if (-not (Enter-Lock)) {
    Write-Log "[weekly $week] skipped: another run still holds the lock"
    exit 0
}

try {
    Write-Log "[weekly $week] starting"

    if ((Invoke-Python @('-m', 'bot.export_logs')) -ne 0) {
        Send-Alert "Weekly synthesis ${week}: couldn't export logs first (see data/runs.log). Stopping."
        exit 1
    }

    # Remember which log files this run will digest; only those get deleted afterwards.
    $logsDir  = Join-Path $Learning 'logs'
    $digested = @(Get-ChildItem $logsDir -Filter *.md -ErrorAction SilentlyContinue)
    $archive  = Join-Path $Learning "archive\$week.md"

    $today  = Get-Date -Format 'dddd d MMMM yyyy'
    $prompt = "Today is $today. Run the weekly synthesis exactly as described in weekly-prompt.md. This is ISO week $week, so write the digest to archive/$week.md. Do not write outbox/lesson.md and do not delete files."
    $code = Invoke-Claude $prompt
    if ($code -ne 0) {
        Send-Alert "Weekly synthesis $week failed (Claude exited with code $code)." $ClaudeOut
        exit 1
    }
    if (-not (Test-Path $archive)) {
        Send-Alert "Weekly synthesis ${week} finished but archive/$week.md wasn't written, so raw logs were kept." $ClaudeOut
        exit 1
    }

    # Claude has no shell access, so the script removes the digested raw logs.
    $digested | Remove-Item -Force
    [void](Invoke-Python @('-m', 'bot.weekly', 'mark'))
    Backup-Learning "Weekly synthesis $week"
    Write-Log "[weekly $week] done"
} finally {
    Exit-Lock
}
