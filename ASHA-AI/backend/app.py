from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from dotenv import load_dotenv
from google import genai

from datetime import timedelta
from collections import Counter
import os


from database import (
    init_db,
    create_user,
    authenticate,
    get_user,

    save_message,
    get_messages,

    save_mood,
    get_moods,

    save_journal,
    get_journals,
    get_journal,
    update_journal,
    delete_journal
)


# ============================================================
# SETUP
# ============================================================

load_dotenv()


app = Flask(__name__)

CORS(app)


app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY",
    "asha-development-secret"
)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)


jwt = JWTManager(app)


# ============================================================
# GEMINI
# ============================================================

gemini_key = os.getenv("GEMINI_API_KEY")

if not gemini_key:
    print("Warning: GEMINI_API_KEY is missing.")


client = None

if gemini_key:
    client = genai.Client(
        api_key=gemini_key
    )


MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# DATABASE
# ============================================================

init_db()


# ============================================================
# BASIC ROUTE
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "message": "ASHA AI backend is running",
        "status": "ok"
    })


# ============================================================
# REGISTER
# ============================================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400


    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")


    if not name:

        return jsonify({
            "error": "Name is required"
        }), 400


    if not email:

        return jsonify({
            "error": "Email is required"
        }), 400


    if not password:

        return jsonify({
            "error": "Password is required"
        }), 400


    if len(password) < 6:

        return jsonify({
            "error": "Password must be at least 6 characters"
        }), 400


    try:

        user_id = create_user(
            name,
            email,
            password
        )

    except Exception as error:

        print("Registration error:", error)

        if "UNIQUE" in str(error).upper():

            return jsonify({
                "error": "Email already registered"
            }), 409


        return jsonify({
            "error": "Could not create account"
        }), 500


    return jsonify({
        "message": "Account created successfully",
        "user_id": user_id
    }), 201


# ============================================================
# LOGIN
# ============================================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    email = data.get("email", "").strip()
    password = data.get("password", "")


    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 400


    user = authenticate(
        email,
        password
    )


    if not user:

        return jsonify({
            "error": "Invalid email or password"
        }), 401


    token = create_access_token(
        identity=str(user["id"])
    )


    return jsonify({

        "message": "Login successful",

        "token": token,

        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }

    }), 200


# ============================================================
# CURRENT USER
# ============================================================

@app.route("/api/me", methods=["GET"])
@jwt_required()
def current_user():

    user_id = int(
        get_jwt_identity()
    )


    user = get_user(
        user_id
    )


    if not user:

        return jsonify({
            "error": "User not found"
        }), 404


    return jsonify({
        "user": user
    }), 200


# ============================================================
# CHAT WITH ASHA
# ============================================================

@app.route("/api/chat", methods=["POST"])
@jwt_required()
def chat():

    user_id = int(
        get_jwt_identity()
    )


    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    message = data.get(
        "message",
        ""
    ).strip()


    if not message:

        return jsonify({
            "error": "Message is required"
        }), 400


    if not client:

        return jsonify({
            "error": "Gemini API key is not configured"
        }), 500


    try:

        # Save user's message

        save_message(
            user_id,
            "user",
            message
        )


        # Ask Gemini

        prompt = f"""
You are ASHA, a mental-awareness and
self-reflection AI companion.

Your role is to help the user:

- understand their emotions
- reflect on their day
- identify thoughts and feelings
- journal
- notice patterns
- handle everyday stress
- think through personal situations
- feel heard and supported

Your personality should be:

- warm
- calm
- non-judgmental
- respectful
- conversational
- emotionally aware

Do not diagnose mental illnesses.

Do not claim to be a therapist,
doctor or psychologist.

Do not make the user dependent on you.

Encourage healthy real-world support
when appropriate.

If the user indicates immediate danger,
self-harm or danger to another person,
encourage them to contact a trusted person
or appropriate emergency services.

Keep normal responses conversational
rather than overly formal.

User message:

{message}
"""


        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )


        ai_message = response.text


        if not ai_message:

            return jsonify({
                "error": "ASHA returned an empty response"
            }), 500


        # Save ASHA response

        save_message(
            user_id,
            "assistant",
            ai_message
        )


        return jsonify({

            "response": ai_message,

            "user_id": str(user_id)

        }), 200


    except Exception as error:

        print("Gemini error:", error)

        return jsonify({
            "error": "Failed to generate ASHA response"
        }), 500


# ============================================================
# CHAT HISTORY
# ============================================================

@app.route("/api/messages", methods=["GET"])
@jwt_required()
def message_history():

    user_id = int(
        get_jwt_identity()
    )


    messages = get_messages(
        user_id
    )


    return jsonify({
        "messages": messages
    }), 200


# ============================================================
# MOOD CHECK-IN
# ============================================================

@app.route("/api/moods", methods=["POST"])
@jwt_required()
def add_mood():

    user_id = int(
        get_jwt_identity()
    )


    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    mood = data.get("mood")
    note = data.get(
        "note",
        ""
    ).strip()


    try:

        mood = int(mood)

    except (ValueError, TypeError):

        return jsonify({
            "error": "Mood must be a number"
        }), 400


    if mood < 1 or mood > 10:

        return jsonify({
            "error": "Mood must be between 1 and 10"
        }), 400


    mood_id = save_mood(
        user_id,
        mood,
        note
    )


    return jsonify({

        "message": "Mood saved successfully",

        "mood_id": mood_id

    }), 201


# ============================================================
# GET MOOD HISTORY
# ============================================================

@app.route("/api/moods", methods=["GET"])
@jwt_required()
def mood_history():

    user_id = int(
        get_jwt_identity()
    )


    moods = get_moods(
        user_id
    )


    return jsonify({
        "moods": moods
    }), 200


# ============================================================
# JOURNAL
# ============================================================

@app.route("/api/journals", methods=["POST"])
@jwt_required()
def add_journal():

    user_id = int(
        get_jwt_identity()
    )


    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    title = data.get(
        "title",
        ""
    ).strip()


    content = data.get(
        "content",
        ""
    ).strip()


    if not content:

        return jsonify({
            "error": "Journal content is required"
        }), 400


    journal_id = save_journal(
        user_id,
        title,
        content
    )


    return jsonify({

        "message": "Journal saved successfully",

        "journal_id": journal_id

    }), 201


# ============================================================
# GET JOURNALS
# ============================================================

@app.route("/api/journals", methods=["GET"])
@jwt_required()
def journal_list():

    user_id = int(
        get_jwt_identity()
    )


    journals = get_journals(
        user_id
    )


    return jsonify({
        "journals": journals
    }), 200


# ============================================================
# GET SINGLE JOURNAL
# ============================================================

@app.route(
    "/api/journals/<int:journal_id>",
    methods=["GET"]
)
@jwt_required()
def journal_details(journal_id):

    user_id = int(
        get_jwt_identity()
    )


    journal = get_journal(
        user_id,
        journal_id
    )


    if not journal:

        return jsonify({
            "error": "Journal not found"
        }), 404


    return jsonify({
        "journal": journal
    }), 200


# ============================================================
# UPDATE JOURNAL
# ============================================================

@app.route(
    "/api/journals/<int:journal_id>",
    methods=["PUT"]
)
@jwt_required()
def edit_journal(journal_id):

    user_id = int(
        get_jwt_identity()
    )


    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    title = data.get(
        "title",
        ""
    ).strip()


    content = data.get(
        "content",
        ""
    ).strip()


    if not content:

        return jsonify({
            "error": "Journal content is required"
        }), 400


    updated = update_journal(
        user_id,
        journal_id,
        title,
        content
    )


    if not updated:

        return jsonify({
            "error": "Journal not found"
        }), 404


    return jsonify({
        "message": "Journal updated successfully"
    }), 200


# ============================================================
# DELETE JOURNAL
# ============================================================

@app.route(
    "/api/journals/<int:journal_id>",
    methods=["DELETE"]
)
@jwt_required()
def remove_journal(journal_id):

    user_id = int(
        get_jwt_identity()
    )


    deleted = delete_journal(
        user_id,
        journal_id
    )


    if not deleted:

        return jsonify({
            "error": "Journal not found"
        }), 404


    return jsonify({
        "message": "Journal deleted successfully"
    }), 200


# ============================================================
# INSIGHTS
# ============================================================

@app.route("/api/insights", methods=["GET"])
@jwt_required()
def insights():

    user_id = int(
        get_jwt_identity()
    )


    moods = get_moods(
        user_id
    )

    journals = get_journals(
        user_id
    )


    # Last 7 mood check-ins

    recent_moods = moods[:7]


    # Most common mood

    common_mood = None


    if recent_moods:

        mood_values = [
            item["mood"]
            for item in recent_moods
        ]

        common_mood = Counter(
            mood_values
        ).most_common(1)[0][0]


    return jsonify({

        "checkins": len(recent_moods),

        "journal_entries": len(journals),

        "common_mood": common_mood,

        "mood_timeline": recent_moods

    }), 200


# ============================================================
# WEEKLY REFLECTION
# ============================================================

@app.route(
    "/api/reflection",
    methods=["GET"]
)
@jwt_required()
def reflection():

    user_id = int(
        get_jwt_identity()
    )


    moods = get_moods(
        user_id
    )

    journals = get_journals(
        user_id
    )


    if not moods:

        return jsonify({

            "ready": False,

            "message":
                "Keep checking in throughout the week."

        }), 200


    mood_values = [
        item["mood"]
        for item in moods[:7]
    ]


    average_mood = round(
        sum(mood_values) /
        len(mood_values),
        1
    )


    return jsonify({

        "ready": True,

        "checkins": len(mood_values),

        "journal_entries":
            len(journals),

        "average_mood":
            average_mood,

        "message":
            "You've taken time to check in with yourself. "
            "Keep noticing your thoughts and feelings "
            "without judging them."

    }), 200


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )