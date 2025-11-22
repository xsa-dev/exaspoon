/**
 * ============================================
 * STATE MANAGER MODULE
 * ============================================
 */

class StateManager {
  constructor() {
    this.storageKeys = {
      INTERFACE: "dashboard_interface_state",
      CHAT: "dashboard_chat_history",
      SETTINGS: "dashboard_settings",
    };

    this.defaultState = {
      interface: {
        theme: "day",
        layout: "split",
        menuOpen: false,
        chartExpanded: false,
        tableExpanded: false,
        chatExpanded: false,
      },
      chat: {
        conversations: [],
        currentConversation: null,
        settings: {
          maxConversations: 5,
          maxMessagesPerConversation: 100,
          autoSave: true,
        },
      },
      settings: {
        lastSaved: null,
        version: "1.0.0",
      },
    };
  }

  /**
   * Initialize the state manager
   */
  initialize() {
    try {
      // Check localStorage availability
      this.testLocalStorageAvailability();
      console.log("StateManager initialized successfully");
    } catch (error) {
      console.warn("StateManager initialization failed:", error);
    }
  }

  /**
   * Check localStorage availability
   */
  testLocalStorageAvailability() {
    const testKey = "test";
    try {
      localStorage.setItem(testKey, "test");
      localStorage.removeItem(testKey);
    } catch (error) {
      throw new Error("localStorage is not available: " + error.message);
    }
  }

  /**
   * Save interface state
   */
  saveInterfaceState(interfaceState) {
    try {
      const state = {
        ...this.defaultState.interface,
        ...interfaceState,
        lastSaved: new Date().toISOString(),
      };

      localStorage.setItem(this.storageKeys.INTERFACE, JSON.stringify(state));
      console.log("Interface state saved:", state);
    } catch (error) {
      console.error("Error saving interface state:", error);
    }
  }

  /**
   * Load interface state
   */
  loadInterfaceState() {
    try {
      const savedState = localStorage.getItem(this.storageKeys.INTERFACE);
      if (savedState) {
        const state = JSON.parse(savedState);
        console.log("Interface state loaded:", state);
        return { ...this.defaultState.interface, ...state };
      }
    } catch (error) {
      console.error("Error loading interface state:", error);
    }

    return this.defaultState.interface;
  }

  /**
   * Save chat history
   */
  saveChatHistory(chatHistory) {
    try {
      const history = {
        conversations: chatHistory.conversations || [],
        currentConversation: chatHistory.currentConversation || null,
        settings: {
          ...this.defaultState.chat.settings,
          ...chatHistory.settings,
        },
        lastSaved: new Date().toISOString(),
      };

      // Limit number of conversations and messages
      history.conversations = this.limitConversations(
        history.conversations,
        history.settings,
      );

      localStorage.setItem(this.storageKeys.CHAT, JSON.stringify(history));
      console.log("Chat history saved:", {
        conversations: history.conversations.length,
        currentConversation: history.currentConversation,
      });
    } catch (error) {
      console.error("Error saving chat history:", error);
    }
  }

  /**
   * Load chat history
   */
  loadChatHistory() {
    try {
      const savedHistory = localStorage.getItem(this.storageKeys.CHAT);
      if (savedHistory) {
        const history = JSON.parse(savedHistory);
        console.log("Chat history loaded:", {
          conversations: history.conversations?.length || 0,
          currentConversation: history.currentConversation,
        });

        return {
          conversations: history.conversations || [],
          currentConversation: history.currentConversation,
          settings: { ...this.defaultState.chat.settings, ...history.settings },
        };
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
    }

    return this.defaultState.chat;
  }

  /**
   * Add new message to history
   */
  addMessage(conversationId, message) {
    try {
      const history = this.loadChatHistory();

      // Find or create conversation
      let conversation = history.conversations.find(
        (c) => c.id === conversationId,
      );
      if (!conversation) {
        conversation = {
          id: conversationId,
          messages: [],
          created: new Date().toISOString(),
          lastUpdated: new Date().toISOString(),
        };
        history.conversations.unshift(conversation);
      }

      // Add message
      conversation.messages.push({
        ...message,
        timestamp: new Date().toISOString(),
      });

      // Limit number of messages
      conversation.messages = this.limitMessages(
        conversation.messages,
        history.settings.maxMessagesPerConversation,
      );

      // Update last updated time
      conversation.lastUpdated = new Date().toISOString();

      // Set as current conversation
      history.currentConversation = conversationId;

      this.saveChatHistory(history);

      return conversation;
    } catch (error) {
      console.error("Error adding message:", error);
      return null;
    }
  }

  /**
   * Create new conversation
   */
  createConversation(title = null) {
    const conversationId = this.generateConversationId();
    const conversation = {
      id: conversationId,
      title: title || `Conversation ${new Date().toLocaleDateString()}`,
      messages: [],
      created: new Date().toISOString(),
      lastUpdated: new Date().toISOString(),
    };

    const history = this.loadChatHistory();
    history.conversations.unshift(conversation);
    history.currentConversation = conversationId;

    this.saveChatHistory(history);

    return conversation;
  }

  /**
   * Delete conversation
   */
  deleteConversation(conversationId) {
    try {
      const history = this.loadChatHistory();
      history.conversations = history.conversations.filter(
        (c) => c.id !== conversationId,
      );

      // If deleting current conversation, select a new one
      if (history.currentConversation === conversationId) {
        history.currentConversation =
          history.conversations.length > 0 ? history.conversations[0].id : null;
      }

      this.saveChatHistory(history);
      return true;
    } catch (error) {
      console.error("Error deleting conversation:", error);
      return false;
    }
  }

  /**
   * Clear entire chat history
   */
  clearChatHistory() {
    try {
      localStorage.removeItem(this.storageKeys.CHAT);
      console.log("Chat history cleared");
      return true;
    } catch (error) {
      console.error("Error clearing chat history:", error);
      return false;
    }
  }

  /**
   * Export chat history
   */
  exportChatHistory() {
    try {
      const history = this.loadChatHistory();
      const exportData = {
        version: "1.0.0",
        exportDate: new Date().toISOString(),
        ...history,
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `chat-history-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      return true;
    } catch (error) {
      console.error("Error exporting chat history:", error);
      return false;
    }
  }

  /**
   * Import chat history
   */
  importChatHistory(file) {
    return new Promise((resolve, reject) => {
      try {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const importData = JSON.parse(e.target.result);

            // Validate imported data
            if (this.validateImportData(importData)) {
              const history = {
                conversations: importData.conversations || [],
                currentConversation: importData.currentConversation,
                settings: {
                  ...this.defaultState.chat.settings,
                  ...importData.settings,
                },
              };

              this.saveChatHistory(history);
              resolve(history);
            } else {
              reject(new Error("Invalid import data format"));
            }
          } catch (parseError) {
            reject(
              new Error("Error parsing import file: " + parseError.message),
            );
          }
        };

        reader.onerror = () => reject(new Error("Error reading file"));
        reader.readAsText(file);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Clear all state (reset to default settings)
   */
  clearAllState() {
    try {
      localStorage.removeItem(this.storageKeys.INTERFACE);
      localStorage.removeItem(this.storageKeys.CHAT);
      localStorage.removeItem(this.storageKeys.SETTINGS);
      console.log("All state cleared");
      return true;
    } catch (error) {
      console.error("Error clearing state:", error);
      return false;
    }
  }

  /**
   * Get storage information
   */
  getStorageInfo() {
    try {
      const interfaceSize = this.getItemSize(this.storageKeys.INTERFACE);
      const chatSize = this.getItemSize(this.storageKeys.CHAT);
      const settingsSize = this.getItemSize(this.storageKeys.SETTINGS);

      return {
        totalSize: interfaceSize + chatSize + settingsSize,
        interface: interfaceSize,
        chat: chatSize,
        settings: settingsSize,
        available: this.getAvailableStorage(),
      };
    } catch (error) {
      console.error("Error getting storage info:", error);
      return null;
    }
  }

  // Private methods

  /**
   * Generate conversation ID
   */
  generateConversationId() {
    return "conv_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Limit number of conversations
   */
  limitConversations(conversations, settings) {
    const maxConversations = settings.maxConversations || 5;
    return conversations.slice(0, maxConversations);
  }

  /**
   * Limit number of messages
   */
  limitMessages(messages, maxMessages) {
    if (!maxMessages || messages.length <= maxMessages) {
      return messages;
    }
    return messages.slice(-maxMessages);
  }

  /**
   * Validate imported data
   */
  validateImportData(data) {
    if (!data || typeof data !== "object") {
      return false;
    }

    if (!Array.isArray(data.conversations)) {
      return false;
    }

    // Check conversation structure
    return data.conversations.every(
      (conv) =>
        conv.id &&
        Array.isArray(conv.messages) &&
        conv.created &&
        conv.lastUpdated,
    );
  }

  /**
   * Get localStorage item size
   */
  getItemSize(key) {
    try {
      const item = localStorage.getItem(key);
      return item ? new Blob([item]).size : 0;
    } catch (error) {
      return 0;
    }
  }

  /**
   * Get available localStorage space
   */
  getAvailableStorage() {
    try {
      const testKey = "storage_test";
      let testString = "";
      const maxSize = 1024 * 1024 * 5; // 5MB test

      // Try to write test data
      for (let i = 0; i < maxSize; i++) {
        testString += "x";
        try {
          localStorage.setItem(testKey, testString);
        } catch (e) {
          localStorage.removeItem(testKey);
          return i;
        }
      }

      localStorage.removeItem(testKey);
      return maxSize;
    } catch (error) {
      return 0;
    }
  }
}

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = StateManager;
}
