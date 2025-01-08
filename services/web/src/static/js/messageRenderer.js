export class MessageRenderer {
  constructor() {
    this.marked = window.marked;
    this.setupMarked();
  }

  setupMarked() {
    this.marked.setOptions({
      headerIds: false,
      mangle: false,
      breaks: true,
      gfm: true,
      sanitize: false,
      highlight: function (code, lang) {
        if (lang && Prism.languages[lang]) {
          try {
            return Prism.highlight(code, Prism.languages[lang], lang);
          } catch (e) {
            console.error(e);
            return code;
          }
        }
        return code;
      },
    });
  }

  createMessageElement(content, type = "assistant", isThinking = false) {
    const messageContainer = document.createElement("div");
    messageContainer.className = `flex ${type === "user" ? "justify-end" : "justify-start"} mb-4`;

    const messageDiv = document.createElement("div");
    messageDiv.className = "p-4 rounded-3xl min-w-48 max-w-3xl";

    const typeClasses = {
      user: "bg-zinc-900 selection:bg-zinc-700 text-white user-message",
      assistant: "bg-champagne-200 dark:bg-zinc-700 selection:bg-champagne-500 selection:dark:bg-zinc-800 assistant-message",
      error: "bg-red-600 dark:bg-red-500 selection:bg-red-200 text-white error-message",
      system: "bg-purple-600 dark:bg-purple-500 selection:bg-purple-900 text-white system-message",
    };
    messageDiv.classList.add(...(typeClasses[type]?.split(" ") || ["bg-champagne-600"]));

    const header = document.createElement("div");
    header.className = `font-bold text-sm ${type === "assistant" ? "text-zinc-800 dark:text-zinc-300" : "text-white"} mb-2`;
    header.textContent = {
      user: "You",
      assistant: "Chipper",
      system: "System",
      error: "Error",
    }[type] || "Message";

    const contentDiv = document.createElement("div");

    if (isThinking) {
      contentDiv.className = "dots-animation ml-1 flex items-center space-x-2";
      const thinkingText = document.createElement("span");
      thinkingText.textContent = "Chipper is thinking";
      contentDiv.appendChild(thinkingText);

      const dotsContainer = document.createElement("span");
      dotsContainer.className = "";
      for (let i = 0; i < 3; i++) {
        const dot = document.createElement("span");
        dot.textContent = ".";
        dot.className = "dot";
        dotsContainer.appendChild(dot);
      }
      contentDiv.appendChild(dotsContainer);
    } else {
      contentDiv.innerHTML = type === "system" ? this.marked.parse(content) : this.marked.parseInline(content);
      contentDiv.className = "prose prose-sm max-w-none break-words";
    }

    messageDiv.appendChild(header);
    messageDiv.appendChild(contentDiv);
    messageContainer.appendChild(messageDiv);

    return { container: messageContainer, message: contentDiv };
  }

  handleCodeHighlighting(outputDiv) {
    outputDiv.querySelectorAll("code").forEach((block) => {
      const lineCount = block.textContent.split("\n").length;
      if (lineCount > 1) {
        if (!Array.from(block.classList).some((cls) => cls.startsWith("language-"))) {
          block.classList.add("language-plaintext");
        }
        Prism.highlightElement(block);
      }
    });
  }
}
