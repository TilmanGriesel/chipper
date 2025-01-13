export class UIManager {
  constructor(elements) {
    this.elements = elements;
    this.setupTextarea();
    this.isProcessing = false;
    this.userIsInspecting = false;
    this.setupScrollHandler();
  }

  setupTextarea() {
    this.elements.messageInput.focus();
    this.elements.messageInput.oninput = () => this.adjustTextareaHeight();
  }

  setupScrollHandler() {
    const container = this.elements.chatMessages;
    let lastScrollTop = container.scrollTop;

    container.addEventListener("scroll", () => {
      const isScrollingUp = container.scrollTop < lastScrollTop;
      const isNotAtBottom =
        container.scrollTop + container.clientHeight <
        container.scrollHeight - 10;

      if (isScrollingUp || isNotAtBottom) {
        this.userIsInspecting = true;
        return;
      }

      this.userIsInspecting = false;

      lastScrollTop = container.scrollTop;
    });
  }

  adjustTextareaHeight() {
    const input = this.elements.messageInput;
    input.style.height = "auto";
    input.style.height = input.scrollHeight + "px";
  }

  scrollToBottomDesired(immediate = true, force = false) {
    if (this.userIsInspecting && !force) return;

    const container = this.elements.chatMessages;
    if (!container) return;

    const scroll = () => {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: immediate ? "auto" : "smooth",
      });
    };

    scroll();
  }

  setBusy(busy) {
    this.isProcessing = busy;
    this.elements.busyIndicator.classList.toggle("off", !busy);
    this.elements.messageInput.disabled = busy;

    // reset user scroll state
    if (busy) {
      this.userIsInspecting = false;
    }

    const button = this.elements.sendButton;
    const sendIcon = document.getElementById("send-icon");
    const abortIcon = document.getElementById("abort-icon");

    if (busy) {
      // abort state
      button.dataset.state = "abort";
      sendIcon.classList.add("hidden");
      abortIcon.classList.remove("hidden");
    } else {
      // send state
      button.dataset.state = "send";
      sendIcon.classList.remove("hidden");
      abortIcon.classList.add("hidden");
    }
  }

  updateMessageInput(newValue) {
    this.elements.messageInput.value = newValue;
    const event = new Event("input", { bubbles: true });
    this.elements.messageInput.dispatchEvent(event);
  }

  toggleTheme() {
    if (document.documentElement.classList.contains("dark")) {
      document.documentElement.classList.remove("dark");
      localStorage.theme = "light";
      document.getElementById("theme-toggle-icon").innerHTML = `
    <path
      d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
    `;
    } else {
      document.documentElement.classList.add("dark");
      localStorage.theme = "dark";
      document.getElementById("theme-toggle-icon").innerHTML = `
    <path
      d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
    `;
    }
  }

  toggleWideMode() {
    const mainContainer = document.getElementById("main");
    if (document.documentElement.classList.contains("wide-mode")) {
      document.documentElement.classList.remove("wide-mode");
      mainContainer.classList.remove("max-w-full");
      mainContainer.classList.add("max-w-3xl");
      localStorage.wideMode = "false";
    } else {
      document.documentElement.classList.add("wide-mode");
      mainContainer.classList.remove("max-w-3xl");
      mainContainer.classList.add("max-w-full");
      localStorage.wideMode = "true";
    }
  }

  isInProcessingState() {
    return this.isProcessing;
  }

  updateGreeting() {
    const hour = new Date().getHours();
    let greeting;

    if (hour >= 5 && hour < 12) {
      greeting = "Good morning! What can I help you with today?";
    } else if (hour >= 12 && hour < 17) {
      greeting = "Good afternoon! What can I help you with today?";
    } else if (hour >= 17 && hour < 22) {
      greeting = "Good evening! What can I help you with today?";
    } else {
      greeting = "Hello! What can I help you with today?";
    }

    this.elements.welcomeText.textContent = greeting;
  }
}
