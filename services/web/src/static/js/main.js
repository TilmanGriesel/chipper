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
    themeButton: document.getElementById("theme-button"),
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
    },
    () => uiManager.toggleTheme(),
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

  // message send handling
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
            messageRenderer.createMessageElement(`${error}`, "error").container
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

  // event listeners
  elements.messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  elements.sendButton.addEventListener("click", sendMessage);

  elements.messageInput.addEventListener("input", () => uiManager.scrollToBottom(false));
  elements.messageInput.addEventListener("focus", () => uiManager.scrollToBottom(false));
  elements.messageInput.addEventListener("blur", () => uiManager.scrollToBottom(false));
  elements.messageInput.addEventListener('touchstart', () => uiManager.scrollToBottom(false));
  elements.messageInput.addEventListener('click', () => uiManager.scrollToBottom(false));

  elements.themeButton.addEventListener("click", uiManager.toggleTheme);

  // theme handling
  if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
});
