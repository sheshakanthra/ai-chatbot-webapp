// script.js
document.addEventListener("DOMContentLoaded", function () {
  const sendBtn = document.getElementById("send-btn");
  const input = document.getElementById("user-input");

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  // Chips click send
  document.querySelectorAll(".chip").forEach(c => {
    c.addEventListener("click", () => {
      input.value = c.textContent;
      sendMessage();
    });
  });
});

// ✅ new addMessage (bubble + avatar)
function addMessage(sender, text, typing = false) {
  const chatBox = document.getElementById("chat-box");

  const row = document.createElement("div");
  row.className = `msg-row ${sender}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = sender === "user" ? "🧑" : "🤖";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (typing) {
    bubble.innerHTML = `
      <span class="typing">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </span>`;
  } else {
    bubble.textContent = text;
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  chatBox.appendChild(row);

  chatBox.scrollTop = chatBox.scrollHeight;
}

// ✅ streaming response typing animation
async function typeReply(fullText) {
  const chatBox = document.getElementById("chat-box");
  const lastBubble = chatBox.querySelector(".msg-row.bot:last-child .bubble");

  lastBubble.textContent = ""; // clear typing dots effect first

  for (let i = 0; i < fullText.length; i++) {
    lastBubble.textContent += fullText[i];
    chatBox.scrollTop = chatBox.scrollHeight;
    await new Promise(res => setTimeout(res, 8)); // typing speed here
  }
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if (!text) return;

  // user bubble
  addMessage("user", text);
  input.value = "";

  // bot typing bubble
  addMessage("bot", "", true);

  try {
    const res = await fetch("/get", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();

    // remove typing bubble
    const chatBox = document.getElementById("chat-box");
    const typingRow = chatBox.querySelector(".msg-row.bot:last-child");
    if (typingRow) typingRow.remove();

    if (data && data.reply) {
      // append empty bubble first (to animate text into it)
      addMessage("bot", "");
      await typeReply(data.reply);
    } else {
      addMessage("bot", "⚠️ No reply from server — try again.");
    }
  } catch (err) {
    console.error(err);
    addMessage("bot", "❌ Server error — check console.");
  }
}
