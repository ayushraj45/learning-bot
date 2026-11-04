# Creates the Windows Task Scheduler entries under the folder \LearningBot\ for the current user.
#
#   .\register-tasks.ps1 -DryRun       show what would be created, change nothing
#   .\register-tasks.ps1               create/update all tasks
#   .\register-tasks.ps1 -Unregister   remove all tasks
#
# Tasks (times come from schedule.ps1):
#   Lesson-HHmm   x5 weekdays        run-lesson.ps1
#   Weekly        Friday evening     run-weekly.ps1
#   Backup        daily 21:00        run-backup.ps1
#   Bot           at logon           start-bot.ps1 (restarts on crash)
param(
    [switch]$DryRun,
    [switch]$Unregister
)

. "$PSScriptRoot\schedule.ps1"

$TaskPath = '\LearningBot\'
$User     = "$env:USERDOMAIN\$env:USERNAME"

if ($Unregister) {
    $existing = @(Get-ScheduledTask -TaskPath $TaskPath -ErrorAction SilentlyContinue)
    if ($DryRun) { $existing | ForEach-Object { "Would remove $($_.TaskPath)$($_.TaskName)" }; return }
    $existing | Unregister-ScheduledTask -Confirm:$false
    "Removed $($existing.Count) task(s)."
    return
}

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Warning "'claude' is not on your PATH. Scheduled lessons will fail until it is."
}

function At([string]$hhmm) { [datetime]::ParseExact($hhmm, 'HH:mm', $null) }
function Script-Args([string]$script, [string]$extra = '') {
    $path = Join-Path $PSScriptRoot $script
    "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$path`" $extra".Trim()
}

$weekdays = 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'

# Lessons and the weekly run: wake the laptop, run a missed task as soon as possible after it's available.
$runSettings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -MultipleInstances IgnoreNew
$weeklySettings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) -MultipleInstances IgnoreNew
$backupSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew
# Bot: no time limit; restart every minute if it crashes.
$botSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew `
    -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)

$plan = @()
foreach ($slot in $LessonSlots) {
    $plan += [pscustomobject]@{
        Name     = 'Lesson-' + $slot.Replace(':', '')
        When     = "Mon-Fri at $slot"
        Trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $weekdays -At (At $slot)
        Args     = Script-Args 'run-lesson.ps1' "-Slot $slot"
        Settings = $runSettings
    }
}
$plan += [pscustomobject]@{
    Name = 'Weekly'; When = "$WeeklyDay at $WeeklyTime"
    Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $WeeklyDay -At (At $WeeklyTime)
    Args = Script-Args 'run-weekly.ps1'; Settings = $weeklySettings
}
$plan += [pscustomobject]@{
    Name = 'Backup'; When = 'daily at 21:00'
    Trigger = New-ScheduledTaskTrigger -Daily -At (At '21:00')
    Args = Script-Args 'run-backup.ps1'; Settings = $backupSettings
}
$plan += [pscustomobject]@{
    Name = 'Bot'; When = 'at logon, auto-restart'
    Trigger = New-ScheduledTaskTrigger -AtLogOn -User $User
    Args = Script-Args 'start-bot.ps1'; Settings = $botSettings
}

# Runs as you, only while you are logged on (needed for your Claude sign-in and PATH). No admin rights.
$principal = New-ScheduledTaskPrincipal -UserId $User -LogonType Interactive -RunLevel Limited

foreach ($t in $plan) {
    if ($DryRun) {
        '{0,-14} {1,-26} powershell.exe {2}' -f $t.Name, $t.When, $t.Args
        continue
    }
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $t.Args -WorkingDirectory (Split-Path $PSScriptRoot -Parent)
    [void](Register-ScheduledTask -TaskPath $TaskPath -TaskName $t.Name -Trigger $t.Trigger -Action $action `
        -Settings $t.Settings -Principal $principal -Force)
    "Registered $($t.Name) ($($t.When))"
}

if (-not $DryRun) {
    ''
    'Done. The bot starts at your next logon; to start it now run:'
    "  Start-ScheduledTask -TaskPath '$TaskPath' -TaskName Bot"
}
