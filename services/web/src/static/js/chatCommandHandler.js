export class ChatCommandHandler {
  constructor(onModelChange, onIndexChange, onStreamChange, onClear) {
    this.onModelChange = onModelChange;
    this.onIndexChange = onIndexChange;
    this.onStreamChange = onStreamChange;
    this.onClear = onClear;
  }

  handleCommand(message) {
    const parts = message.split(" ");

    const commands = {
      "/help": () => ({
        type: "system",
        content: this.getHelpMessage(),
      }),
      "/model": () => {
        const model = parts[1] || null;
        this.onModelChange(model);
        return { type: "system", content: `Model set to: \`${model}\`` };
      },
      "/index": () => {
        const index = parts[1] || null;
        this.onIndexChange(index);
        return { type: "system", content: `Index set to: \`${index}\`` };
      },
      "/stream": () => {
        const value = parts[1] || "true";
        const enabled = value === "true" || value === "1";
        this.onStreamChange(enabled);
        return {
          type: "system",
          content: `Streaming is ${enabled ? "enabled" : "disabled"}`,
        };
      },
      "/clear": () => {
        this.onClear();
        return { type: "system", content: "Chat history cleared" };
      },
    };

    const command = commands[parts[0]];
    return command ? command() : null;
  }

  getHelpMessage() {
    return `### Available Commands
  
  \`/model [name]\` - Change AI model
  \`/index [name]\` - Change knowledge base index
  \`/stream [name]\` - Enable or disable response streaming
  \`/clear\` - Clear chat history
  \`/help\` - Show this help message
  
  ### Chat Controls
  - Press Enter to send message`;
  }
}