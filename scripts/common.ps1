# Shared helpers for run-lesson.ps1 and run-weekly.ps1. Dot-source this file.

$ErrorActionPreference = 'Stop'

$Root      = Split-Path $PSScriptRoot -Parent
$Py        = Join-Path $Root '.venv\Scripts\python.exe'
$Learning  = Join-Path $Root 'learning'
$ChallengesDir = Join-Path $Root 'coding-challenges'   # outside learning/: Claude's memory never includes these
$DataDir   = Join-Path $Root 'data'
$LockFile  = Join-Path $DataDir 'run.lock'
$RunLog    = Join-Path $DataDir 'runs.log'
$ClaudeOut = Join-Path $DataDir 'last-claude-output.txt'

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

function Write-Log([string]$Message) {
    "$(Get-Date -Format 's') $Message" | Add-Content -Path $RunLog -Encoding UTF8
}

# Runs `python <args>` from the repo root, logs its output, returns the exit code.
function Invoke-Python([string[]]$PyArgs) {
    Push-Location $Root
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $Py @PyArgs 2>&1 | ForEach-Object { Write-Log "py: $_" }
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prev
        Pop-Location
    }
    return $code
}

# Sends a failure message to Telegram. Never throws.
function Send-Alert([string]$Reason, [string]$OutputFile = '') {
    Write-Log "ALERT: $Reason"
    $alertArgs = @('-m', 'bot.alerts', 'failure', '--reason', $Reason)
    if ($OutputFile) { $alertArgs += @('--output-file', $OutputFile) }
    try { [void](Invoke-Python $alertArgs) } catch { Write-Log "alert failed: $_" }
}

# One run at a time (lessons and the weekly synthesis share this lock).
# Returns $false if it could not get the lock within the wait time.
function Enter-Lock([int]$WaitMinutes = 10) {
    $deadline = (Get-Date).AddMinutes($WaitMinutes)
    while ($true) {
        if (Test-Path $LockFile) {
            $age = (Get-Date) - (Get-Item $LockFile).LastWriteTime
            if ($age.TotalMinutes -ge 20) { Remove-Item $LockFile -Force -ErrorAction SilentlyContinue }  # stale
        }
        try {
            $fs = [System.IO.File]::Open($LockFile, 'CreateNew', 'Write', 'None')
            $fs.Close()
            return $true
        } catch [System.IO.IOException] {
            if ((Get-Date) -gt $deadline) { return $false }
            Start-Sleep -Seconds 15
        }
    }
}

function Exit-Lock { Remove-Item $LockFile -Force -ErrorAction SilentlyContinue }

# Runs Claude headless in learning/ with tools limited to that folder's files.
# Output goes to data/last-claude-output.txt. Returns claude's exit code.
function Invoke-Claude([string]$Prompt) {
    Push-Location $Learning
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = & claude -p $Prompt --allowedTools Read Write Edit Glob Grep --permission-mode acceptEdits 2>&1 | Out-String
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prev
        Pop-Location
    }
    Set-Content -Path $ClaudeOut -Value $out -Encoding UTF8
    return $code
}

# Commits learning/ and coding-challenges/ (nothing else) and pushes if a remote exists. Failures are logged, not fatal.
function Backup-Learning([string]$Message) {
    if (-not (Test-Path (Join-Path $Root '.git'))) { return }
    Push-Location $Root
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        New-Item -ItemType Directory -Force -Path $ChallengesDir | Out-Null
        git add -- learning coding-challenges 2>&1 | Out-Null
        git diff --cached --quiet -- learning coding-challenges
        if ($LASTEXITCODE -ne 0) {
            git commit -q -m $Message -- learning coding-challenges 2>&1 | ForEach-Object { Write-Log "git: $_" }
        }
        if (git remote) {
            git push -q 2>&1 | ForEach-Object { Write-Log "git: $_" }
            if ($LASTEXITCODE -ne 0) { Write-Log 'git push failed (backup not pushed)' }
        }
    } catch {
        Write-Log "git backup problem: $_"
    } finally {
        $ErrorActionPreference = $prev
        Pop-Location
    }
}
