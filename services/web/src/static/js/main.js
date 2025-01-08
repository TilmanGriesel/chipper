import { MessageRenderer } from "./messageRenderer.js";
import { ChatCommandHandler } from "./chatCommandHandler.js";
import { URLParamsHandler } from "./urlParamsHandler.js";
import { UIManager } from "./uiManager.js";
import { ChatService } from "./chatService.js";
import InputHistoryManager from "./inputHistoryManager.js";

document.addEventListener("DOMContentLoaded", () => {
  const elements = {
    messageInput: document.getElementById("message-input"),
    welcomeMessage: document.getElementById("welcome-message"),
    welcomeText: document.getElementById("welcome-text"),
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

  let urlParamsHandler;
  const chatCommandHandler = new ChatCommandHandler(
    (model) => chatService.setModel(model),
    (index) => chatService.setIndex(index),
    (enable) => chatService.setStreamMode(enable),
    () => {
      chatService.clearMessages();
      elements.chatMessages.innerHTML = "";
    },
    () => uiManager.toggleTheme(),
    null
  );

  urlParamsHandler = new URLParamsHandler(chatCommandHandler);
  chatCommandHandler.urlParamsHandler = urlParamsHandler;

  urlParamsHandler.handleURLParams();

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

  uiManager.updateGreeting()

  // message send handling
  async function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message) return;

    elements.welcomeMessage.classList.add('hidden');
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
      uiManager.scrollToBottom();
      return;
    }

    const userMessage = messageRenderer.createMessageElement(message, "user");
    elements.chatMessages.appendChild(userMessage.container);
    uiManager.updateMessageInput("");
    uiManager.scrollToBottom();

    uiManager.setBusy(true);
    chatService.addMessage("user", message);

    let messageItem = null;
    let outputDiv = null;
    let responseContent = "";

    try {
      messageItem = messageRenderer.createMessageElement("", "assistant", true);
      elements.chatMessages.appendChild(messageItem.container);
      outputDiv = messageItem.message;
      uiManager.scrollToBottom();

      await chatService.sendMessage(
        (chunk) => {
          if (outputDiv.classList.contains('dots-animation')) {
            // replace the thinking animation with a new content div on first chunk
            const newContentDiv = document.createElement("div");
            newContentDiv.className = "prose prose-sm max-w-none break-words";
            outputDiv.parentNode.replaceChild(newContentDiv, outputDiv);
            outputDiv = newContentDiv;
          }

          responseContent += chunk;
          outputDiv.innerHTML = marked.parse(responseContent);
          messageRenderer.handleCodeHighlighting(outputDiv);
          uiManager.scrollToBottom();
        },
        (error) => {
          if (error !== 'AbortError') {
            elements.chatMessages.appendChild(
              messageRenderer.createMessageElement(`${error}`, "error").container
            );
            uiManager.scrollToBottom();
          }
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
      if (uiManager.isInProcessingState()) {
        chatService.abortCurrentRequest();
        uiManager.setBusy(false);
      } else {
        sendMessage();
      }
    }
  });

  elements.sendButton.addEventListener("click", () => {
    if (uiManager.isInProcessingState()) {
      chatService.abortCurrentRequest();
      uiManager.setBusy(false);
    } else {
      sendMessage();
    }
  });

  elements.sendButton.addEventListener("click", sendMessage);

  elements.messageInput.addEventListener("input", () => uiManager.scrollToBottom());
  elements.messageInput.addEventListener("focus", () => uiManager.scrollToBottom());
  elements.messageInput.addEventListener("blur", () => uiManager.scrollToBottom());
  elements.messageInput.addEventListener('touchstart', () => uiManager.scrollToBottom());
  elements.messageInput.addEventListener('click', () => uiManager.scrollToBottom());

  elements.themeButton.addEventListener("click", uiManager.toggleTheme);

  // theme handling
  if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
});
