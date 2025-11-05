document.addEventListener("DOMContentLoaded", function () {
  const sendBtn = document.getElementById("send-btn");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const form = document.getElementById("composer");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage();
  });

  sendBtn.addEventListener("click", sendMessage);

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      input.value = chip.textContent;
      sendMessage();
    });
  });
});

function addBubble(sender, text, typing = false) {
  const row = document.createElement("div");
  row.className = `msg-row ${sender}`;

  const avatar = `<div class="avatar">${sender === "user" ? "🧑" : "🤖"}</div>`;
  let bubble;

  if (typing) {
    bubble = `
      <div class="bubble">
        <span class="typing">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </span>
      </div>
    `;
  } else {
    bubble = `<div class="bubble">${text}</div>`;
  }

  row.innerHTML = avatar + bubble;
  chatBox.appendChild(row);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function typeReply(text) {
  const chatBox = document.getElementById("chat-box");
  const lastBubble = chatBox.querySelector(".msg-row.bot:last-child .bubble");

  lastBubble.textContent = "";

  for (let char of text) {
    lastBubble.textContent += char;
    chatBox.scrollTop = chatBox.scrollHeight;
    await new Promise(r => setTimeout(r, 10));
  }
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if (!text) return;

  addBubble("user", text);
  input.value = "";

  // Show typing indicator
  addBubble("bot", "", true);

  try {
    const res = await fetch("/get", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });

    const data = await res.json();

    // Remove typing dot bubble
    const chatBox = document.getElementById("chat-box");
    const lastBot = chatBox.querySelector(".msg-row.bot:last-child");
    if (lastBot) lastBot.remove();

    // Add new bubble for reply
    addBubble("bot", "");
    await typeReply(data.reply || "⚠️ No reply");
  } catch (err) {
    console.error(err);

    const chatBox = document.getElementById("chat-box");
    const lastBot = chatBox.querySelector(".msg-row.bot:last-child");
    if (lastBot) lastBot.remove();

    addBubble("bot", "❌ Error — server not responding");
  }
}
