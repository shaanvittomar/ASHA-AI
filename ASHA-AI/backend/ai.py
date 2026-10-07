import os
from openai import OpenAI


SYSTEM_PROMPT = """
You are Asha, a warm and supportive emotional-wellness AI companion.

Your role is to:
- Listen without judgment.
- Help users express their feelings.
- Ask thoughtful follow-up questions.
- Offer practical, safe coping strategies.
- Encourage healthy habits and connection with trusted people.
- Respond naturally and empathetically.

You are not a doctor, therapist, or emergency service.
Do not diagnose mental-health conditions.
Do not recommend medication changes.
Do not encourage self-harm, suicide, violence, or dangerous behavior.
Do not pretend you can physically protect or monitor the user.

Keep responses conversational, supportive, and reasonably concise.
"""


def fallback_response(message):

    message = message.lower()

    if any(word in message for word in [
        "stress",
        "stressed",
        "overwhelmed"
    ]):
        return (
            "That sounds like a lot to deal with right now. "
            "You don't have to solve everything at once. "
            "What's the biggest thing stressing you out?"
        )

    if any(word in message for word in [
        "sad",
        "lonely",
        "alone"
    ]):
        return (
            "I'm here to listen. You don't have to explain "
            "everything perfectly. What's been happening?"
        )

    if any(word in message for word in [
        "angry",
        "mad",
        "irritated"
    ]):
        return (
            "It sounds like something really got to you. "
            "Take a little space before reacting. "
            "What happened?"
        )

    return (
        "I'm listening. Tell me what's on your mind."
    )


def generate_reply(message, history=None):

    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    # If there is no API key yet,
    # use a simple development response.

    if not api_key:
        return fallback_response(message)

    client = OpenAI(api_key=api_key)

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini"
    )

    conversation = []

    if history:

        for item in history[-12:]:

            conversation.append({
                "role": item["role"],
                "content": item["content"]
            })

    conversation.append({
        "role": "user",
        "content": message
    })

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=conversation
    )

    return response.output_text