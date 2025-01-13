export class TTSManager {
  constructor() {
    this.ttsIframeElement = null;
    this.messageQueue = [];
    this.isProcessing = false;
    this.initPromise = null;
    this.isReady = false;
  }

  cleanText(text) {
    if (!text) return "";

    let cleaned = text
      .replace(/\*\*(.*?)\*\*/g, "$1") // Bold
      .replace(/\*(.*?)\*/g, "$1") // Italic
      .replace(/\[(.*?)\]\(.*?\)/g, "$1") // Links
      .replace(/`(.*?)`/g, "$1") // Code
      .replace(/^#{1,6}\s/gm, "") // Headers
      .replace(/^[->]\s/gm, "") // Blockquotes and lists
      .replace(/^\d+\.\s/gm, "") // Numbered lists
      .replace(/\n{2,}/g, " ") // Multiple newlines
      .replace(/\s+/g, " "); // Multiple spaces

    cleaned = cleaned.trim();

    this.log("Text cleaned", {
      original: text,
      cleaned: cleaned,
      lengthDiff: text.length - cleaned.length,
    });

    return cleaned;
  }

  checkQueueStatus() {
    const status = {
      isProcessing: this.isProcessing,
      queueLength: this.messageQueue.length,
      hasFrame: !!this.ttsIframeElement,
    };
    this.log("Queue status check", status, status.queueLength > 0 ? "warn" : "info");
    return status;
  }

  log(message, data = null, type = "info") {
    const timestamp = new Date().toISOString();
    const prefix = "[TTS]";
    const logData = data ? `: ${JSON.stringify(data)}` : "";

    switch (type) {
      case "error":
        console.error(`${prefix} [${timestamp}] ${message}${logData}`);
        break;
      case "warn":
        console.warn(`${prefix} [${timestamp}] ${message}${logData}`);
        break;
      default:
        console.log(`${prefix} [${timestamp}] ${message}${logData}`);
    }
  }

  init() {
    this.log("TTSManager init called");

    this.handleMessage = this.handleMessage.bind(this);
    window.addEventListener("message", this.handleMessage);

    if (this.initPromise) {
      this.log("Initialization already in progress, returning existing promise");
      return this.initPromise;
    }

    this.initPromise = new Promise((resolve, reject) => {
      if (this.ttsIframeElement) {
        this.log("TTS frame already exists, resolving immediately");
        resolve();
        return;
      }

      const container = document.getElementById("tts-container");
      if (!container) {
        const error = new Error("TTS container element not found");
        this.log("Failed to find TTS container element", null, "error");
        reject(error);
        return;
      }

      this.log("Creating TTS iframe");
      const iframe = document.createElement("iframe");
      iframe.style.cssText = "visibility: hidden; width: 0; height: 0;";
      iframe.src = "static/vendor/tts-sherpa-onnx/chipper_helper.html";

      container.appendChild(iframe);
      this.ttsIframeElement = iframe;
      this.log("TTS iframe created and appended to container");
    }).catch((error) => {
      this.log("Initialization failed", error, "error");
      this.initPromise = null;
      throw error;
    });

    return this.initPromise;
  }

  handleMessage(event) {
    this.log("Message received", event.data);
    this.checkQueueStatus();

    if (event.data?.type === "tts-message") {
      const message = {
        text: this.cleanText(event.data.text),
        sid: event.data.sid || 0,
        speed: event.data.speed || 1,
      };

      this.log("Processing incoming TTS message", message);

      this.messageQueue.push(message);
      this.log("Updated message queue", { length: this.messageQueue.length });

      if (!this.ttsIframeElement) {
        this.log("No TTS frame found, initializing");
        this.init()
          .then(() => {
            this.log("Initialization complete, processing queue");
            if (!this.isProcessing) {
              this.processMessageQueue();
            }
          })
          .catch((error) => {
            this.log("Failed to initialize TTS system", error, "error");
          });
      } else if (!this.isProcessing && this.isReady) {
        this.log("System not processing, attempting to process queue");
        this.processMessageQueue();
      }
      return;
    }

    if (!this.ttsIframeElement || event.source !== this.ttsIframeElement.contentWindow) {
      this.log("Ignoring message from unknown source");
      return;
    }

    switch (event.data?.type) {
      case "tts-ready":
        this.log("TTS system is ready");
        this.isReady = true;
        this.processMessageQueue();
        break;
      case "tts-error": {
        this.log("TTS system error", event.data.error, "error");
        if (this.isProcessing) {
          this.log("Forcing processing state reset after error", null, "warn");
        }
        this.isReady = false;
        this.isProcessing = false;
        break;
      }

      case "tts-complete": {
        this.log("TTS generation complete", {
          queueLength: this.messageQueue.length,
        });
        const wasProcessing = this.isProcessing;
        this.isProcessing = false;
        if (!wasProcessing) {
          this.log("Warning: Received complete event while not processing", null, "warn");
        }
        // TODO: tts-complete does not handle playback time; playback complete event yet, overlap will happen.
        this.processMessageQueue();
        break;
      }

      default: {
        this.log("Unhandled message type", { type: event.data?.type }, "warn");
        break;
      }
    }
  }

  generateTTS(message) {
    this.log("generateTTS called", message);

    if (!this.ttsIframeElement) {
      this.log(
        "Cannot generate TTS: system not ready",
        {
          hasFrame: false,
        },
        "error",
      );
      return;
    }

    try {
      this.log("Sending TTS generation request", {
        text: message.text,
        sid: message.sid,
        speed: message.speed,
      });

      this.isProcessing = true;
      this.ttsIframeElement.contentWindow.postMessage(
        {
          type: "tts-generate",
          text: message.text,
          sid: message.sid,
          speed: message.speed,
        },
        "*",
      );
      this.log("TTS generation request sent successfully");
    } catch (error) {
      this.log("TTS generation failed", error, "error");
      this.isProcessing = false;
      this.messageQueue.unshift(message);
      this.log("Message returned to queue, attempting to process next");
      this.processMessageQueue();
    }
  }

  processMessageQueue() {
    this.log("processMessageQueue called", {
      isProcessing: this.isProcessing,
      queueLength: this.messageQueue.length,
    });

    if (this.isProcessing || this.messageQueue.length === 0) {
      this.log("Skipping queue processing", {
        reason: this.isProcessing ? "currently processing" : "queue empty",
      });
      return;
    }

    const message = this.messageQueue.shift();
    this.log("Processing next message from queue", {
      remaining: this.messageQueue.length,
    });
    this.generateTTS(message);
  }

  destroy() {
    this.log("Destroying TTSManager");
    window.removeEventListener("message", this.handleMessage);

    if (this.ttsIframeElement) {
      this.log("Removing TTS iframe");
      this.ttsIframeElement.remove();
      this.ttsIframeElement = null;
    }

    this.isProcessing = false;
    this.messageQueue = [];
    this.initPromise = null;
    this.log("TTSManager destroyed");
  }
}
