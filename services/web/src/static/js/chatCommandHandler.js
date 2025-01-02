export class ChatCommandHandler {
  constructor(onModelChange, onIndexChange, onStreamChange, onClear, onToggleTheme) {
    this.onModelChange = onModelChange;
    this.onIndexChange = onIndexChange;
    this.onStreamChange = onStreamChange;
    this.onClear = onClear;
    this.onToggleTheme = onToggleTheme;
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
          content: `Streaming is \`${enabled ? "enabled" : "disabled"}\``,
        };
      },
      "/clear": () => {
        this.onClear();
        return { type: "system", content: "Chat history cleared" };
      },
      "/theme": () => {
        this.onToggleTheme();
        return { type: "system", content: "Theme toggled" };
      },
    };

    const command = commands[parts[0]];
    return command ? command() : null;
  }

  getHelpMessage() {
    return `### Available Commands
  
  \`/model [name]\` - Change AI model
  \`/index [name]\` - Change knowledge base index
  \`/stream [0/1]\` - Enable or disable response streaming
  \`/clear\` - Clear chat history
  \`/theme\` - Toggle theme
  \`/help\` - Show this help message`;
  }
}
