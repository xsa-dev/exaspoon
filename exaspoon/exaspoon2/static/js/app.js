/**
 * ============================================
 * MAIN APPLICATION COORDINATOR
 * ============================================
 */

class DashboardApp {
  constructor() {
    // Log session ID if available
    if (typeof window.sessionId !== "undefined") {
      console.log(`🔗 Session ID: ${window.sessionId}`);
      this.sessionId = window.sessionId;
    } else {
      console.warn("⚠️ Session ID not found");
      this.sessionId = null;
    }

    // Initialize state manager
    this.stateManager = new StateManager();
    this.stateManager.initialize();

    // Load saved interface state or use defaults
    const savedState = this.stateManager.loadInterfaceState();
    this.interfaceState = savedState;

    // Apply saved theme or use default
    this.themeConfig = this.getThemeConfig(savedState.theme);
    this.applyTheme(this.themeConfig);

    // Initialize managers
    this.matrixRain = null;
    this.chartManager = null;
    this.chatInterface = null;
    this.uiManager = null;

    // Data state
    this.data = [];

    // Real-time client
    this.realtimeClient = null;

    this.initialize();
  }

  async initialize() {
    if (typeof d3 === "undefined") {
      console.error(
        "D3.js is not loaded. Please check your internet connection.",
      );
      return;
    }

    console.log("D3.js loaded successfully, version:", d3.version);

    try {
      // Initialize components in order
      this.initializeMatrixRain();
      this.initializeChart();
      this.initializeChat();
      this.initializeUI();

      // Bind global events
      this.bindGlobalEvents();

      // Load initial data
      await this.fetchChartData();

      // Initialize real-time client
      this.initializeRealtimeClient();

      // Initialize date display
      this.updateDateDisplay();

      // Set up date update interval (every minute)
      this.dateUpdateInterval = setInterval(() => {
        this.updateDateDisplay();
      }, 60000);

      // Restore saved interface state
      this.restoreInterfaceState();

      console.log("Dashboard initialized successfully");
    } catch (error) {
      console.error("Error initializing dashboard:", error);
      this.showFallbackData();
    }
  }

  initializeMatrixRain() {
    this.matrixRain = new MatrixRain("matrix-canvas", this.themeConfig.theme);
    this.matrixRain.start();
  }

  initializeChart() {
    // Destroy existing chart manager if it exists
    if (this.chartManager) {
      this.chartManager.destroy();
    }

    // Chart wrapper already exists in HTML, just use it
    this.chartManager = new ChartManager(
      ".chart-wrapper",
      this.themeConfig.theme,
      this.themeConfig.highlightColors,
    );
    this.chartManager.initialize();
  }

  initializeChat() {
    // Chat interface is now in HTML, just initialize it
    this.chatInterface = new ChatInterface(
      "#chat-response",
      this.themeConfig.theme,
      this.stateManager,
    );
    this.chatInterface.initialize();

    // Log session info in chat context
    if (this.sessionId) {
      console.log(
        `💬 Chat interface initialized for session: ${this.sessionId}`,
      );
    }
  }

  initializeUI() {
    const mainContainer = document.getElementById("main-container");

    this.uiManager = new UIManager(
      "#main-container",
      this.themeConfig.theme,
      this.stateManager,
    );
    this.uiManager.initialize();
  }

  bindGlobalEvents() {
    // Listen for refresh data events
    document.addEventListener("refreshData", async (event) => {
      await this.fetchChartData();
      this.uiManager.showNotification("Data refreshed successfully", "success");
    });

    // Listen for theme toggle events
    document.addEventListener("toggleTheme", (event) => {
      this.toggleTheme();
    });

    // Listen for chart resize events (layout changes)
    document.addEventListener("resizeChart", (event) => {
      if (this.chartManager) {
        this.chartManager.resize();
      }
    });

    // Listen for window resize
    window.addEventListener(
      "resize",
      this.debounce(() => {
        if (this.chartManager) {
          this.chartManager.destroy();
          this.initializeChart();
          if (this.data.length > 0) {
            this.chartManager.updateData(this.data);
          }
        }
      }, 250),
    );

    // Handle visibility change to pause/resume matrix animation
    document.addEventListener("visibilitychange", () => {
      if (this.matrixRain) {
        if (document.hidden) {
          this.matrixRain.stop();
        } else {
          this.matrixRain.start();
        }
      }
    });
  }

  async fetchChartData() {
    try {
      this.uiManager.showLoadingState("Downloading...");

      const response = await fetch("/api/chart/monthly-totals?months=12");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      const rawData = result.data || [];

      // Process data: remove duplicates and sort by time
      const uniqueData = rawData.filter(
        (item, index, self) =>
          index === self.findIndex((t) => t.month === item.month),
      );

      // Create two data arrays with different sorting for chart and table

      // For table: keep descending order (newest first) - as received from backend
      const tableData = uniqueData.map((item) => ({
        ...item,
        isQuarterMax: false,
        isQuarterMin: false,
      }));

      // For chart: chronological order (oldest first) - reverse the backend data
      const chartData = [...uniqueData].reverse().map((item) => ({
        ...item,
        isQuarterMax: false,
        isQuarterMin: false,
      }));

      // Mark min and max values for each quarter (3 months) based on chronological data
      for (let i = 0; i < chartData.length; i += 3) {
        const quarter = chartData.slice(i, i + 3);
        if (!quarter.length) continue;
        const values = quarter.map((entry) => entry.value);
        const maxVal = Math.max(...values);
        const minVal = Math.min(...values);
        quarter.forEach((entry) => {
          if (entry.value === maxVal) entry.isQuarterMax = true;
          if (entry.value === minVal) entry.isQuarterMin = true;
        });
      }

      // Store table data for other potential uses
      this.data = tableData;

      // Update chart with chronological data and table with descending data
      this.chartManager.updateData(chartData);
      this.uiManager.updateDataTable(tableData);
    } catch (error) {
      console.error("Error fetching chart data:", error);
      this.showFallbackData();
      this.uiManager.showNotification(
        "Using fallback data due to fetch error",
        "warning",
      );
    } finally {
      this.uiManager.hideLoadingState();
    }
  }

  showFallbackData() {
    const fallbackData = [
      { month: "FEB 26", value: 13 },
      { month: "JAN 26", value: -92 },
      { month: "DEC 25", value: 77 },
      { month: "NOV 25", value: -24 },
      { month: "OCT 25", value: 58 },
      { month: "SEP 25", value: -81 },
    ];

    this.data = fallbackData.map((item) => ({
      ...item,
      isQuarterMax: false,
      isQuarterMin: false,
    }));

    // Mark min and max values for each quarter
    for (let i = 0; i < this.data.length; i += 3) {
      const quarter = this.data.slice(i, i + 3);
      if (!quarter.length) continue;
      const values = quarter.map((entry) => entry.value);
      const maxVal = Math.max(...values);
      const minVal = Math.min(...values);
      quarter.forEach((entry) => {
        if (entry.value === maxVal) entry.isQuarterMax = true;
        if (entry.value === minVal) entry.isQuarterMin = true;
      });
    }

    if (this.chartManager) {
      this.chartManager.updateData(this.data);
    }
    if (this.uiManager) {
      this.uiManager.updateDataTable(this.data);
    }
  }

  toggleTheme() {
    // Toggle theme
    const newThemeName =
      this.themeConfig.theme === colorSchemes.night ? "day" : "night";
    this.themeConfig = this.getThemeConfig(newThemeName);

    // Apply new theme
    this.applyTheme(this.themeConfig);

    // Update interface state
    this.interfaceState.theme = newThemeName;
    this.saveInterfaceState();

    // Update all components
    if (this.matrixRain) {
      this.matrixRain.updateTheme(this.themeConfig.theme);
    }
    if (this.chartManager) {
      this.chartManager.updateTheme(
        this.themeConfig.theme,
        this.themeConfig.highlightColors,
      );
    }
    if (this.chatInterface) {
      this.chatInterface.updateTheme(this.themeConfig.theme);
    }
    if (this.uiManager) {
      this.uiManager.updateTheme(this.themeConfig.theme);
    }

    this.uiManager.showNotification(
      `Switched to ${this.themeConfig.isDay ? "day" : "night"} theme`,
      "info",
    );
  }

  applyTheme(themeConfig) {
    // Update body class for CSS-based theming
    document.body.className = themeConfig.isDay ? "day-theme" : "night-theme";
  }

  /**
   * Get theme configuration based on theme name
   */
  getThemeConfig(themeName) {
    const isDay = themeName === "day";
    return {
      theme: isDay ? colorSchemes.day : colorSchemes.night,
      isDay: isDay,
      highlightColors: isDay
        ? { max: "#28a745", min: "#dc3545" }
        : { max: "#00ffd5", min: "#ff2b6d" },
    };
  }

  /**
   * Save current interface state
   */
  saveInterfaceState() {
    this.stateManager.saveInterfaceState(this.interfaceState);
  }

  /**
   * Update interface state
   */
  updateInterfaceState(key, value) {
    this.interfaceState[key] = value;
    this.saveInterfaceState();
  }

  /**
   * Restore UI states from saved interface state
   */
  restoreInterfaceState() {
    if (!this.uiManager) return;

    // Restore menu state
    if (this.interfaceState.menuOpen) {
      this.uiManager.showMenu();
    }

    // Restore layout state
    if (
      this.interfaceState.layout === "fullscreen-data" &&
      this.uiManager.currentLayout !== "fullscreen-data"
    ) {
      this.uiManager.toggleLayout();
    }

    // Restore expanded states after a short delay to ensure elements are ready
    setTimeout(() => {
      // Restore chart expanded state
      if (this.interfaceState.chartExpanded) {
        const chartContainer = document.getElementById("chart-container");
        if (chartContainer && !chartContainer.classList.contains("expanded")) {
          this.uiManager.toggleChartSize();
        }
      }

      // Restore table expanded state
      if (this.interfaceState.tableExpanded) {
        const tableContainer = document.getElementById("table-container");
        if (tableContainer && !tableContainer.classList.contains("expanded")) {
          this.uiManager.toggleTableSize();
        }
      }

      // Restore chat expanded state (uses fullscreen class)
      if (this.interfaceState.chatExpanded) {
        const chatContainer = document.getElementById("chat-response");
        if (chatContainer && !chatContainer.classList.contains("fullscreen")) {
          toggleFullscreen("chat-response");
        }
      }
    }, 100);
  }

  // Utility function for debouncing
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Real-time client initialization
  initializeRealtimeClient() {
    if (!this.sessionId) {
      console.warn(
        "⚠️ No session ID available, skipping real-time client initialization",
      );
      return;
    }

    try {
      this.realtimeClient = new RealtimeClient({
        sessionId: this.sessionId,
        onConnect: (data) => {
          console.log("🔌 Real-time client connected");
          this.updateConnectionStatus("connected");
          this.uiManager.showNotification(
            "Real-time updates enabled",
            "success",
          );
        },
        onDisconnect: (event) => {
          console.log("🔌 Real-time client disconnected");
          this.updateConnectionStatus("disconnected");
          this.uiManager.showNotification(
            "Real-time updates disconnected",
            "warning",
          );
        },
        onMessage: (data) => {
          console.debug("📨 Real-time message received:", data);
        },
        onError: (error) => {
          console.error("❌ Real-time client error:", error);
          this.updateConnectionStatus("error");
          this.uiManager.showNotification(
            "Real-time connection error",
            "error",
          );
        },
        onDataChange: async (dataType, data) => {
          console.log(`🔄 Real-time ${dataType} change:`, data);
          await this.handleRealtimeDataChange(dataType, data);
        },
      });

      // Connect to the real-time service
      this.realtimeClient.connect();
    } catch (error) {
      console.error("❌ Failed to initialize real-time client:", error);
      this.updateConnectionStatus("error");
    }
  }

  // Handle real-time data changes
  async handleRealtimeDataChange(dataType, data) {
    switch (dataType) {
      case "transaction":
      case "account":
      case "category":
        // Refresh chart data when database changes occur
        console.log(`📊 Refreshing chart due to ${dataType} change`);
        await this.fetchChartData();
        break;

      case "refresh":
        // Manual refresh triggered
        const dataTypeStr = data.data_type || "all";
        console.log(`🔄 Manual refresh triggered for: ${dataTypeStr}`);
        await this.fetchChartData();
        break;

      default:
        console.log(`🔄 Unknown data change type: ${dataType}`);
        break;
    }
  }

  // Update connection status indicator
  updateConnectionStatus(status) {
    const statusIndicator = document.getElementById("realtime-status");
    const menuStatusIndicator = document.getElementById(
      "menu-connection-status",
    );
    const menuConnectionIcon = document.getElementById("menu-connection-icon");

    // Remove all status classes from main indicator
    statusIndicator.classList.remove(
      "connected",
      "disconnected",
      "error",
      "connecting",
    );

    // Remove all status classes from menu indicator
    if (menuStatusIndicator) {
      menuStatusIndicator.classList.remove(
        "connected",
        "disconnected",
        "error",
        "connecting",
      );
    }

    // Add current status class and update content for both indicators
    switch (status) {
      case "connected":
        statusIndicator.classList.add("connected");
        statusIndicator.innerHTML = "🔌 Live";
        statusIndicator.title = "Real-time updates connected";

        if (menuStatusIndicator) {
          menuStatusIndicator.classList.add("connected");
          menuStatusIndicator.innerHTML = "Live";
          menuStatusIndicator.title = "Connected to real-time updates";
        }
        if (menuConnectionIcon) {
          menuConnectionIcon.innerHTML = "🔌";
        }
        break;

      case "connecting":
        statusIndicator.classList.add("connecting");
        statusIndicator.innerHTML = "🔄 Connecting...";
        statusIndicator.title = "Connecting to real-time updates";

        if (menuStatusIndicator) {
          menuStatusIndicator.classList.add("connecting");
          menuStatusIndicator.innerHTML = "Connecting...";
          menuStatusIndicator.title = "Connecting to real-time updates";
        }
        if (menuConnectionIcon) {
          menuConnectionIcon.innerHTML = "🔄";
        }
        break;

      case "disconnected":
        statusIndicator.classList.add("disconnected");
        statusIndicator.innerHTML = "🔌 Offline";
        statusIndicator.title = "Real-time updates disconnected";

        if (menuStatusIndicator) {
          menuStatusIndicator.classList.add("disconnected");
          menuStatusIndicator.innerHTML = "Offline";
          menuStatusIndicator.title = "Real-time updates disconnected";
        }
        if (menuConnectionIcon) {
          menuConnectionIcon.innerHTML = "🔌";
        }
        break;

      case "error":
        statusIndicator.classList.add("error");
        statusIndicator.innerHTML = "❌ Error";
        statusIndicator.title = "Real-time connection error";

        if (menuStatusIndicator) {
          menuStatusIndicator.classList.add("error");
          menuStatusIndicator.innerHTML = "Error";
          menuStatusIndicator.title = "Real-time connection error";
        }
        if (menuConnectionIcon) {
          menuConnectionIcon.innerHTML = "❌";
        }
        break;

      default:
        statusIndicator.classList.add("disconnected");
        statusIndicator.innerHTML = "❓ Unknown";
        statusIndicator.title = "Connection status unknown";

        if (menuStatusIndicator) {
          menuStatusIndicator.classList.add("disconnected");
          menuStatusIndicator.innerHTML = "Unknown";
          menuStatusIndicator.title = "Connection status unknown";
        }
        if (menuConnectionIcon) {
          menuConnectionIcon.innerHTML = "❓";
        }
        break;
    }
  }

  // Update date display
  updateDateDisplay() {
    updateCurrentDateDisplay();
  }

  // Manual refresh method using real-time client
  async refreshDataRealtime() {
    if (this.realtimeClient && this.realtimeClient.isConnected) {
      // Use real-time client to trigger refresh
      this.realtimeClient.refreshData();
    } else {
      // Fallback to regular refresh
      await this.fetchChartData();
      this.uiManager.showNotification("Data refreshed", "info");
    }
  }

  destroy() {
    // Clear date update interval
    if (this.dateUpdateInterval) {
      clearInterval(this.dateUpdateInterval);
      this.dateUpdateInterval = null;
    }

    // Disconnect real-time client
    if (this.realtimeClient) {
      this.realtimeClient.disconnect();
      this.realtimeClient = null;
    }

    if (this.matrixRain) this.matrixRain.destroy();
    if (this.chartManager) this.chartManager.destroy();
    if (this.chatInterface) this.chatInterface.destroy();
    if (this.uiManager) this.uiManager.destroy();
  }
}

// Global function for fullscreen toggle
function toggleFullscreen(elementId) {
  const element = document.getElementById(elementId);
  if (!element) return;

  const isNowFullscreen = !element.classList.contains("fullscreen");

  if (element.classList.contains("fullscreen")) {
    element.classList.remove("fullscreen");
  } else {
    element.classList.add("fullscreen");
  }

  // Save fullscreen state for any element
  if (window.dashboardApp && window.dashboardApp.stateManager) {
    switch (elementId) {
      case "chat-response":
        window.dashboardApp.updateInterfaceState(
          "chatExpanded",
          isNowFullscreen,
        );
        break;
      default:
        // For other elements, we could add more cases if needed
        break;
    }
  }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Create global app instance
  window.dashboardApp = new DashboardApp();
});

// Handle page unload
window.addEventListener("beforeunload", () => {
  if (window.dashboardApp) {
    window.dashboardApp.destroy();
  }
});
