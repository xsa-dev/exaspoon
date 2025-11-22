/**
 * ============================================
 * CHAT INTERFACE MODULE
 * ============================================
 */

class ChatInterface {
  constructor(containerSelector, theme, stateManager = null) {
    this.container = document.querySelector(containerSelector);
    this.theme = theme;
    this.messages = [];
    this.isLoading = false;
    this.stateManager = stateManager;
    this.currentConversationId = null;

    // UI elements
    this.chatContainer = null;
    this.inputArea = null;
    this.inputField = null;
    this.sendButton = null;
    this.loadingIndicator = null;
  }

  initialize() {
    this.createChatInterface();
    this.bindEvents();

    // Load saved chat history if state manager is available
    if (this.stateManager) {
      this.loadChatHistory();
    }

    return this;
  }

  createChatInterface() {
    // Use existing HTML elements
    this.chatContainer = this.container;
    this.messagesArea = document.getElementById("response-textarea");
    this.inputField = document.getElementById("input-field");

    // Create send button if it doesn't exist
    if (!document.getElementById("send-button")) {
      this.sendButton = document.createElement("button");
      this.sendButton.id = "send-button";
      this.sendButton.className = "send-button";
      this.sendButton.textContent = "Send";
      this.sendButton.setAttribute("aria-label", "Send message");
      this.inputField.parentNode.appendChild(this.sendButton);
    } else {
      this.sendButton = document.getElementById("send-button");
    }

    // Create loading indicator if it doesn't exist
    if (!document.getElementById("loading-indicator")) {
      this.loadingIndicator = document.createElement("div");
      this.loadingIndicator.id = "loading-indicator";
      this.loadingIndicator.className = "loading-indicator";
      this.loadingIndicator.setAttribute("aria-live", "polite");
      this.loadingIndicator.style.display = "none";
      this.chatContainer.appendChild(this.loadingIndicator);
    } else {
      this.loadingIndicator = document.getElementById("loading-indicator");
    }

    this.applyTheme();
  }

  bindEvents() {
    this.sendButton.addEventListener("click", () => this.sendMessage());
    this.inputField.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Add keyboard navigation
    this.inputField.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.inputField.blur();
      }
    });
  }

  async sendMessage() {
    const message = this.inputField.value.trim();
    if (!message || this.isLoading) return;

    this.addMessage(message, "user");
    this.inputField.value = "";
    this.setLoading(true);

    try {
      const response = await this.fetchChatResponse(message);
      this.addMessage(response, "assistant");
    } catch (error) {
      this.addMessage(
        "Sorry, I encountered an error. Please try again.",
        "error",
      );
      console.error("Chat error:", error);
    } finally {
      this.setLoading(false);
      // Return focus to input field after message is sent, especially in fullscreen mode
      this.inputField.focus();
    }
  }

  async fetchChatResponse(message) {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    // Log session info if available
    if (result.session_id) {
      console.log(`🔗 Response from session: ${result.session_id}`);
    }

    return result.response || "No response available.";
  }

  addMessage(content, type = "user") {
    const message = {
      content,
      type,
      timestamp: new Date(),
    };

    this.messages.push(message);
    this.renderMessage(message);

    // Enhanced scrolling with delay for DOM rendering
    this.scrollToBottom(100);

    // Save message to state manager if available
    if (this.stateManager) {
      this.saveMessageToHistory(message);
    }
  }

  renderMessage(message) {
    let content = message.content;

    // Configure marked.js options if available
    if (typeof marked !== "undefined") {
      marked.setOptions({
        breaks: true, // Convert line breaks to <br>
        gfm: true, // GitHub Flavored Markdown
        sanitize: false, // Allow HTML (safe in this context)
        smartLists: true, // Better list behavior
        smartypants: true, // Smart typographic punctuation
      });
    }

    if (message.type === "assistant" && typeof marked !== "undefined") {
      // Use marked.js for markdown rendering with enhanced formatting
      content = marked.parse(message.content);

      // Wrap in message container for better styling
      content = `<div class="chat-message chat-message--assistant">
                <div class="chat-message-content">${content}</div>
            </div>`;
    } else if (message.type === "user") {
      // For user messages, also support markdown but with different styling
      if (typeof marked !== "undefined") {
        content = marked.parse(message.content);
      }

      content = `<div class="chat-message chat-message--user">
                <div class="chat-message-content"><strong>You:</strong> ${content}</div>
            </div>`;
    } else if (message.type === "error") {
      // For error messages, add special formatting
      if (typeof marked !== "undefined") {
        content = marked.parse(message.content);
      }

      content = `<div class="chat-message chat-message--error">
                <div class="chat-message-content"><strong>Error:</strong> ${content}</div>
            </div>`;
    } else {
      // Fallback for other message types
      content = `<div class="chat-message">
                <div class="chat-message-content">${content}</div>
            </div>`;
    }

    // Append the formatted message
    this.messagesArea.innerHTML += content;

    // Add syntax highlighting for code blocks if highlight.js is available
    if (typeof hljs !== "undefined") {
      this.messagesArea.querySelectorAll("pre code").forEach((block) => {
        // Try to detect language from class or content
        const language = this.detectCodeLanguage(block);
        if (language) {
          block.className = `language-${language}`;
          block.parentElement.setAttribute("data-language", language);
        }
        hljs.highlightElement(block);
      });
    }

    // Add copy buttons to code blocks
    this.addCopyButtonsToCodeBlocks();
  }

  detectCodeLanguage(codeBlock) {
    const text = codeBlock.textContent || codeBlock.innerText;
    const lines = text.split("\n").filter((line) => line.trim().length > 0);

    if (lines.length === 0) return null;

    // Language detection patterns
    const patterns = {
      python: /^def |^import |^from |^class |^#|^    /,
      javascript: /^const |^let |^var |^function |^=>|^import |^export /,
      typescript:
        /^interface |^type |^const |^let |^function |^=>|^import |^export /,
      java: /^public class |^private |^public |^import java|^package /,
      css: /^\.|#|^@|^{/,
      html: /^<[^>]+>/,
      sql: /^SELECT |^INSERT |^UPDATE |^DELETE |^CREATE |^ALTER /,
      json: /^[\\{\\[]/,
      xml: /^<\\?xml|^<[^>]+>/,
      yaml: /^[\\w-]+:/,
      bash: /^#!\/bin\/bash|^cd |^ls |^echo |^sudo /,
      php: /^<\\?php|^function |^class |^\\$[a-zA-Z]/,
      c: /^#include |^int |^void |^char /,
      cpp: /^#include |^namespace |^std::|^using /,
      go: /^package |^import |^func /,
      rust: /^use |^fn |^let |^mut /,
    };

    for (const [lang, pattern] of Object.entries(patterns)) {
      if (pattern.test(text)) {
        return lang;
      }
    }

    // Check for common file extensions in first line
    const firstLine = lines[0].toLowerCase();
    const extensionPatterns = {
      python: /\.py$/,
      javascript: /\.js$/,
      typescript: /\.ts$/,
      css: /\.css$/,
      html: /\.html?$/,
      json: /\.json$/,
      xml: /\.xml$/,
      yaml: /\.ya?ml$/,
      bash: /\.sh$/,
      php: /\.php$/,
      c: /\.c$/,
      cpp: /\.cpp$/,
      go: /\.go$/,
      rust: /\.rs$/,
    };

    for (const [lang, pattern] of Object.entries(extensionPatterns)) {
      if (pattern.test(firstLine)) {
        return lang;
      }
    }

    return null;
  }

  addCopyButtonsToCodeBlocks() {
    this.messagesArea.querySelectorAll("pre").forEach((pre) => {
      // Skip if already has copy button
      if (pre.querySelector(".copy-button")) return;

      const copyButton = document.createElement("button");
      copyButton.className = "copy-button";
      copyButton.innerHTML = "📋";
      copyButton.title = "Copy code";
      copyButton.style.cssText = `
                position: absolute;
                top: 0.5em;
                right: 0.5em;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 0.3em 0.5em;
                cursor: pointer;
                font-size: 0.8em;
                transition: all 0.2s ease;
                z-index: 1;
            `;

      copyButton.addEventListener("click", () => {
        const code = pre.querySelector("code");
        if (code) {
          navigator.clipboard.writeText(code.textContent).then(() => {
            copyButton.innerHTML = "✅";
            setTimeout(() => {
              copyButton.innerHTML = "📋";
            }, 2000);
          });
        }
      });

      copyButton.addEventListener("mouseenter", () => {
        copyButton.style.background = "rgba(255, 255, 255, 0.2)";
        copyButton.style.transform = "translateY(-1px)";
      });

      copyButton.addEventListener("mouseleave", () => {
        copyButton.style.background = "rgba(255, 255, 255, 0.1)";
        copyButton.style.transform = "translateY(0)";
      });

      pre.style.position = "relative";
      pre.appendChild(copyButton);
    });
  }

  scrollToBottom(delay = 0) {
    // Enhanced scroll with optional delay for DOM rendering
    if (delay > 0) {
      setTimeout(() => {
        this.performScroll();
      }, delay);
    } else {
      // Use requestAnimationFrame for smooth scrolling after DOM updates
      requestAnimationFrame(() => {
        this.performScroll();
      });
    }
  }

  performScroll() {
    if (!this.messagesArea) return;

    try {
      // Scroll to bottom with smooth behavior
      this.messagesArea.scrollTop = this.messagesArea.scrollHeight;

      // Double-check scroll position in case content is still loading
      setTimeout(() => {
        if (
          this.messagesArea.scrollTop <
          this.messagesArea.scrollHeight - 100
        ) {
          this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
        }
      }, 50);
    } catch (error) {
      console.warn("Error scrolling to bottom:", error);
    }
  }

  setLoading(loading) {
    this.isLoading = loading;
    this.inputField.disabled = loading;
    this.sendButton.disabled = loading;

    if (loading) {
      this.loadingIndicator.style.display = "block";
      this.loadingIndicator.innerHTML =
        '<div class="loading-spinner"></div><span class="sr-only">Loading response...</span>';

      // Scroll to show loading indicator
      this.scrollToBottom(50);
    } else {
      this.loadingIndicator.style.display = "none";
      // Ensure focus returns to input when loading completes
      setTimeout(() => {
        this.inputField.focus();
      }, 100);
    }
  }

  clearMessages() {
    this.messages = [];
    this.messagesArea.innerHTML = "";
  }

  applyTheme() {
    if (this.chatContainer) {
      const bgOpacity = this.theme.isDay ? 0.95 : 0.85;
      this.chatContainer.style.backgroundColor = this.hexToRgba(
        this.theme.background,
        bgOpacity,
      );
      this.chatContainer.style.color = this.theme.text;
      this.chatContainer.style.borderColor = this.theme.text;

      // Update input field
      if (this.inputField) {
        this.inputField.style.backgroundColor = this.hexToRgba(
          this.theme.background,
          0.7,
        );
        this.inputField.style.color = this.theme.text;
        this.inputField.style.borderColor = this.theme.text;
      }

      // Update send button
      if (this.sendButton) {
        this.sendButton.style.backgroundColor = this.theme.line;
        this.sendButton.style.color = this.theme.background;
      }
    }
  }

  hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  updateTheme(newTheme) {
    this.theme = newTheme;
    this.applyTheme();
  }

  /**
   * Load chat history from state manager
   */
  loadChatHistory() {
    try {
      const chatHistory = this.stateManager.loadChatHistory();

      // Load current conversation if exists
      if (chatHistory.currentConversation) {
        const currentConv = chatHistory.conversations.find(
          (c) => c.id === chatHistory.currentConversation,
        );
        if (currentConv) {
          this.loadConversation(currentConv);
        }
      } else if (chatHistory.conversations.length > 0) {
        // Load the most recent conversation if no current one
        this.loadConversation(chatHistory.conversations[0]);
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
    }
  }

  /**
   * Load a specific conversation
   */
  loadConversation(conversation) {
    if (!conversation) return;

    this.currentConversationId = conversation.id;
    this.messages = [];

    // Clear current display
    if (this.messagesArea) {
      this.messagesArea.innerHTML = "";
    }

    // Load messages with timestamps as Date objects
    conversation.messages.forEach((msg) => {
      this.messages.push({
        ...msg,
        timestamp: new Date(msg.timestamp),
      });
      this.renderMessage(this.messages[this.messages.length - 1]);
    });

    // Enhanced scroll when loading conversation
    this.scrollToBottom(150);
    console.log(`Loaded conversation with ${this.messages.length} messages`);
  }

  /**
   * Save message to history via state manager
   */
  saveMessageToHistory(message) {
    try {
      // Create conversation if doesn't exist
      if (!this.currentConversationId) {
        const conversation = this.stateManager.createConversation();
        this.currentConversationId = conversation.id;
      }

      // Save message
      this.stateManager.addMessage(this.currentConversationId, {
        content: message.content,
        type: message.type,
      });
    } catch (error) {
      console.error("Error saving message to history:", error);
    }
  }

  /**
   * Start new conversation
   */
  startNewConversation() {
    try {
      if (this.stateManager) {
        const conversation = this.stateManager.createConversation();
        this.currentConversationId = conversation.id;

        // Clear current messages
        this.messages = [];
        if (this.messagesArea) {
          this.messagesArea.innerHTML = "";
        }

        console.log("Started new conversation:", conversation.id);
      }
    } catch (error) {
      console.error("Error starting new conversation:", error);
    }
  }

  /**
   * Clear current conversation
   */
  clearCurrentConversation() {
    this.messages = [];
    if (this.messagesArea) {
      this.messagesArea.innerHTML = "";
    }
  }

  /**
   * Clear all chat history
   */
  clearChatHistory() {
    try {
      if (this.stateManager) {
        this.stateManager.clearChatHistory();
      }
      this.clearCurrentConversation();
      this.currentConversationId = null;
      console.log("Chat history cleared");
    } catch (error) {
      console.error("Error clearing chat history:", error);
    }
  }

  /**
   * Export chat history
   */
  exportChatHistory() {
    try {
      if (this.stateManager) {
        return this.stateManager.exportChatHistory();
      }
      return false;
    } catch (error) {
      console.error("Error exporting chat history:", error);
      return false;
    }
  }

  /**
   * Import chat history
   */
  importChatHistory(file) {
    try {
      if (this.stateManager) {
        return this.stateManager.importChatHistory(file).then((history) => {
          // Reload conversation after import
          this.loadChatHistory();
          return history;
        });
      }
      return Promise.reject(new Error("State manager not available"));
    } catch (error) {
      console.error("Error importing chat history:", error);
      return Promise.reject(error);
    }
  }

  /**
   * Get conversation list
   */
  getConversations() {
    try {
      if (this.stateManager) {
        const history = this.stateManager.loadChatHistory();
        return history.conversations;
      }
      return [];
    } catch (error) {
      console.error("Error getting conversations:", error);
      return [];
    }
  }

  destroy() {
    if (this.chatContainer) {
      this.chatContainer.remove();
    }
  }
}
