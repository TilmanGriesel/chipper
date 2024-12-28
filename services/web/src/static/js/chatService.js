export class ChatService {
  constructor(options = {}) {
    this.currentModel = null;
    this.currentIndex = null;
    this.enableStream = true;
    this.messages = [];
  }

  async sendMessage(message, onChunk, onError) {
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
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      if (this.enableStream) {
        await this.handleStreamingResponse(response, onChunk, onError);
      } else {
        await this.handleNonStreamingResponse(response, onChunk, onError);
      }
    } catch (error) {
      onError(error.message);
    }
  }

  async handleStreamingResponse(response, onChunk, onError) {
    if (!response.body) {
      throw new Error("ReadableStream not supported in this browser.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

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
          if (data.chunk) {
            onChunk(data.chunk);
          }
          if (data.done) break;
        } catch (parseError) {
          console.error("Failed to parse JSON:", parseError);
        }
      }
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
