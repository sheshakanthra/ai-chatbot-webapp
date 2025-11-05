import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import logging

# Absolute base dir so Flask knows correct static & template folders on Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)

# Optional OpenAI import (only used if OPENAI_API_KEY is set)
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
if USE_OPENAI:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

# Logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat() + "Z"})

@app.route("/get", methods=["POST"])
def get_reply():
    payload = request.get_json(force=True)
    message = payload.get("message", "").strip()

    if not isinstance(message, str):
        return jsonify({"error": "message must be a string"}), 400

    # Use OpenAI, else fallback
    if USE_OPENAI:
        try:
            resp = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=512,
            )
            reply = resp["choices"][0]["message"]["content"].strip()
            return jsonify({"reply": reply, "source": "openai"})
        except Exception as e:
            app.logger.exception("OpenAI API error")
            reply = f"Sorry, OpenAI error happened. Fallback reply: {fallback_bot_reply(message)}"
            return jsonify({"reply": reply, "source": "fallback", "error": str(e)})

    reply = fallback_bot_reply(message)
    return jsonify({"reply": reply, "source": "rule-based"})


def fallback_bot_reply(msg: str) -> str:
    txt = msg.lower().strip()

    # Common replies
    if txt in ["", "?", "??"]:
        return "Please type something so I can respond 😊"
    if any(g in txt for g in ["hi", "hello", "hey", "yo", "sup"]):
        return "Hey there 👋! How can I help you today?"
    if "how are you" in txt:
        return "I'm doing great 😄 Thanks for asking! What about you?"
    if "your name" in txt or "who are you" in txt:
        return "I'm ChatMate 🤖 — an AI built by **Shesh**!"
    if "who created you" in txt or "who made you" in txt:
        return "I was created by **Shesh**, the coding legend 😎"
    if "help" in txt:
        return "Sure 😃! Ask me anything — facts, concepts, study questions, coding help, etc."

    # Facts (offline mini brain 🧠)
    facts = {
        # Tech & AI
        "elon musk": "Elon Musk is the CEO of SpaceX & Tesla, and founder of Neuralink & The Boring Company.",
        "ai": "AI means Artificial Intelligence — machines that can think/learn like humans.",
        "machine learning": "Machine learning is a way computers learn from data without explicit programming.",
        "python": "Python is a powerful and easy programming language used in AI, web, automation and more.",
        "flask": "Flask is a lightweight Python web framework for building web apps & APIs.",
        "github": "GitHub is a platform for hosting and collaborating on code using Git.",
        "cloud computing": "Cloud computing allows apps and data to run on remote servers instead of your device.",
        "api": "An API lets different software programs communicate with each other.",

        # Programming basics
        "frontend": "Frontend is the part of a website you see — built with HTML, CSS, JS.",
        "backend": "Backend is the server-side — handles logic, database, APIs.",
        "algorithm": "An algorithm is a step-by-step method to solve a problem.",

        # Study / knowledge
        "internet": "The internet is a global network connecting millions of computers.",
        "database": "A database is a system that stores and manages data.",

        # Basic life responses
        "weather": "I can’t check live weather now 🌤️, but Google Weather or your phone can!",
        "time": "Check your system clock 🕒 — it's always right!",
        "date": "Today's date is shown on your device calendar 📅.",

        # Fun
        "joke": "🤣 Here's one: Why do programmers prefer dark mode? Because light attracts bugs!",
        "motivation": "Believe in yourself 💪 Every master was once a beginner.",
    }

    for key, val in facts.items():
        if key in txt:
            return val

    # Extra flexible small talk
    if "thanks" in txt or "thank you" in txt:
        return "You're welcome! 😊 Happy to help!"
    if "who am i" in txt:
        return "You're an awesome human chatting with me 😎"
    if "joke" in txt:
        return "😂 Why don’t programmers go outside? Too many bugs in the wild!"

    # Default fallback
    return "Hmm 🤔 I'm not sure about that yet, but I'm learning every day!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")
