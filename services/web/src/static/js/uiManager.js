export class UIManager {
  constructor(elements) {
    this.elements = elements;
    this.setupTextarea();
  }

  setupTextarea() {
    this.elements.messageInput.focus();
    this.elements.messageInput.oninput = () => this.adjustTextareaHeight();
  }

  adjustTextareaHeight() {
    const input = this.elements.messageInput;
    input.style.height = "auto";
    input.style.height = input.scrollHeight + "px";
  }

  scrollToBottom(immediate = false) {
    const scroll = () => {
      const container = this.elements.chatMessages;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    };
    immediate ? scroll() : setTimeout(scroll, 200);
  }

  setBusy(busy) {
    this.elements.busyIndicator.classList.toggle("hidden", !busy);
    this.elements.messageInput.disabled = busy;
    this.elements.sendButton.disabled = busy;
    this.elements.sendButton.classList.toggle("opacity-50", busy);
    this.elements.sendButton.classList.toggle("cursor-not-allowed", busy);
  }

  updateMessageInput(newValue) {
    this.elements.messageInput.value = newValue;
    const event = new Event("input", { bubbles: true });
    this.elements.messageInput.dispatchEvent(event);
  }
}
