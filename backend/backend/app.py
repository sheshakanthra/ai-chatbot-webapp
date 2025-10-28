import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import logging

# Optional OpenAI import (only used if OPENAI_API_KEY is set)
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
if USE_OPENAI:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

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
    
    if not isinstance(message, str):
        return jsonify({"error": "message must be a string"}), 400

    # If OpenAI key present, use GPT model
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
            reply = f"Sorry, OpenAI error occurred. Fallback reply: {fallback_bot_reply(message)}"
            return jsonify({"reply": reply, "source": "fallback", "error": str(e)}), 200

    # Otherwise, use local rule-based chatbot
    reply = fallback_bot_reply(message)
    return jsonify({"reply": reply, "source": "rule-based"})


def fallback_bot_reply(msg: str) -> str:
    txt = msg.lower().strip()

    if txt == "":
        return "Please type something so I can help you 😊"
    if any(g in txt for g in ["hi", "hello", "hey"]):
        return "Hey there! I'm your chatbot. How can I help you today?"
    if "name" in txt:
        return "I'm Shesh's AI chatbot — you can call me ChatMate!"
    if "help" in txt or "how" in txt:
        return "I can chat with you or answer simple facts. Try asking 'who is Elon Musk' or 'what is AI'."
    if "time" in txt or "date" in txt:
        return f"The current server time (UTC) is {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}."

    # Simple fact-based mini-knowledge base (free!)
    facts = {
        "elon musk": "Elon Musk is the CEO of SpaceX and Tesla, and the founder of companies like Neuralink and The Boring Company.",
        "ai": "AI stands for Artificial Intelligence — it means machines that can learn and make decisions like humans.",
        "flask": "Flask is a lightweight Python web framework used to build web apps and APIs easily.",
        "python": "Python is a popular programming language known for its simplicity and power.",
        "render": "Render is a cloud platform that lets you deploy web apps easily, just like your chatbot!",
        "machine learning": "Machine learning is a branch of AI where computers learn from data without being explicitly programmed.",
        "openai": "OpenAI is a research company that creates powerful AI models like GPT-4, which can understand and generate human-like text.",
        "github": "GitHub is a platform for hosting and collaborating on code repositories using Git."
    }

    for key, val in facts.items():
        if key in txt:
            return val

    # Default fallback
    return "Hmm, I don't have info on that yet — but I’m always learning! Try asking something else 😊"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")
