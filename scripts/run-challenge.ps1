# Weekend coding challenge (no lessons on Saturday/Sunday). Task Scheduler calls this in the morning:
#   powershell -File run-challenge.ps1 -Slot 09:00
# Writes coding-challenges/YYYY-MM-DD.md and pings Telegram, so it's waiting for you all day.
# Manual testing:  -Force (ignore the "too late" and "already written" rules)
param(
    [Parameter(Mandatory)][string]$Slot,
    [switch]$Force
)

. "$PSScriptRoot\common.ps1"
. "$PSScriptRoot\schedule.ps1"

$started   = Get-Date
$scheduled = [datetime]::ParseExact($Slot, 'HH:mm', $null)   # today at that time
$slotId    = $scheduled.ToString('yyyy-MM-ddTHH:mm')
$lateBy    = ($started - $scheduled).TotalMinutes
$dated     = Join-Path $ChallengesDir ('{0}.md' -f $started.ToString('yyyy-MM-dd'))

if (-not $Force -and $lateBy -gt $WeekendMaxLateMinutes) {
    Write-Log "[$slotId] skipped: challenge run started $([int]$lateBy) min late"
    exit 0
}
if (-not $Force -and (Test-Path $dated)) {
    Write-Log "[$slotId] skipped: today's challenge already written"
    exit 0
}
if (-not (Enter-Lock)) {
    Write-Log "[$slotId] skipped: another run still holds the lock"
    exit 0
}

try {
    Write-Log "[$slotId] starting challenge"
    Remove-Item (Join-Path $Learning 'outbox\coding-challenge.md') -Force -ErrorAction SilentlyContinue

    $type   = Get-ChallengeType $started
    $today  = Get-Date -Format 'dddd d MMMM yyyy'
    $prompt = "Today is $today. This is a challenge-only run: write coding-challenge.md as described in CLAUDE.md (type: $type), " +
              "update challenge-track.md, and do not write a lesson or touch the other memory files."

    $code = Invoke-Claude $prompt
    if ($code -ne 0) {
        Send-Alert "Weekend coding challenge failed (Claude exited with code $code)." $ClaudeOut
        exit 1
    }
    if (-not (Publish-Challenge $started)) {
        Send-Alert "Weekend coding challenge run finished but no challenge file was written." $ClaudeOut
        exit 1
    }

    Backup-Learning "Challenge $slotId"
    Write-Log "[$slotId] done"
} finally {
    Exit-Lock
}
