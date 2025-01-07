export class ChatService {
  constructor(options = {}) {
    this.currentModel = null;
    this.currentIndex = null;
    this.enableStream = true;
    this.messages = [];
    this.currentController = null;
  }

  abortCurrentRequest() {
    if (this.currentController) {
      this.currentController.abort();
      this.currentController = null;
      console.info("Chat request aborted");
    }
  }

  async sendMessage(onChunk, onError) {
    this.abortCurrentRequest();
    this.currentController = new AbortController();

    const chatBody = JSON.stringify({
      model: this.currentModel,
      messages: this.messages,
      stream: this.enableStream,
      options: {
        index: this.currentIndex,
      },
    });

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: chatBody,
        signal: this.currentController.signal,
      });

      if (!response.ok) {
        if (response.status === 429)
          throw new Error(`Rate limit exceeded. Please try again later.`);
        
        throw new Error(`Server responded with status ${response.status}`);
      }

      if (this.enableStream) {
        await this.handleStreamingResponse(response, onChunk, onError);
      } else {
        await this.handleNonStreamingResponse(response, onChunk, onError);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.info('Request aborted');
        await this.notifyServerAbort();
        return;
      }
      onError(error.message);
    } finally {
      this.currentController = null;
    }
  }

  async notifyServerAbort() {
    try {
      const response = await fetch("/api/chat/abort", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
      });
      if (!response.ok) {
        console.error("Failed to notify server about abort");
      }
    } catch (error) {
      console.error("Error notifying server about abort:", error);
    }
  }

  async handleStreamingResponse(response, onChunk, onError) {
    if (!response.body) {
      throw new Error("ReadableStream not supported in this browser.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    try {
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
            if (data.error) {
              onError(data.error);
              return;
            }
            if (data.type === "abort") {
              console.info("Received abort confirmation from server");
              return;
            }
            if (data.chunk) {
              onChunk(data.chunk);
            }
            if (data.done) break;
          } catch (parseError) {
            console.error("Failed to parse JSON:", parseError);
          }
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        throw error;
      }
      throw new Error(`Stream reading error: ${error.message}`);
    } finally {
      reader.cancel();
    }
  }

  async handleNonStreamingResponse(response, onChunk, onError) {
    const data = await response.json();

    if (data.error) {
      onError(data.error);
      return;
    }

    if (data.success && data.messages) {
      const lastMessage = data.messages[data.messages.length - 1];
      if (lastMessage.role === "assistant") {
        onChunk(lastMessage.content);
        this.messages = data.messages;
      }
    }
  }

  addMessage(role, content) {
    this.messages.push({ role, content });

    console.info("----------Adding message----------");
    console.info("Added message:", {
      role,
      content,
    });
    console.info("Current model:", this.currentModel);
    console.info("Current index:", this.currentIndex);
    console.info("Message history:", this.messages);
    console.info("----------------------------------");
  }

  clearMessages() {
    this.messages = [];
  }

  setModel(model) {
    this.currentModel = model;
    console.info("Current model:", this.currentModel);
  }

  setIndex(index) {
    this.currentIndex = index;
    console.info("Current index:", this.currentIndex);
  }

  setStreamMode(enable) {
    this.enableStream = enable;
  }
}
