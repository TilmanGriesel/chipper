document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("message-input").focus();
});

const messageInput = document.getElementById("message-input");
const chatMessages = document.getElementById("chat-messages");
const busyIndicator = document.getElementById("busy-indicator");
const sendButton = document.getElementById("send-button");

marked.setOptions({
  headerIds: false,
  mangle: false,
  breaks: true,
  gfm: true,
  sanitize: false,
  highlight: function (code, lang) {
    if (lang && Prism.languages[lang]) {
      try {
        return Prism.highlight(code, Prism.languages[lang], lang);
      } catch (e) {
        console.error(e);
        return code;
      }
    }
    return code;
  },
});

messageInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

function scrollToBottom(immediate = false) {
  const scroll = () => {
    const container = chatMessages;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  };

  if (immediate) {
    scroll();
  } else {
    setTimeout(scroll, 200);
  }
}

messageInput.addEventListener("input", () => scrollToBottom(false));

function setBusy(busy) {
  busyIndicator.classList.toggle("hidden", !busy);
  messageInput.disabled = busy;
  sendButton.disabled = busy;
  if (busy) {
    sendButton.classList.add("opacity-50", "cursor-not-allowed");
  } else {
    sendButton.classList.remove("opacity-50", "cursor-not-allowed");
  }
}

function createMessageElement(content, type = "chipper", timestamp) {
  const messageContainer = document.createElement("div");
  messageContainer.className =
    "flex " + (type === "user" ? "justify-end" : "justify-start");

  const messageDiv = document.createElement("div");
  messageDiv.className = "p-4 rounded-3xl min-w-48";

  switch (type) {
    case "user":
      messageDiv.classList.add("bg-zinc-900", "text-white", "user-message");
      break;
    case "chipper":
      messageDiv.classList.add("bg-zinc-200", "chipper-message");
      break;
    case "error":
      messageDiv.classList.add("bg-red-600", "text-white", "error-message");
      break;
    case "system":
      messageDiv.classList.add("bg-purple-600", "text-white", "system-message");
      break;
    default:
      messageDiv.classList.add("bg-gray-600");
  }

  const header = document.createElement("div");
  header.className = "font-bold text-sm text-gray-700 mb-2 ";
  if (type === "user") {
    header.className += "sender-user text-white";
    header.textContent = "You";
  } else if (type === "chipper") {
    header.className += "sender-chipper";
    header.textContent = "Chipper";
  } else if (type === "system") {
    header.className += "sender-system text-white";
    header.textContent = "System";
  } else if (type === "error") {
    header.className += "sender-error text-white";
    header.textContent = "Error";
  } else {
    header.textContent = "Message";
  }

  const contentDiv = document.createElement("div");
  contentDiv.className = "prose prose-sm max-w-none";
  contentDiv.innerHTML = marked.parse(content);

  contentDiv.querySelectorAll("pre code").forEach((block) => {
    if (!block.className.includes("language-")) {
      block.className = "language-plaintext";
    }
    Prism.highlightElement(block);
  });

  messageDiv.appendChild(header);
  messageDiv.appendChild(contentDiv);
  messageContainer.appendChild(messageDiv);

  return messageContainer;
}

async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message) return;

  chatMessages.appendChild(createMessageElement(message, "user"));
  messageInput.value = "";
  scrollToBottom(false);

  setBusy(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (data.error) {
      throw new Error(data.error);
    }

    if (data.command_response) {
      data.replies.forEach((reply) => {
        chatMessages.appendChild(createMessageElement(reply, "system"));
        scrollToBottom(false);
      });
    } else if (Array.isArray(data.replies)) {
      data.replies.forEach((reply) => {
        chatMessages.appendChild(createMessageElement(reply, "chipper"));
        scrollToBottom(false);
      });
    } else {
      chatMessages.appendChild(
        createMessageElement("Unexpected response format.", "error")
      );
      scrollToBottom();
    }
  } catch (error) {
    chatMessages.appendChild(
      createMessageElement(`Error: ${error.message}`, "error")
    );
    scrollToBottom();
  } finally {
    setBusy(false);
    scrollToBottom();
  }
}
