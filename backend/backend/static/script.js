// script.js
document.addEventListener("DOMContentLoaded", function () {
  const sendBtn = document.getElementById("send-btn");
  const input = document.getElementById("user-input");
  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });
});

function addMessage(sender, text) {
  const chatBox = document.getElementById("chat-box");
  const p = document.createElement("div");
  p.className = "msg " + (sender === "user" ? "user" : "bot");
  p.textContent = text;
  chatBox.appendChild(p);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if (!text) return;

  addMessage("user", text);
  input.value = "";
  addMessage("bot", "⏳ typing...");

  try {
    const res = await fetch("/get", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    // remove last "typing..." message
    const chatBox = document.getElementById("chat-box");
    const nodes = chatBox.querySelectorAll(".msg.bot");
    if (nodes.length) nodes[nodes.length - 1].remove();

    if (data && data.reply) {
      addMessage("bot", data.reply);
    } else {
      addMessage("bot", "No reply from server — try again.");
    }
  } catch (err) {
    console.error(err);
    addMessage("bot", "Error contacting server. Check console.");
  }
}
