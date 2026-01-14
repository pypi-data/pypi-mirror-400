from enum import Enum

class Action(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"
    BAN = "BAN"

def decide_action(score: float) -> Action:
    """
    Decide moderation action based on NSFW confidence score.
    """
    if score >= 0.90:
        return Action.BAN
    elif score >= 0.75:
        return Action.BLOCK
    elif score >= 0.60:
        return Action.WARN
    return Action.ALLOW
