export class URLParamsHandler {
  constructor(chatCommandHandler) {
    this.chatCommandHandler = chatCommandHandler;
    this.supportedParams = {
      model: "/model",
      index: "/index",
      stream: "/stream",
      theme: "/theme",
    };
  }

  handleURLParams() {
    const urlParams = new URLSearchParams(window.location.search);

    for (const [param, command] of Object.entries(this.supportedParams)) {
      const value = urlParams.get(param);
      if (value !== null) {
        const commandString = `${command} ${value}`;
        this.chatCommandHandler.handleCommand(commandString);
      }
    }
  }

  getParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
  }

  updateURL(param, value) {
    const url = new URL(window.location);
    if (value === null || value === "") {
      url.searchParams.delete(param);
    } else {
      url.searchParams.set(param, value);
    }
    window.history.replaceState({}, "", url);
  }
}
