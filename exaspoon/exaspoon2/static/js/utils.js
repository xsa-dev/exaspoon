/**
 * ============================================
 * UTILITY FUNCTIONS
 * ============================================
 */

/**
 * Determine if current time is day time
 * @returns {boolean} True if day time (6 AM - 8 PM)
 */
function isDayTime() {
  const now = new Date();
  const hour = now.getHours();
  // Consider day time from 6 AM to 8 PM for better visibility
  return hour >= 6 && hour < 20;
}

/**
 * Convert hex color to rgba with alpha
 * @param {string} hex - Hex color code
 * @param {number} alpha - Alpha transparency (0-1)
 * @returns {string} RGBA color string
 */
function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Convert month string to number for sorting
 * @param {string} monthStr - Month string in format "MON YY"
 * @returns {number} Numeric value for sorting
 */
function parseMonth(monthStr) {
  const [month, year] = monthStr.split(" ");
  const monthIndex = monthOrder.indexOf(month);
  const yearNum = parseInt(year);
  return yearNum * 12 + monthIndex;
}

/**
 * Month order for sorting
 */
const monthOrder = [
  "JAN",
  "FEB",
  "MAR",
  "APR",
  "MAY",
  "JUN",
  "JUL",
  "AUG",
  "SEP",
  "OCT",
  "NOV",
  "DEC",
];

/**
 * Theme system configuration
 */
const colorSchemes = {
  night: {
    // Professional dark theme
    background: "#1a1a1a",
    grid: "#404040",
    line: "#b0b0b0",
    text: "#e0e0e0",
    matrix: "#b0b0b0",
  },
  day: {
    // Clean light theme
    background: "#ffffff",
    grid: "#e9ecef",
    line: "#6c757d",
    text: "#212529",
    matrix: "#6c757d",
  },
};

/**
 * Get current theme based on time of day
 * @returns {object} Theme configuration
 */
function getCurrentTheme() {
  const isDay = isDayTime();
  return {
    theme: isDay ? colorSchemes.day : colorSchemes.night,
    isDay,
    highlightColors: isDay
      ? { max: "#28a745", min: "#dc3545" }
      : { max: "#5cb85c", min: "#ff6b6b" },
  };
}

/**
 * Apply theme to document body
 * @param {object} theme - Theme configuration
 */
function applyTheme(theme) {
  document.body.style.background = theme.background;
}

/**
 * Format current date for display
 * @returns {string} Formatted current date (e.g., "November 22, 2025")
 */
function getCurrentDateString() {
  const now = new Date();
  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  const day = now.getDate();
  const month = months[now.getMonth()];
  const year = now.getFullYear();

  return `${month} ${day}, ${year}`;
}

/**
 * Update current date display
 */
function updateCurrentDateDisplay() {
  const dateElement = document.getElementById("current-date");
  if (dateElement) {
    dateElement.textContent = getCurrentDateString();
  }
}
