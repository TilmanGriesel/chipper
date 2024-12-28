export default class InputHistoryManager {
  constructor(options = {}) {
    this.maxSize = options.maxSize || 50;
    this.excludePatterns = options.excludePatterns || [/^\//];
    this.history = [];
    this.currentIndex = -1;
    this.savedInput = "";
  }

  addToHistory(input) {
    const trimmedInput = input.trim();

    if (!trimmedInput || this.isExcluded(trimmedInput)) {
      return;
    }

    if (this.history[0] === trimmedInput) {
      return;
    }

    this.history.unshift(trimmedInput);

    if (this.history.length > this.maxSize) {
      this.history.pop();
    }

    this.resetNavigation();
  }

  isExcluded(input) {
    return this.excludePatterns.some((pattern) => pattern.test(input));
  }

  navigateBack(currentInput) {
    if (this.history.length === 0) return null;

    if (this.currentIndex === -1) {
      this.savedInput = currentInput;
    }

    if (this.currentIndex < this.history.length - 1) {
      this.currentIndex++;
      return this.history[this.currentIndex];
    }

    return null;
  }

  navigateForward() {
    if (this.currentIndex === -1) return null;

    if (this.currentIndex > 0) {
      this.currentIndex--;
      return this.history[this.currentIndex];
    } else {
      const savedInput = this.savedInput;
      this.resetNavigation();
      return savedInput;
    }
  }

  resetNavigation() {
    this.currentIndex = -1;
    this.savedInput = "";
  }

  getHistory() {
    return [...this.history];
  }

  clearHistory() {
    this.history = [];
    this.resetNavigation();
  }
}
