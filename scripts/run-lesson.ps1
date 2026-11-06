# Runs one lesson slot. Task Scheduler calls this with the slot time, e.g.:
#   powershell -File run-lesson.ps1 -Slot 11:30
# Manual testing:  -Force (ignore the "too late" rule)  -SkipClaude (send what is already in outbox/lesson.md)
param(
    [Parameter(Mandatory)][string]$Slot,
    [switch]$Force,
    [switch]$SkipClaude
)

. "$PSScriptRoot\common.ps1"
. "$PSScriptRoot\schedule.ps1"

$started   = Get-Date
$scheduled = [datetime]::ParseExact($Slot, 'HH:mm', $null)   # today at that time
$slotId    = $scheduled.ToString('yyyy-MM-ddTHH:mm')
$lateBy    = ($started - $scheduled).TotalMinutes

# 1. Catch-up rule: never deliver a lesson long after its slot.
if (-not $Force -and $lateBy -gt $MaxLateMinutes) {
    Write-Log "[$slotId] skipped: started $([int]$lateBy) min late"
    exit 0
}

# 2. Never send the same slot twice.
if ((Invoke-Python @('-m', 'bot.send_lesson', '--check-slot', $slotId)) -eq 3) {
    Write-Log "[$slotId] skipped: already sent"
    exit 0
}

# 3. One run at a time.
if (-not (Enter-Lock)) {
    Write-Log "[$slotId] skipped: another run still holds the lock"
    exit 0
}

try {
    Write-Log "[$slotId] starting"
    $outbox        = Join-Path $Learning 'outbox\lesson.md'
    $challengeFile = Join-Path $Learning 'outbox\coding-challenge.md'   # hand-off only; moved out of learning/ below
    $isDrill       = ($Slot -eq $DrillSlot)
    $isChallenge   = ($Slot -eq $ChallengeSlot)

    if (-not $SkipClaude) {
        # 4. Pull new Q&A from SQLite into learning/logs/ so Claude can adapt.
        if ((Invoke-Python @('-m', 'bot.export_logs')) -ne 0) {
            Send-Alert "Slot ${Slot}: couldn't export your Q&A logs (see data/runs.log). Continuing without them."
        }

        # 5. Ask Claude for the lesson.
        Remove-Item $outbox -Force -ErrorAction SilentlyContinue   # never send a stale file
        Remove-Item $challengeFile -Force -ErrorAction SilentlyContinue
        $today = Get-Date -Format 'dddd d MMMM yyyy'
        if ($isDrill) {
            $prompt = "Today is $today. This is a drill run: write an interview drill (kind: drill) as described in CLAUDE.md. Follow CLAUDE.md exactly, write outbox/lesson.md and update the memory files."
        } else {
            $prompt = "Today is $today. Run a normal lesson now. Follow CLAUDE.md exactly, write outbox/lesson.md and update the memory files."
        }
        if ($isChallenge) { $prompt += ' Also write coding-challenge.md as described in CLAUDE.md.' }

        $code = Invoke-Claude $prompt
        if ($code -ne 0) {
            Send-Alert "Lesson run failed for slot $Slot (Claude exited with code $code)." $ClaudeOut
            exit 1
        }
    }

    if (-not (Test-Path $outbox)) {
        Send-Alert "Lesson run for slot $Slot finished but no lesson file was written." $ClaudeOut
        exit 1
    }

    # 6. Send to Telegram and record in SQLite.
    $sendCode = Invoke-Python @('-m', 'bot.send_lesson', '--slot', $slotId)
    if ($sendCode -eq 3) { Write-Log "[$slotId] already sent"; exit 0 }
    if ($sendCode -ne 0) {
        Send-Alert "Lesson for slot $Slot was written but couldn't be sent (exit $sendCode). See data/runs.log. It stays in outbox/ for a retry."
        exit 1
    }

    # 7. Coding challenge ping (16:30 slot).
    if ($isChallenge -and -not $SkipClaude) {
        if ((Test-Path $challengeFile) -and ((Get-Item $challengeFile).LastWriteTime -gt $started)) {
            # Keep every day's challenge in its own dated file, outside learning/ so Claude never reads them.
            New-Item -ItemType Directory -Force -Path $ChallengesDir | Out-Null
            $dated = Join-Path $ChallengesDir ("{0}.md" -f $started.ToString('yyyy-MM-dd'))
            Move-Item -Path $challengeFile -Destination $dated -Force
            [void](Invoke-Python @('-m', 'bot.alerts', 'challenge', '--path', "coding-challenges/$($started.ToString('yyyy-MM-dd')).md"))
        } else {
            Send-Alert "Slot ${Slot}: the coding challenge wasn't written today."
        }
    }

    # 8. Back up Claude's memory.
    Backup-Learning "Lesson $slotId"
    Write-Log "[$slotId] done"
} finally {
    Exit-Lock
}
