export class ChatService {
  constructor(options = {}) {
    this.currentModel = null;
    this.currentIndex = null;
    this.enableStream = true;
    this.messages = [];
    this.currentController = null;
    this.onImageCallback = options.onImage;
    this.onToolCallCallback = options.onToolCall;
    this.onMetricsCallback = options.onMetrics;
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
        if (response.status === 429) {
          throw new Error("Rate limit exceeded. Please try again later.");
        }
        throw new Error(`Server responded with status ${response.status}`);
      }

      if (this.enableStream) {
        await this.handleStreamingResponse(response, onChunk, onError);
      } else {
        await this.handleNonStreamingResponse(response, onChunk, onError);
      }
    } catch (error) {
      if (error.name === "AbortError") {
        console.info("Request aborted");
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
        },
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
    let isFirstChunk = true;
    let isInThinkBlock = false;
    let thinkBuffer = "";
    let fullResponse = "";

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

            // Handle error responses
            if (data.error || (data.done && data.done_reason === "error")) {
              console.error(data);
              onError(data.message.content || "Unknown error occurred");
              return;
            }

            // Handle abort confirmation
            if (data.type === "abort") {
              console.info("Received abort confirmation from server");
              return;
            }

            // Handle streaming content
            if (data.message?.content || data.chunk) {
              const content = data.message?.content || data.chunk;
              const chunk = isFirstChunk ? content.trimLeft() : content;

              if (chunk.length > 0) {
                fullResponse += chunk;

                // Process think tags
                for (let i = 0; i < chunk.length; i++) {
                  if (chunk.slice(i).startsWith("<think>")) {
                    isInThinkBlock = true;
                    i += "<think>".length - 1;
                    continue;
                  }
                  if (chunk.slice(i).startsWith("</think>")) {
                    isInThinkBlock = false;
                    console.log("Think block content:", thinkBuffer);
                    thinkBuffer = "";
                    i += "</think>".length - 1;
                    continue;
                  }

                  if (isInThinkBlock) {
                    thinkBuffer += chunk[i];
                  } else {
                    onChunk(chunk[i]);
                  }
                }
                isFirstChunk = false;
              }

              // Handle additional message features
              if (data.message?.images && this.onImageCallback) {
                this.onImageCallback(data.message.images);
              }
              if (data.message?.tool_calls && this.onToolCallCallback) {
                this.onToolCallCallback(data.message.tool_calls);
              }
            }

            // Handle completion
            if (data.done) {
              if (thinkBuffer) {
                console.log("Final think block content:", thinkBuffer);
                thinkBuffer = "";
              }

              // Handle metrics if callback is provided
              if (this.onMetricsCallback) {
                const metrics = {
                  totalDuration: data.total_duration,
                  loadDuration: data.load_duration,
                  promptEvalCount: data.prompt_eval_count,
                  promptEvalDuration: data.prompt_eval_duration,
                  evalCount: data.eval_count,
                  evalDuration: data.eval_duration,
                };
                this.onMetricsCallback(metrics);
              }

              // Handle TTS if full_response is available
              if (data.full_response?.llm?.replies?.[0]) {
                const ttsText = data.full_response.llm.replies[0];
                window.postMessage(
                  {
                    type: "tts-message",
                    text: ttsText,
                    sid: 0,
                    speed: 1,
                  },
                  "*",
                );
              } else if (fullResponse) {
                // Fallback to using accumulated response
                window.postMessage(
                  {
                    type: "tts-message",
                    text: fullResponse,
                    sid: 0,
                    speed: 1,
                  },
                  "*",
                );
              }
              break;
            }
          } catch (parseError) {
            console.error("Failed to parse JSON:", parseError);
            onError("Failed to parse server response");
          }
        }
      }
    } catch (error) {
      if (error.name === "AbortError") {
        throw error;
      }
      throw new Error(`Stream reading error: ${error.message}`);
    } finally {
      reader.cancel();
    }
  }

  async handleNonStreamingResponse(response, onChunk, onError) {
    const data = await response.json();

    if (data.error || (data.done && data.done_reason === "error")) {
      onError(data.error || "Unknown error occurred");
      return;
    }

    // Handle standard message format
    if (data.message?.content) {
      const trimmedContent = data.message.content.trimLeft();
      onChunk(trimmedContent);

      // Handle additional message features
      if (data.message.images && this.onImageCallback) {
        this.onImageCallback(data.message.images);
      }
      if (data.message.tool_calls && this.onToolCallCallback) {
        this.onToolCallCallback(data.message.tool_calls);
      }

      // Update messages array
      this.messages.push({
        role: "assistant",
        content: trimmedContent,
      });
    }
    // Handle legacy format
    else if (data.success && data.messages) {
      const lastMessage = data.messages[data.messages.length - 1];
      if (lastMessage.role === "assistant") {
        const trimmedContent = lastMessage.content.trimLeft();
        onChunk(trimmedContent);
        this.messages = data.messages;
      }
    }

    // Handle metrics if callback is provided
    if (this.onMetricsCallback && data.done) {
      const metrics = {
        totalDuration: data.total_duration,
        loadDuration: data.load_duration,
        promptEvalCount: data.prompt_eval_count,
        promptEvalDuration: data.prompt_eval_duration,
        evalCount: data.eval_count,
        evalDuration: data.eval_duration,
      };
      this.onMetricsCallback(metrics);
    }
  }

  addMessage(role, content) {
    this.messages.push({ role, content });

    console.info("---------- Adding message ----------");
    console.info("Added message:", {
      role,
      content,
    });
    console.info("Current model:", this.currentModel);
    console.info("Current index:", this.currentIndex);
    console.info("Message history:", this.messages);
    console.info("------------------------------------");
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
