export class ChatCommandHandler {
  constructor(
    onModelChange,
    onIndexChange,
    onStreamChange,
    onClear,
    onToggleTheme,
    onToggleWide,
    urlParamsHandler
  ) {
    this.onModelChange = onModelChange;
    this.onIndexChange = onIndexChange;
    this.onStreamChange = onStreamChange;
    this.onClear = onClear;
    this.onToggleTheme = onToggleTheme;
    this.onToggleWide = onToggleWide;
    this.urlParamsHandler = urlParamsHandler;
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
        if (this.urlParamsHandler) {
          this.urlParamsHandler.updateURL("model", model);
        }
        return { type: "system", content: `Model set to: \`${model}\`` };
      },
      "/index": () => {
        const index = parts[1] || null;
        this.onIndexChange(index);
        if (this.urlParamsHandler) {
          this.urlParamsHandler.updateURL("index", index);
        }
        return { type: "system", content: `Index set to: \`${index}\`` };
      },
      "/stream": () => {
        const value = parts[1] || "true";
        const enabled = value === "true" || value === "1";
        this.onStreamChange(enabled);
        if (this.urlParamsHandler) {
          this.urlParamsHandler.updateURL("stream", enabled ? "1" : "0");
        }
        return {
          type: "system",
          content: `Streaming is \`${enabled ? "enabled" : "disabled"}\``,
        };
      },
      "/clear": () => {
        this.onClear();
        return { type: "system", content: null };
      },
      "/theme": () => {
        this.onToggleTheme();
        if (this.urlParamsHandler) {
          const isDark = document.documentElement.classList.contains("dark");
          this.urlParamsHandler.updateURL("theme", isDark ? "dark" : "light");
        }
        return { type: "system", content: "Theme toggled" };
      },
      "/wide": () => {
        this.onToggleWide();
        if (this.urlParamsHandler) {
          const isWide =
            document.documentElement.classList.contains("wide-mode");
          this.urlParamsHandler.updateURL("wide", isWide ? "1" : "0");
        }
        return { type: "system", content: "Wide mode toggled" };
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
  \`/wide\` - Toggle wide mode
  \`/help\` - Show this help message
  
  You can also set initial values using URL parameters:
  \`?model=name&index=name&stream=1&theme=dark&wide=1\``;
  }
}
