import { MessageRenderer } from "./messageRenderer.js";
import { ChatCommandHandler } from "./chatCommandHandler.js";
import { UIManager } from "./uiManager.js";
import { ChatService } from "./chatService.js";
import InputHistoryManager from "./inputHistoryManager.js";

document.addEventListener("DOMContentLoaded", () => {
  const elements = {
    messageInput: document.getElementById("message-input"),
    chatMessages: document.getElementById("chat-messages"),
    busyIndicator: document.getElementById("busy-indicator"),
    sendButton: document.getElementById("send-button"),
  };

  const historyManager = new InputHistoryManager({
    maxSize: 50,
    excludePatterns: [],
  });

  const messageRenderer = new MessageRenderer();
  const chatService = new ChatService();
  const uiManager = new UIManager(elements);

  const chatCommandHandler = new ChatCommandHandler(
    (model) => chatService.setModel(model),
    (index) => chatService.setIndex(index),
    (enable) => chatService.setStreamMode(enable),
    () => {
      chatService.clearMessages();
      elements.chatMessages.innerHTML = "";
    }
  );

  elements.messageInput.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      const previousMessage = historyManager.navigateBack(
        elements.messageInput.value
      );
      if (previousMessage !== null) {
        uiManager.updateMessageInput(previousMessage);
        setTimeout(() => {
          elements.messageInput.selectionStart =
            elements.messageInput.selectionEnd =
              elements.messageInput.value.length;
        }, 0);
      }
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      const nextMessage = historyManager.navigateForward();
      if (nextMessage !== null) {
        uiManager.updateMessageInput(nextMessage);
        setTimeout(() => {
          elements.messageInput.selectionStart =
            elements.messageInput.selectionEnd =
              elements.messageInput.value.length;
        }, 0);
      }
    }
  });

  // Handle message sending
  async function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message) return;

    historyManager.addToHistory(message);

    const commandResult = chatCommandHandler.handleCommand(message);
    if (commandResult) {
      elements.chatMessages.appendChild(
        messageRenderer.createMessageElement(
          commandResult.content,
          commandResult.type
        ).container
      );
      uiManager.updateMessageInput("");
      uiManager.scrollToBottom(false);
      return;
    }

    const userMessage = messageRenderer.createMessageElement(message, "user");
    elements.chatMessages.appendChild(userMessage.container);
    uiManager.updateMessageInput("");
    uiManager.scrollToBottom(false);

    uiManager.setBusy(true);
    chatService.addMessage("user", message);

    let messageItem = null;
    let outputDiv = null;
    let responseContent = "";

    try {
      await chatService.sendMessage(
        message,
        (chunk) => {
          if (!messageItem) {
            messageItem = messageRenderer.createMessageElement("", "assistant");
            elements.chatMessages.appendChild(messageItem.container);
            outputDiv = messageItem.message;
          }

          responseContent += chunk;
          outputDiv.innerHTML = marked.parse(responseContent);
          messageRenderer.handleCodeHighlighting(outputDiv);
          uiManager.scrollToBottom(false);
        },
        (error) => {
          elements.chatMessages.appendChild(
            messageRenderer.createMessageElement(`Error: ${error}`, "error")
              .container
          );
          uiManager.scrollToBottom();
        }
      );

      if (responseContent) {
        chatService.addMessage("assistant", responseContent);
      }
    } finally {
      uiManager.setBusy(false);
      uiManager.scrollToBottom();
      elements.messageInput.focus();
    }
  }

  // Setup event listeners
  elements.messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  elements.messageInput.addEventListener("input", () =>
    uiManager.scrollToBottom(false)
  );
  elements.sendButton.addEventListener("click", sendMessage);
});
