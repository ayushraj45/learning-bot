# Single source of truth for the daily schedule (UK local time, weekdays).
# Dot-sourced by run-lesson.ps1 and, in Phase 4, register-tasks.ps1.
# Edit the times here; re-run register-tasks.ps1 afterwards to update Task Scheduler.

$LessonSlots   = @('09:00', '11:30', '14:00', '16:30', '19:00')
$DrillSlot     = '19:00'   # this slot asks for an interview drill instead of a lesson
$ChallengeSlot = '16:30'   # this slot also writes coding-challenge.md and pings Telegram
$MaxLateMinutes = 60       # a run later than this after its slot is skipped, not sent late

$WeeklyDay  = 'Friday'
$WeeklyTime = '20:30'
