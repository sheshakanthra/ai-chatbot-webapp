import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import logging

# Optional OpenAI import (only used if OPENAI_API_KEY is set)
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
if USE_OPENAI:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, static_folder="static", template_folder="templates")

# Basic logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()+"Z"})

@app.route("/get", methods=["POST"])
def get_reply():
    payload = request.get_json(force=True)
    message = payload.get("message", "")
    # Minimal input sanitization
    if not isinstance(message, str):
        return jsonify({"error": "message must be a string"}), 400

    # If OpenAI key present, call ChatCompletion (gpt-3.5/gpt-4 if available)
    if USE_OPENAI:
        try:
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=512,
            )
            reply = resp.choices[0].message.content.strip()
            return jsonify({"reply": reply, "source": "openai"})
        except Exception as e:
            app.logger.exception("OpenAI API error")
            # fallback to rule-based reply
            reply = f"Sorry, OpenAI error occurred. Fallback reply: {fallback_bot_reply(message)}"
            return jsonify({"reply": reply, "source": "fallback", "error": str(e)}), 200

    # Otherwise use local rule-based / simple intent system
    reply = fallback_bot_reply(message)
    return jsonify({"reply": reply, "source": "rule-based"})


def fallback_bot_reply(msg: str) -> str:
    txt = msg.lower().strip()
    if txt == "":
        return "Please type something so I can help you 😊"
    if any(g in txt for g in ["hi", "hello", "hey"]):
        return "Hey there! I'm your chatbot. How can I help you today?"
    if "name" in txt:
        return "I'm Shesh's AI chatbot. You can call me ChatMate!"
    if "help" in txt or "how" in txt:
        return "I can answer simple questions or you can connect me to OpenAI to get smarter. Try asking about building a chatbot!"
    if any(q in txt for q in ["time", "date"]):
        return f"The current server time (UTC) is {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}."
    # small echo + guidance
    if len(txt.split()) <= 3:
        return "Could you give me a bit more detail? For example: 'How to deploy a Flask app?'"
    # default fallback
    return "I'm still learning. Try rephrasing, or enable the OpenAI API key to get a smarter reply."


if __name__ == "__main__":
    # Use port from env for deployment platforms
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")
