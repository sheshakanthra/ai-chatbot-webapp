// WhatsApp-style chat: bubbles + typing + /get fetch
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("composer");
  const input = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");

  form.addEventListener("submit", (e)=>{ e.preventDefault(); sendMessage(); });
  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e)=>{ if(e.key==="Enter") sendMessage(); });

  // stamp times for any static bubbles on load
  document.querySelectorAll(".msg .meta .time").forEach(el=> el.textContent = now());
});

function now(){
  const d = new Date();
  return d.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"});
}

function appendBubble(sender, text, typing=false){
  const chat = document.getElementById("chat-box");

  const msg = document.createElement("div");
  msg.className = `msg ${sender}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if(typing){
    bubble.innerHTML = `
      <div class="text typing">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>
      <div class="meta"><span class="time">${now()}</span></div>
    `;
  }else{
    bubble.innerHTML = `
      <div class="text"></div>
      <div class="meta"><span class="time">${now()}</span></div>
    `;
    bubble.querySelector(".text").textContent = text;
  }

  msg.appendChild(bubble);
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

async function typeIntoLastBot(text){
  const chat = document.getElementById("chat-box");
  const last = chat.querySelector(".msg.bot:last-child .text");
  if(!last) return;
  last.textContent = "";
  for(const ch of text){
    last.textContent += ch;
    chat.scrollTop = chat.scrollHeight;
    await new Promise(r=>setTimeout(r, 8)); // typing speed
  }
}

async function sendMessage(){
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if(!text) return;

  // user bubble
  appendBubble("user", text);
  input.value = "";

  // bot typing bubble
  appendBubble("bot", "", true);

  try{
    const res = await fetch("/get", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();

    // remove typing
    const chat = document.getElementById("chat-box");
    const typing = chat.querySelector(".msg.bot:last-child");
    if(typing) typing.remove();

    // place a clean bubble and type into it
    appendBubble("bot", "");
    await typeIntoLastBot((data && data.reply) ? data.reply : "Hmm, no reply yet.");
  }catch(err){
    console.error(err);
    const chat = document.getElementById("chat-box");
    const typing = chat.querySelector(".msg.bot:last-child");
    if(typing) typing.remove();
    appendBubble("bot", "❌ Network error. Please try again.");
  }
}
