HIGH_RISK_PHRASES = [
    "kill myself",
    "killing myself",
    "suicide",
    "suicidal",
    "end my life",
    "ending my life",
    "want to die",
    "i want to die",
    "wish i was dead",
    "take my own life",
    "hurt myself",
    "harm myself",
    "self harm",
    "self-harm"
]


def assess_risk(text):

    text = " ".join(text.lower().split())

    for phrase in HIGH_RISK_PHRASES:

        if phrase in text:
            return "high"

    return "low"


def safety_response():

    return (
        "I'm really sorry you're dealing with something this "
        "heavy. I'm here to listen, but I can't safely handle "
        "an immediate crisis on my own. Please reach out to "
        "someone you trust who can stay with you and contact "
        "your local emergency or crisis service if you may "
        "act on these thoughts. Are you in immediate danger "
        "right now?"
    )