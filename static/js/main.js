console.log("main.js loaded");

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

let totalMessages = 0;
let toxicMessages = 0;

// Add message bubble to chat UI
function appendMessage(text, label, severity) {
    const div = document.createElement("div");

    div.classList.add("message-bubble");

    if (severity === "high" || severity === "medium") {
        div.classList.add("toxic");
    } else {
        div.classList.add("safe");
    }

    div.innerHTML = `
        <strong>You:</strong> ${text}
        <br>
        <small>${label} (${severity})</small>
    `;

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}


// POST message to Flask
async function analyzeMessage(text) {
    const res = await fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text})
    });

    const data = await res.json();

    if (res.ok) {
        totalMessages++;
        if (data.severity === "medium" || data.severity === "high") {
            toxicMessages++;
        }

        appendMessage(data.message, data.label, data.severity);

        // update side panel
        document.getElementById("label").innerText = data.label;
        document.getElementById("severity").innerText = data.severity;
        document.getElementById("score").innerText = data.score;
        document.getElementById("score-bar").style.width = data.score + "%";

        document.getElementById("total-msg").innerText = totalMessages;
        document.getElementById("toxic-msg").innerText = toxicMessages;

    } else {
        alert(data.error || "Something went wrong!");
    }
}

// SEND button
sendBtn.addEventListener("click", () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    analyzeMessage(text);
});

// ENTER key
input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        sendBtn.click();
    }
});
