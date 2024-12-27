document.addEventListener("DOMContentLoaded", () => {
  const messageInput = document.getElementById("message-input");
  const chatMessages = document.getElementById("chat-messages");
  const busyIndicator = document.getElementById("busy-indicator");
  const sendButton = document.getElementById("send-button");

  let conversationHistory = [];
  let currentIndex = "default";
  let currentModel = "llama3.2";

  messageInput.focus();

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
    immediate ? scroll() : setTimeout(scroll, 200);
  }

  messageInput.addEventListener("input", () => scrollToBottom(false));

  function setBusy(busy) {
    busyIndicator.classList.toggle("hidden", !busy);
    messageInput.disabled = busy;
    sendButton.disabled = busy;
    sendButton.classList.toggle("opacity-50", busy);
    sendButton.classList.toggle("cursor-not-allowed", busy);
  }

  function handleCommand(message) {
    const parts = message.split(" ");
    if (parts[0] === "/help") {
      return {
        type: "system",
        content: `### Available Commands

\`/index [name]\` - Switch knowledge base index
\`/model [name]\` - Change AI model
\`/help\` - Show this help message

### Chat Controls
- Press Enter to send message`,
      };
    }
    if (parts[0] === "/index") {
      currentIndex = parts[1] || "default";
      return { type: "system", content: `Index set to: ${currentIndex}` };
    }
    if (parts[0] === "/model") {
      currentModel = parts[1] || "llama3.2";
      return { type: "system", content: `Model set to: ${currentModel}` };
    }
    return null;
  }

  function createMessageElement(content, type = "chipper") {
    const messageContainer = document.createElement("div");
    messageContainer.className = `flex ${
      type === "user" ? "justify-end" : "justify-start"
    } mb-4`;

    const messageDiv = document.createElement("div");
    messageDiv.className = "p-4 rounded-3xl min-w-48 max-w-lg";

    const typeClasses = {
      user: "bg-zinc-900 text-white user-message",
      chipper: "bg-zinc-200 chipper-message",
      error: "bg-red-600 text-white error-message",
      system: "bg-purple-600 text-white system-message",
    };
    messageDiv.classList.add(
      ...(typeClasses[type]?.split(" ") || ["bg-gray-600"])
    );

    const header = document.createElement("div");
    header.className = `font-bold text-sm ${
      type === "chipper" ? "text-zinc-800" : "text-white"
    } mb-2`;
    header.textContent =
      {
        user: "You",
        chipper: "Chipper",
        system: "System",
        error: "Error",
      }[type] || "Message";

    const contentDiv = document.createElement("div");
    contentDiv.innerHTML =
      type === "system" ? marked.parse(content) : marked.parseInline(content);
    contentDiv.className = "prose prose-sm max-w-none break-words";

    messageDiv.appendChild(header);
    messageDiv.appendChild(contentDiv);
    messageContainer.appendChild(messageDiv);

    return { container: messageContainer, message: contentDiv };
  }

  async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    const commandResult = handleCommand(message);
    if (commandResult) {
      chatMessages.appendChild(
        createMessageElement(commandResult.content, commandResult.type)
          .container
      );
      messageInput.value = "";
      scrollToBottom(false);
      return;
    }

    const userMessage = createMessageElement(message, "user");
    chatMessages.appendChild(userMessage.container);
    messageInput.value = "";
    scrollToBottom(false);

    setBusy(true);

    try {
      const response = await fetch("/api/query/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: message,
          conversation: conversationHistory,
          es_index: currentIndex,
          model_name: currentModel,
        }),
      });

      if (!response.ok)
        throw new Error(`Server responded with status ${response.status}`);
      if (!response.body)
        throw new Error("ReadableStream not supported in this browser.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let messageItem = null;
      let outputDiv = null;
      let parsedContentBuffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        let newlineIndex;

        while ((newlineIndex = buffer.indexOf("\n\n")) >= 0) {
          const messageChunk = buffer.slice(0, newlineIndex).trim();
          buffer = buffer.slice(newlineIndex + 2);

          if (!messageChunk.startsWith("data: ")) continue;

          try {
            const data = JSON.parse(messageChunk.slice(6).trim());

            if (data.chunk) {
              if (data.command_response) {
                if (!messageItem) {
                  messageItem = createMessageElement("", "system");
                  chatMessages.appendChild(messageItem.container);
                  outputDiv = messageItem.message;
                }
                continue;
              }

              if (!messageItem) {
                messageItem = createMessageElement("", "chipper");
                chatMessages.appendChild(messageItem.container);
                outputDiv = messageItem.message;
              }

              parsedContentBuffer += data.chunk;
              outputDiv.innerHTML = marked.parse(parsedContentBuffer);

              outputDiv.querySelectorAll("code").forEach((block) => {
                const lineCount = block.textContent.split("\n").length;
                if (lineCount > 1) {
                  if (
                    !Array.from(block.classList).some((cls) =>
                      cls.startsWith("language-")
                    )
                  ) {
                    block.classList.add("language-plaintext");
                  }

                  Prism.highlightElement(block);
                }
              });

              scrollToBottom(false);
            }

            if (data.done) {
              conversationHistory.push({ role: "user", content: message });
              conversationHistory.push({
                role: "assistant",
                content: data.full_response,
              });
              break;
            }

            if (data.error) {
              if (!messageItem) {
                messageItem = createMessageElement("", "error");
                chatMessages.appendChild(messageItem.container);
                outputDiv = messageItem.message;
              }
              outputDiv.innerHTML += `<span class="text-red-500">Error: ${data.error}</span>`;
              scrollToBottom();
              return;
            }
          } catch (parseError) {
            console.error("Failed to parse JSON:", parseError);
          }
        }
      }
    } catch (error) {
      console.error("Error during message sending:", error);
      chatMessages.appendChild(
        createMessageElement(`Error: ${error.message}`, "error").container
      );
      scrollToBottom();
    } finally {
      setBusy(false);
      scrollToBottom();
    }
  }

  sendButton.addEventListener("click", sendMessage);
});
