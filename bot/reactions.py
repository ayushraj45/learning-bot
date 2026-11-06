"""What each Telegram reaction means. To teach the bot a new emoji, add one line here.

Reactions are about DEPTH on the lesson's concept, not about how many lessons you get.
The meaning text is written into the log export, so Claude reads it before each lesson.
"""
from __future__ import annotations

REACTIONS: dict[str, str] = {
    "👍": "got it - go deeper / harder on this concept next time",
    "👎": "did not get it - make this concept easier and explain it differently",
}


def pick_reaction(new_reaction: list[dict]) -> str | None:
    """Reduce Telegram's `new_reaction` list to the one emoji we store.

    Empty list (reaction removed), or only emoji we have no meaning for, gives None.
    If several known emoji are present (Telegram Premium allows more than one),
    the first one wins.
    """
    for item in new_reaction:
        if item.get("type") == "emoji" and item.get("emoji") in REACTIONS:
            return item["emoji"]
    return None
