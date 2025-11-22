/**
 * ============================================
 * UI MANAGEMENT MODULE
 * ============================================
 */

class UIManager {
  constructor(containerSelector, theme, stateManager = null) {
    this.container = document.querySelector(containerSelector);
    this.theme = theme;
    this.data = [];
    this.stateManager = stateManager;
    this.currentLayout = "split";
  }

  initialize() {
    this.createDataTable();
    this.createControls();
    return this;
  }

  createDataTable() {
    // Use existing table from HTML
    const table = document.getElementById("data-table");
    if (!table) return;

    // Apply theme colors
    const bgOpacity = this.theme.isDay ? 0.9 : 0.2;
    table.style.backgroundColor = this.hexToRgba(
      this.theme.background,
      bgOpacity,
    );
    table.style.color = this.theme.text;
    table.style.borderColor = this.theme.text;
  }

  createControls() {
    // Controls already exist in HTML, just apply theme
    const controlsContainer = document.querySelector(".controls-container");
    if (controlsContainer) {
      this.applyThemeToControls();
    }
  }

  updateDataTable(data) {
    this.data = data;
    const tbody = document.getElementById("table-body");
    if (!tbody) return;

    // Clear existing data
    tbody.innerHTML = "";

    // Add new data with proper accessibility
    data.forEach((item, index) => {
      const row = document.createElement("tr");
      row.setAttribute("role", "row");

      const dateCell = document.createElement("td");
      dateCell.setAttribute("role", "cell");
      dateCell.textContent = item.month || item.date || "N/A";

      const descriptionCell = document.createElement("td");
      descriptionCell.setAttribute("role", "cell");
      descriptionCell.textContent = item.description || "Financial data";

      const categoryCell = document.createElement("td");
      categoryCell.setAttribute("role", "cell");
      categoryCell.textContent = item.category || "General";

      const amountCell = document.createElement("td");
      amountCell.setAttribute("role", "cell");
      amountCell.textContent = (item.value || 0).toLocaleString();
      amountCell.style.textAlign = "right";

      // Color code positive/negative values using CSS classes
      const value = item.value || 0;
      if (value > 0) {
        amountCell.className = "value-positive";
      } else if (value < 0) {
        amountCell.className = "value-negative";
      } else {
        amountCell.className = "value-zero";
      }

      // Highlight quarterly min/max values
      if (item.isQuarterMax || item.isQuarterMin) {
        const highlightColor = item.isQuarterMax ? "#28a745" : "#dc3545";
        row.style.backgroundColor = this.hexToRgba(highlightColor, 0.1);
        row.style.border = `1px solid ${this.hexToRgba(highlightColor, 0.3)}`;

        // Add screen reader notification
        row.setAttribute(
          "aria-label",
          `${item.month}: ${item.value} (${item.isQuarterMax ? "quarterly maximum" : "quarterly minimum"})`,
        );
      }

      row.appendChild(dateCell);
      row.appendChild(descriptionCell);
      row.appendChild(categoryCell);
      row.appendChild(amountCell);
      tbody.appendChild(row);
    });
  }

  hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  applyTheme() {
    const table = document.getElementById("data-table");
    if (table) {
      const bgOpacity = this.theme.isDay ? 0.9 : 0.2;
      table.style.backgroundColor = this.hexToRgba(
        this.theme.background,
        bgOpacity,
      );
      table.style.color = this.theme.text;
      table.style.borderColor = this.theme.text;
    }

    this.applyThemeToControls();
  }

  applyThemeToControls() {
    const controls = this.container.querySelectorAll(".control-button");
    controls.forEach((button) => {
      button.style.backgroundColor = this.theme.line;
      button.style.color = this.theme.background;
      button.style.borderColor = this.theme.text;
    });
  }

  async refreshData() {
    // Dispatch custom event for chart manager to handle
    const event = new CustomEvent("refreshData", {
      detail: { source: "ui" },
    });
    document.dispatchEvent(event);
  }

  toggleTheme() {
    // Dispatch custom event for theme toggle
    const event = new CustomEvent("toggleTheme", {
      detail: { source: "ui" },
    });
    document.dispatchEvent(event);
  }

  updateTheme(newTheme) {
    this.theme = newTheme;
    this.applyTheme();
    this.updateHighlightTheme();
  }

  showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.className = `notification notification--${type}`;
    notification.setAttribute("role", "alert");
    notification.setAttribute("aria-live", "assertive");
    notification.textContent = message;

    // Apply theme
    notification.style.backgroundColor = this.hexToRgba(this.theme.text, 0.9);
    notification.style.color = this.theme.background;

    // Position notification
    notification.style.position = "fixed";
    notification.style.top = "20px";
    notification.style.right = "20px";
    notification.style.padding = "12px 16px";
    notification.style.borderRadius = "6px";
    notification.style.zIndex = "1000";
    notification.style.maxWidth = "300px";

    document.body.appendChild(notification);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 3000);
  }

  showLoadingState(message = "Loading...") {
    const loadingOverlay = document.createElement("div");
    loadingOverlay.id = "loading-overlay";
    loadingOverlay.className = "loading-overlay";
    loadingOverlay.setAttribute("role", "status");
    loadingOverlay.setAttribute("aria-live", "polite");

    const spinner = document.createElement("div");
    spinner.className = "loading-spinner";

    const text = document.createElement("span");
    text.textContent = message;
    text.className = "loading-text";

    loadingOverlay.appendChild(spinner);
    loadingOverlay.appendChild(text);

    // Style overlay
    loadingOverlay.style.position = "fixed";
    loadingOverlay.style.top = "0";
    loadingOverlay.style.left = "0";
    loadingOverlay.style.width = "100%";
    loadingOverlay.style.height = "100%";
    loadingOverlay.style.backgroundColor = this.hexToRgba(
      this.theme.background,
      0.9,
    );
    loadingOverlay.style.display = "flex";
    loadingOverlay.style.flexDirection = "column";
    loadingOverlay.style.justifyContent = "center";
    loadingOverlay.style.alignItems = "center";
    loadingOverlay.style.zIndex = "9999";

    document.body.appendChild(loadingOverlay);
  }

  hideLoadingState() {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
      overlay.remove();
    }
  }

  toggleTableSize() {
    const tableContainer = document.getElementById("table-container");
    if (!tableContainer) return;

    const isCurrentlyExpanded = tableContainer.classList.contains("expanded");
    tableContainer.classList.toggle("expanded");

    // Save table expanded state
    const isNowExpanded = tableContainer.classList.contains("expanded");
    if (this.stateManager && window.dashboardApp) {
      window.dashboardApp.updateInterfaceState("tableExpanded", isNowExpanded);
    }

    // Add event listener to close on escape key when expanded
    if (isNowExpanded) {
      const handleEscape = (e) => {
        if (e.key === "Escape") {
          tableContainer.classList.remove("expanded");
          // Save collapsed state
          if (this.stateManager && window.dashboardApp) {
            window.dashboardApp.updateInterfaceState("tableExpanded", false);
          }
          document.removeEventListener("keydown", handleEscape);
        }
      };

      // Add temporary escape key listener
      setTimeout(() => {
        document.addEventListener("keydown", handleEscape);
      }, 100);

      // Show notification
      this.showNotification("Table expanded. Press ESC to collapse.", "info");
    }
  }

  toggleChartSize() {
    const chartContainer = document.getElementById("chart-container");
    if (!chartContainer) return;

    chartContainer.classList.toggle("expanded");

    // Save chart expanded state
    const isNowExpanded = chartContainer.classList.contains("expanded");
    if (this.stateManager && window.dashboardApp) {
      window.dashboardApp.updateInterfaceState("chartExpanded", isNowExpanded);
    }

    // Add event listener to close on escape key when expanded
    if (isNowExpanded) {
      const handleEscape = (e) => {
        if (e.key === "Escape") {
          chartContainer.classList.remove("expanded");
          // Save collapsed state
          if (this.stateManager && window.dashboardApp) {
            window.dashboardApp.updateInterfaceState("chartExpanded", false);
          }
          document.removeEventListener("keydown", handleEscape);
        }
      };

      // Add temporary escape key listener
      setTimeout(() => {
        document.addEventListener("keydown", handleEscape);
      }, 100);

      // Show notification
      this.showNotification("Chart expanded. Press ESC to collapse.", "info");

      // Trigger chart resize if chart exists
      setTimeout(() => {
        const event = new CustomEvent("resizeChart", {
          detail: { container: chartContainer },
        });
        document.dispatchEvent(event);
      }, 300);
    }
  }

  /**
   * Toggle chat fullscreen/expanded state
   */
  toggleChatSize() {
    const chatContainer = document.getElementById("chat-response");
    if (!chatContainer) return;

    chatContainer.classList.toggle("expanded");

    // Save chat expanded state
    const isNowExpanded = chatContainer.classList.contains("expanded");
    if (this.stateManager && window.dashboardApp) {
      window.dashboardApp.updateInterfaceState("chatExpanded", isNowExpanded);
    }

    // Add event listener to close on escape key when expanded
    if (isNowExpanded) {
      const handleEscape = (e) => {
        if (e.key === "Escape") {
          chatContainer.classList.remove("expanded");
          // Save collapsed state
          if (this.stateManager && window.dashboardApp) {
            window.dashboardApp.updateInterfaceState("chatExpanded", false);
          }
          document.removeEventListener("keydown", handleEscape);
        }
      };

      // Add temporary escape key listener
      setTimeout(() => {
        document.addEventListener("keydown", handleEscape);
      }, 100);

      // Show notification
      this.showNotification("Chat expanded. Press ESC to collapse.", "info");
    }
  }

  destroy() {
    const table = document.getElementById("data-table");
    if (table) {
      table.remove();
    }

    const controls = this.container.querySelector(".controls-container");
    if (controls) {
      controls.remove();
    }

    this.hideLoadingState();
  }

  // Slide-out Menu functionality
  toggleMenu() {
    const slideMenu = document.getElementById("slide-menu");
    const menuBackdrop = document.getElementById("menu-backdrop");
    const menuButton = document.querySelector(".menu-gear-button");

    if (!slideMenu || !menuBackdrop || !menuButton) return;

    const isOpen = slideMenu.classList.contains("open");

    if (isOpen) {
      this.closeMenu();
    } else {
      this.openMenu();
    }
  }

  openMenu() {
    const slideMenu = document.getElementById("slide-menu");
    const menuBackdrop = document.getElementById("menu-backdrop");
    const menuButton = document.querySelector(".menu-gear-button");

    if (!slideMenu || !menuBackdrop || !menuButton) return;

    slideMenu.classList.add("open");
    menuBackdrop.classList.add("show");
    menuButton.setAttribute("aria-expanded", "true");

    // Save menu state
    if (this.stateManager && window.dashboardApp) {
      window.dashboardApp.updateInterfaceState("menuOpen", true);
    }

    // Add escape key listener
    this.addMenuEscapeKeyListener();

    // Add tab key listener for focus trapping
    this.addMenuTabKeyListener();

    // Focus first menu item for accessibility
    const firstItem = slideMenu.querySelector(".menu-item");
    if (firstItem) {
      setTimeout(() => {
        firstItem.focus();
      }, 100);
    }

    // Prevent body scroll when menu is open
    document.body.style.overflow = "hidden";
  }

  closeMenu() {
    const slideMenu = document.getElementById("slide-menu");
    const menuBackdrop = document.getElementById("menu-backdrop");
    const menuButton = document.querySelector(".menu-gear-button");

    if (!slideMenu || !menuBackdrop || !menuButton) return;

    slideMenu.classList.remove("open");
    menuBackdrop.classList.remove("show");
    menuButton.setAttribute("aria-expanded", "false");

    // Save menu state
    if (this.stateManager && window.dashboardApp) {
      window.dashboardApp.updateInterfaceState("menuOpen", false);
    }

    // Remove event listeners
    this.removeMenuEscapeKeyListener();
    this.removeMenuTabKeyListener();

    // Restore body scroll
    document.body.style.overflow = "";

    // Return focus to menu button
    menuButton.focus();
  }

  addMenuEscapeKeyListener() {
    this.handleMenuEscapeKey = (event) => {
      if (event.key === "Escape") {
        this.closeMenu();
      }
    };

    document.addEventListener("keydown", this.handleMenuEscapeKey);
  }

  removeMenuEscapeKeyListener() {
    if (this.handleMenuEscapeKey) {
      document.removeEventListener("keydown", this.handleMenuEscapeKey);
      this.handleMenuEscapeKey = null;
    }
  }

  addMenuTabKeyListener() {
    const slideMenu = document.getElementById("slide-menu");
    if (!slideMenu) return;

    this.handleMenuTabKey = (event) => {
      if (event.key === "Tab") {
        const focusableElements = slideMenu.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
        );

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          // Tab
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    document.addEventListener("keydown", this.handleMenuTabKey);
  }

  removeMenuTabKeyListener() {
    if (this.handleMenuTabKey) {
      document.removeEventListener("keydown", this.handleMenuTabKey);
      this.handleMenuTabKey = null;
    }
  }

  // Menu action handlers
  resetChart() {
    this.closeMenu();
    if (window.dashboardApp && window.dashboardApp.chartManager) {
      window.dashboardApp.chartManager.destroy();
      window.dashboardApp.initializeChart();
      if (window.dashboardApp.data.length > 0) {
        window.dashboardApp.chartManager.updateData(window.dashboardApp.data);
      }
      this.showNotification("Chart reset successfully", "success");
    }
  }

  exportChart() {
    this.closeMenu();
    if (window.dashboardApp && window.dashboardApp.chartManager) {
      // Simple CSV export of current data
      const data = window.dashboardApp.data;
      if (data && data.length > 0) {
        const csvContent = [
          ["Month", "Value", "Quarter Max", "Quarter Min"],
          ...data.map((item) => [
            item.month,
            item.value,
            item.isQuarterMax ? "Yes" : "No",
            item.isQuarterMin ? "Yes" : "No",
          ]),
        ]
          .map((row) => row.join(","))
          .join("\n");

        // Create download link
        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `chart-data-${new Date().toISOString().split("T")[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        this.showNotification("Chart data exported successfully", "success");
      } else {
        this.showNotification("No data available to export", "warning");
      }
    }
  }

  showSettings() {
    this.closeMenu();
    this.showNotification("Settings panel coming soon!", "info");
  }

  showAbout() {
    this.closeMenu();
    this.showNotification(
      "ExaspoonAi Dashboard v1.0 - Data Visualization Platform",
      "info",
    );
  }

  /**
   * Clear chat history
   */
  clearChatHistory() {
    this.closeMenu();

    if (window.dashboardApp && window.dashboardApp.chatInterface) {
      const confirmed = confirm(
        "Are you sure you want to clear all chat history? This action cannot be undone.",
      );
      if (confirmed) {
        window.dashboardApp.chatInterface.clearChatHistory();
        this.showNotification("Chat history cleared successfully", "success");
      }
    } else {
      this.showNotification("Chat interface not available", "error");
    }
  }

  /**
   * Export chat history
   */
  exportChatHistory() {
    this.closeMenu();

    if (window.dashboardApp && window.dashboardApp.chatInterface) {
      const success = window.dashboardApp.chatInterface.exportChatHistory();
      if (success) {
        this.showNotification("Chat history exported successfully", "success");
      } else {
        this.showNotification("Failed to export chat history", "error");
      }
    } else {
      this.showNotification("Chat interface not available", "error");
    }
  }

  toggleLayout() {
    this.closeMenu();

    const mainContainer = document.getElementById("main-container");
    if (!mainContainer) return;

    const isFullscreen = mainContainer.classList.contains("fullscreen-data");

    if (isFullscreen) {
      // Switch back to split view
      mainContainer.classList.remove("fullscreen-data");
      this.currentLayout = "split";
      this.showNotification("Switched to split view layout", "info");
    } else {
      // Switch to full-screen financial data
      mainContainer.classList.add("fullscreen-data");
      this.currentLayout = "fullscreen-data";
      this.showNotification(
        "Switched to full-screen financial data layout",
        "info",
      );
    }

    // Save layout state
    if (this.stateManager && window.dashboardApp) {
      window.dashboardApp.updateInterfaceState("layout", this.currentLayout);
    }

    // Trigger chart resize after layout change
    setTimeout(() => {
      const event = new CustomEvent("resizeChart", {
        detail: { container: document.getElementById("chart-container") },
      });
      document.dispatchEvent(event);
    }, 300);
  }

  updateHighlightTheme() {
    // Update highlight.js theme based on current theme
    const highlightTheme = document.getElementById("highlight-theme");
    if (highlightTheme) {
      const isDark = !this.theme.isDay;
      const themeUrl = isDark
        ? "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"
        : "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css";

      // Only update if different
      if (highlightTheme.href !== themeUrl) {
        highlightTheme.href = themeUrl;
      }
    }
  }

  /**
   * Show connection details modal/notification
   */
  showConnectionDetails() {
    this.closeMenu();

    // Get current connection status
    const statusIndicator = document.getElementById("realtime-status");
    const menuStatusIndicator = document.getElementById(
      "menu-connection-status",
    );
    const app = window.dashboardApp;

    let status = "unknown";
    let details = [];

    if (app && app.realtimeClient) {
      if (app.realtimeClient.isConnected) {
        status = "connected";
        details = [
          "✅ Connection Status: Connected",
          `📡 Session ID: ${app.sessionId || "Unknown"}`,
          "🔄 Real-time updates: Active",
          "💬 Last heartbeat: Recent",
        ];
      } else {
        status = "disconnected";
        details = [
          "❌ Connection Status: Disconnected",
          `📡 Session ID: ${app.sessionId || "Unknown"}`,
          "🔄 Real-time updates: Inactive",
          "🔧 Attempting to reconnect...",
        ];
      }
    } else {
      status = "error";
      details = [
        "⚠️ Connection Status: Error",
        "📡 Session ID: Not available",
        "🔄 Real-time updates: Not initialized",
        "🔧 Please refresh the page",
      ];
    }

    // Create detailed notification
    const notification = document.createElement("div");
    notification.className = `notification notification--${status === "connected" ? "success" : status === "error" ? "error" : "warning"}`;
    notification.setAttribute("role", "alert");
    notification.setAttribute("aria-live", "assertive");
    notification.style.maxWidth = "400px";
    notification.style.whiteSpace = "pre-line";
    notification.style.textAlign = "left";
    notification.style.fontFamily = "monospace";
    notification.style.fontSize = "13px";
    notification.style.lineHeight = "1.4";

    details.forEach((detail, index) => {
      if (index > 0) {
        notification.appendChild(document.createElement("br"));
      }
      notification.appendChild(document.createTextNode(detail));
    });

    // Add reconnect button if disconnected
    if (status === "disconnected" && app) {
      const br = document.createElement("br");
      const br2 = document.createElement("br");
      notification.appendChild(br);
      notification.appendChild(br2);

      const reconnectBtn = document.createElement("button");
      reconnectBtn.textContent = "🔄 Reconnect";
      reconnectBtn.style.cssText = `
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                margin-top: 8px;
                font-family: monospace;
            `;
      reconnectBtn.onmouseover = () =>
        (reconnectBtn.style.transform = "scale(1.05)");
      reconnectBtn.onmouseout = () =>
        (reconnectBtn.style.transform = "scale(1)");
      reconnectBtn.onclick = () => {
        notification.remove();
        if (app.realtimeClient) {
          app.realtimeClient.connect();
          this.showNotification("Attempting to reconnect...", "info");
        }
      };

      notification.appendChild(reconnectBtn);
    }

    document.body.appendChild(notification);

    // Auto-remove after longer duration for detailed notification
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 8000);
  }
}
