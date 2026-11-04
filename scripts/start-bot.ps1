# Starts the Telegram bot. Task Scheduler runs this at logon and restarts it if it crashes.
. "$PSScriptRoot\common.ps1"

Write-Log 'bot: starting'
Push-Location $Root
$prev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    # The bot writes its own rotating log to data/bot.log, so console output is discarded.
    & $Py -m bot.bot 2>&1 | Out-Null
    $code = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $prev
    Pop-Location
}
Write-Log "bot: exited with code $code"

# Exit code 2 = config problem (.env missing values). Restarting can't fix that, so don't loop.
if ($code -eq 2) { exit 0 }
exit $code
