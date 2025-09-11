from random import choice


def get_positive_response() -> str:
    """Return a positive response."""
    return choice(
        [
            "Sure, I can do that.",
            "Sounds good.",
            "Yep.",
            "I'll do it.",
            "Works for me.",
            "👍",
            "Absolutely!",
            "Perfect!",
            "Great idea!",
            "Count me in!",
            "That works!",
            "Yes!",
            "Definitely!",
            "I'm in!",
            "Let's do it!",
            "👍👍",
            "Perfect timing!",
            "Sounds great!",
            "I'm on it!",
            "No problem!",
            "✅",
        ],
    )


def get_negative_response() -> str:
    """Return a negative response."""
    return choice(
        [
            "Sorry, I can't do that.",
            "I'm sorry, I can't do that.",
            "Nope",
            "no",
            "Sorry, I'm busy then.",
            "👎",
            "Can't make it.",
            "Not available.",
            "Sorry, no.",
            "I'm out.",
            "Not this time.",
            "Sorry, I'm booked.",
            "Can't do it.",
            "Not possible.",
            "I'm unavailable.",
            "👎👎",
            "Sorry, I'm swamped.",
            "No can do.",
            "I'm tied up.",
            "Not happening.",
            "❌",
        ],
    )
