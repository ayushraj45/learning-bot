# Single source of truth for the daily schedule (UK local time, weekdays).
# Dot-sourced by run-lesson.ps1 and, in Phase 4, register-tasks.ps1.
# Edit the times here; re-run register-tasks.ps1 afterwards to update Task Scheduler.

$LessonSlots   = @('09:00', '11:30', '14:00', '16:30', '19:00')
$DrillSlot     = '19:00'   # this slot asks for an interview drill instead of a lesson
$ChallengeSlot = '16:30'   # this slot also writes coding-challenge.md and pings Telegram
# Interview sprint (until the Java/React interview): which track each weekday slot teaches.
# AI once a day; everything else Java/Spring/React. The drill slot picks Java or React itself.
$SlotTracks = @{
    '09:00' = 'java'    # core Java and backend
    '11:30' = 'ai'      # the one daily AI lesson
    '14:00' = 'java'    # Java / Spring
    '16:30' = 'react'   # React and frontend
    '19:00' = 'java or react (your pick: whichever was taught less recently, or a weak spot)'   # drill
}
$MaxLateMinutes = 60       # a run later than this after its slot is skipped, not sent late

# Weekend: no lessons, just the coding challenge, ready in the morning to do any time that day.
$WeekendChallengeDays = @('Saturday', 'Sunday')
$WeekendChallengeTime = '09:00'
$WeekendMaxLateMinutes = 480   # still worth writing if the laptop wakes up late (until 17:00)
$PracticalChallengeDay = 'Sunday'   # Spring Boot practical task
$ReactChallengeDay     = 'Saturday' # React component/hooks task; weekdays are NeetCode problems in Java

$WeeklyDay  = 'Friday'
$WeeklyTime = '20:30'
