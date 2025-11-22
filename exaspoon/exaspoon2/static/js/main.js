/**
 * ============================================
 * DASHBOARD APPLICATION
 * Interactive data visualization and chat interface
 * ============================================
 */

// Wait for D3.js to be loaded and DOM to be ready
document.addEventListener("DOMContentLoaded", function () {
  if (typeof d3 === "undefined") {
    console.error(
      "D3.js is not loaded. Please check your internet connection.",
    );
    return;
  }

  // ============================================
  // UTILITY FUNCTIONS
  // ============================================

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

  // ============================================
  // GLOBAL VARIABLES & STATE
  // ============================================

  const isDay = isDayTime();
  let data = [];
  let config, svg, xScale, yScale, yAxis, xAxis, lineGenerator;
  let zeroLineBase = null;
  let zeroLineSheen = null;
  let zeroLineLength = 0;
  let zeroLineVisibleSegment = 0;

  // ============================================
  // THEME & COLOR SYSTEM
  // ============================================

  /**
   * Color scheme configurations for different times of day
   */
  const colorSchemes = {
    night: {
      // Classic matrix: green on black
      background: "#000000",
      grid: "#003300",
      line: "#00ff00",
      text: "#00ff00",
      matrix: "#00ff00",
    },
    day: {
      // Orange matrix: orange on light background
      background: "#fff8e1",
      grid: "#ffe0b2",
      line: "#ff9800",
      text: "#ff9800",
      matrix: "#ff6f00",
    },
  };

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

  // Theme selection and color setup
  const theme = isDay ? colorSchemes.day : colorSchemes.night;
  const highlightColors = isDay
    ? { max: "#ffb300", min: "#d84315" }
    : { max: "#00ffd5", min: "#ff2b6d" };

  // Apply background to body
  document.body.style.background = theme.background;

  // ============================================
  // Matrix Rain Animation
  // ============================================
  const canvas = document.getElementById("matrix-canvas");
  const ctx = canvas.getContext("2d");
  const mainContainer = document.getElementById("main-container");

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  // Matrix characters
  const matrixChars =
    "0123456789" + // Numbers
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + // Latin uppercase
    "abcdefghijklmnopqrstuvwxyz" + // Latin lowercase
    "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ" + // Greek uppercase
    "αβγδεζηθικλμνξοπρστυφχψω" + // Greek lowercase
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン" + // Japanese characters
    "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" + // Special characters
    "∀∃∈∉∑∏∫∂∇∆∞√≤≥≠≈±×÷" + // Math symbols
    "HELLOWORLDDATALANGUAGEENGLISH" + // English words
    "DIGITALTECHNOLOGYCYBERPUNK"; // Tech words
  const chars = matrixChars.split("");

  const fontSize = 14;
  const columns = canvas.width / fontSize;
  const drops = [];

  // Initialize drops
  for (let i = 0; i < columns; i++) {
    drops[i] = Math.random() * -100;
  }

  function drawMatrix() {
    // Semi-transparent background for trail effect
    ctx.fillStyle = theme.background + "08";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = theme.matrix;
    ctx.font = fontSize + "px monospace";

    for (let i = 0; i < drops.length; i++) {
      const text = chars[Math.floor(Math.random() * chars.length)];
      const x = i * fontSize;
      const y = drops[i] * fontSize;

      // Trail gradient effect
      const opacity = Math.max(0, 1 - drops[i] * 0.01);
      ctx.globalAlpha = opacity;
      ctx.fillText(text, x, y);

      // Reset drops with random speed
      if (y > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }

      drops[i]++;
    }

    ctx.globalAlpha = 1.0;
    requestAnimationFrame(drawMatrix);
  }

  // Start animation
  drawMatrix();

  // Update canvas size on window resize
  window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const newColumns = canvas.width / fontSize;
    while (drops.length < newColumns) {
      drops.push(Math.random() * -100);
    }
    drops.splice(newColumns);
  });

  // ============================================
  // Data Configuration
  // ============================================

  // Function to update chart with data - defined in global scope
  function updateChartWithData() {
    if (!config || !svg || !xScale || !yScale || !lineGenerator) return;

    // Update Y-axis scale
    const maxValue = d3.max(data, (d) => Math.abs(d.value));
    const absMaxValue = maxValue || 100;
    yScale.domain([-absMaxValue, absMaxValue]);

    // Update X-axis scale
    xScale.domain(data.map((d) => d.month));

    // Update chart line
    svg
      .select("path.chart-line")
      .datum(data)
      .transition()
      .duration(750)
      .attr("d", lineGenerator);

    // Update data points
    svg
      .selectAll("circle")
      .data(data)
      .transition()
      .duration(750)
      .attr("cx", (d) => xScale(d.month))
      .attr("cy", (d) => yScale(d.value))
      .attr("r", (d) =>
        d.isQuarterMax || d.isQuarterMin
          ? config.styles.pointRadius + 3
          : config.styles.pointRadius,
      )
      .attr("fill", (d) => {
        if (d.isQuarterMax) return highlightColors.max;
        if (d.isQuarterMin) return highlightColors.min;
        return config.colors.line;
      });

    // Update quarter labels
    const quarterHighlights = data.filter(
      (d) => d.isQuarterMax || d.isQuarterMin,
    );
    const quarterLabels = svg
      .selectAll("text.quarter-label")
      .data(quarterHighlights);

    quarterLabels.exit().remove();

    quarterLabels
      .enter()
      .append("text")
      .attr("class", "quarter-label")
      .merge(quarterLabels)
      .transition()
      .duration(750)
      .attr("x", (d) => xScale(d.month))
      .attr("y", (d) => yScale(d.value) + (d.isQuarterMin ? 18 : -12))
      .attr("text-anchor", "middle")
      .attr("fill", (d) =>
        d.isQuarterMax ? highlightColors.max : highlightColors.min,
      )
      .style("font-size", "10px")
      .style("font-family", "var(--font-mono)")
      .style("pointer-events", "none")
      .text((d) => {
        if (d.isQuarterMax && d.isQuarterMin) return "Q MAX/MIN";
        return d.isQuarterMax ? "Q MAX" : "Q MIN";
      });

    // Update X-axis
    xAxis.call(d3.axisBottom(xScale));
    xAxis
      .selectAll("text")
      .attr("fill", config.styles.xAxisText.fill)
      .style("font-size", config.styles.xAxisText.fontSize)
      .style("font-weight", config.styles.xAxisText.fontWeight)
      .style("font-family", config.styles.xAxisText.fontFamily)
      .style("text-anchor", "end")
      .attr("transform", "rotate(-60)");

    // Update grid lines
    const gridStep = absMaxValue / 10;
    const gridLines = [];
    for (let i = -absMaxValue; i <= absMaxValue; i += gridStep) {
      gridLines.push(i);
    }

    svg
      .selectAll("g")
      .filter(function () {
        return this.getAttribute("stroke") === config.colors.grid;
      })
      .selectAll("line")
      .data(gridLines)
      .transition()
      .duration(750)
      .attr("y1", (d) => yScale(d))
      .attr("y2", (d) => yScale(d));
  }

  // Function to fetch data from Supabase
  async function fetchChartData() {
    try {
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

      data = uniqueData
        .sort((a, b) => parseMonth(a.month) - parseMonth(b.month))
        .map((item) => ({
          ...item,
          isQuarterMax: false,
          isQuarterMin: false,
        }));

      // Mark min and max values for each quarter (3 months)
      for (let i = 0; i < data.length; i += 3) {
        const quarter = data.slice(i, i + 3);
        if (!quarter.length) continue;
        const values = quarter.map((entry) => entry.value);
        const maxVal = Math.max(...values);
        const minVal = Math.min(...values);
        quarter.forEach((entry) => {
          if (entry.value === maxVal) entry.isQuarterMax = true;
          if (entry.value === minVal) entry.isQuarterMin = true;
        });
      }

      // Update chart and data table
      updateChartWithData();
      updateDataTable();
    } catch (error) {
      console.error("Error fetching chart data:", error);
      // Use fallback data
      useFallbackData();
    }
  }

  // Function to use fallback data
  function useFallbackData() {
    const fallbackData = [
      { month: "FEB 26", value: 13 },
      { month: "JAN 26", value: -92 },
      { month: "DEC 25", value: 77 },
      { month: "NOV 25", value: -24 },
      { month: "OCT 25", value: 58 },
      { month: "SEP 25", value: -81 },
    ];

    data = fallbackData.map((item) => ({
      ...item,
      isQuarterMax: false,
      isQuarterMin: false,
    }));

    // Mark min and max values for each quarter
    for (let i = 0; i < data.length; i += 3) {
      const quarter = data.slice(i, i + 3);
      if (!quarter.length) continue;
      const values = quarter.map((entry) => entry.value);
      const maxVal = Math.max(...values);
      const minVal = Math.min(...values);
      quarter.forEach((entry) => {
        if (entry.value === maxVal) entry.isQuarterMax = true;
        if (entry.value === minVal) entry.isQuarterMin = true;
      });
    }

    updateChartWithData();
    updateDataTable();
  }

  // ============================================
  // Create Data Table
  // ============================================

  // Create and update zero line glow and sheen effect
  function runZeroSheen() {
    if (!zeroLineSheen || !zeroLineLength) return;
    const targetOffset = -(zeroLineLength + zeroLineVisibleSegment);
    zeroLineSheen.interrupt("zero-sheen");
    zeroLineSheen.attr("stroke-dashoffset", 0);
    zeroLineSheen
      .transition("zero-sheen")
      .duration(2600)
      .ease(d3.easeLinear)
      .attr("stroke-dashoffset", targetOffset)
      .on("end", runZeroSheen);
  }

  function updateZeroLine(margins = config.margin) {
    if (!config || !svg) return;
    const yZero = yScale(0);
    zeroLineLength = Math.max(1, config.width - margins.left - margins.right);
    zeroLineVisibleSegment = Math.max(60, zeroLineLength * 0.22);

    if (!zeroLineBase) {
      zeroLineBase = svg
        .append("line")
        .attr("class", "zero-line-base")
        .attr("stroke-linecap", "round")
        .style("pointer-events", "none");
    }

    zeroLineBase
      .attr("x1", margins.left)
      .attr("x2", config.width - margins.right)
      .attr("y1", yZero)
      .attr("y2", yZero)
      .attr("stroke", hexToRgba(theme.text, isDay ? 0.45 : 0.55))
      .attr("stroke-width", 3)
      .style("filter", `drop-shadow(0 0 8px ${hexToRgba(theme.text, 0.4)})`);

    if (!zeroLineSheen) {
      zeroLineSheen = svg
        .append("line")
        .attr("class", "zero-line-sheen")
        .attr("stroke", "rgba(255,255,255,0.95)")
        .attr("stroke-width", 5)
        .attr("stroke-linecap", "round")
        .style("mix-blend-mode", "screen")
        .style("pointer-events", "none");
    }

    zeroLineSheen
      .attr("x1", margins.left)
      .attr("x2", config.width - margins.right)
      .attr("y1", yZero)
      .attr("y2", yZero)
      .attr("stroke-dasharray", `${zeroLineVisibleSegment} ${zeroLineLength}`)
      .attr("stroke-dashoffset", 0)
      .style("opacity", isDay ? 0.9 : 0.8);

    runZeroSheen();
  }

  function createDataTable() {
    const table = document.createElement("table");
    table.id = "data-table";
    table.setAttribute("role", "table");
    table.setAttribute("aria-label", "Monthly data values");

    // Apply theme colors
    const bgOpacity = isDay ? 0.9 : 0.2;
    const bgColor = hexToRgba(theme.background, bgOpacity);
    table.style.backgroundColor = bgColor;
    table.style.color = theme.text;
    table.style.borderColor = theme.text;

    // Table header
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const th1 = document.createElement("th");
    th1.textContent = "Month";
    th1.setAttribute("scope", "col");
    th1.style.backgroundColor = hexToRgba(theme.text, 0.3);
    th1.style.color = theme.background;
    const th2 = document.createElement("th");
    th2.textContent = "Value";
    th2.setAttribute("scope", "col");
    th2.style.backgroundColor = hexToRgba(theme.text, 0.3);
    th2.style.color = theme.background;
    th2.style.textAlign = "right";
    headerRow.appendChild(th1);
    headerRow.appendChild(th2);
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Table caption for screen readers
    const caption = document.createElement("caption");
    caption.textContent = "Monthly data values showing financial metrics";
    caption.className = "sr-only";
    table.appendChild(caption);

    // Table body - initially empty
    const tbody = document.createElement("tbody");
    table.appendChild(tbody);

    // Add table to main-container
    mainContainer.appendChild(table);
  }

  // Function to update data table
  function updateDataTable() {
    const table = document.getElementById("data-table");
    if (!table) return;

    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    // Clear existing data
    tbody.innerHTML = "";

    // Add new data with proper accessibility
    data.forEach((item, index) => {
      const row = document.createElement("tr");
      row.setAttribute("role", "row");

      const cell1 = document.createElement("td");
      cell1.textContent = item.month;
      cell1.setAttribute("role", "cell");
      cell1.setAttribute("aria-label", `Month: ${item.month}`);
      cell1.style.borderColor = hexToRgba(theme.text, 0.4);

      const cell2 = document.createElement("td");
      const valueText = item.value >= 0 ? `+${item.value}` : `${item.value}`;
      cell2.textContent = valueText;
      cell2.setAttribute("role", "cell");
      cell2.setAttribute("aria-label", `Value: ${valueText}`);
      cell2.style.textAlign = "right";
      cell2.style.fontWeight = "bold";
      cell2.style.color = theme.line;
      cell2.style.borderColor = hexToRgba(theme.text, 0.4);

      // Add special styling for quarter highlights
      if (item.isQuarterMax) {
        row.setAttribute(
          "aria-label",
          `Month: ${item.month}, Value: ${valueText} - Quarter Maximum`,
        );
        row.setAttribute(
          "title",
          `Quarter Maximum: ${item.month} with value ${valueText}`,
        );
        cell2.style.backgroundColor = hexToRgba(highlightColors.max, 0.2);
      }
      if (item.isQuarterMin) {
        row.setAttribute(
          "aria-label",
          `Month: ${item.month}, Value: ${valueText} - Quarter Minimum`,
        );
        row.setAttribute(
          "title",
          `Quarter Minimum: ${item.month} with value ${valueText}`,
        );
        cell2.style.backgroundColor = hexToRgba(highlightColors.min, 0.2);
      }

      // Add tooltip for regular rows
      if (!item.isQuarterMax && !item.isQuarterMin) {
        row.setAttribute("title", `${item.month}: ${valueText}`);
      }

      row.appendChild(cell1);
      row.appendChild(cell2);
      tbody.appendChild(row);
    });
  }

  createDataTable();

  // ============================================
  // Chart Configuration
  // ============================================
  // Calculate width based on chart container (Grid manages dimensions)
  const chartContainer = document.getElementById("chart-container");
  const getChartWidth = () => {
    // Use requestAnimationFrame to get actual dimensions after Grid renders
    if (chartContainer && chartContainer.clientWidth > 0) {
      return chartContainer.clientWidth;
    }
    // Fallback: calculate based on window width, considering Grid margins (15px padding * 2 + 15px gap)
    return Math.floor(((window.innerWidth - 45) * 11) / 12);
  };

  // Slightly delay initialization to get correct Grid dimensions
  const initChart = () => {
    const chartWidth = getChartWidth();

    // Default to full chart display (textarea collapsed)
    const initialHeight = Math.floor(window.innerHeight * 0.65);

    const config = {
      width: chartWidth,
      height: initialHeight,
      margin: { top: 30, right: 15, bottom: 80, left: 60 },
      colors: theme,
      styles: {
        axisText: {
          fontSize: "14px",
          fill: theme.text,
          fontFamily: "'Courier New', monospace",
        },
        xAxisText: {
          fontSize: "16px",
          fontWeight: "700",
          fill: theme.text,
          fontFamily: "'Courier New', monospace",
        },
        lineWidth: 2.5,
        pointRadius: 6,
      },
    };

    // ============================================
    // Create SVG
    // ============================================
    const svg = d3
      .select("#chart-container")
      .append("svg")
      .attr("width", config.width)
      .attr("height", config.height)
      .attr("viewBox", `0 0 ${config.width} ${config.height}`)
      .attr("role", "img")
      .attr(
        "aria-label",
        "Interactive data chart showing monthly values with trend line",
      )
      .style("background", "transparent");

    return { config, svg };
  };

  // Initialize chart after creating table
  // Use requestAnimationFrame to get correct Grid dimensions
  requestAnimationFrame(() => {
    const result = initChart();
    config = result.config;
    svg = result.svg;

    // ============================================
    // Scales
    // ============================================
    // Initialize with default domain, will be updated with real data later
    xScale = d3
      .scalePoint()
      .domain([]) // Initially empty, will be updated
      .range([config.margin.left, config.width - config.margin.right]);

    yScale = d3
      .scaleLinear()
      .domain([-100, 100]) // Default range
      .range([config.height - config.margin.bottom, config.margin.top]);

    // ============================================
    // Grid
    // ============================================
    const defaultMax = 100;
    const gridStep = defaultMax / 10;
    const gridLines = [];
    for (let i = -defaultMax; i <= defaultMax; i += gridStep) {
      gridLines.push(i);
    }
    svg
      .append("g")
      .attr("stroke", config.colors.grid)
      .attr("stroke-width", 1)
      .attr("stroke-opacity", 0.3)
      .selectAll("line")
      .data(gridLines)
      .join("line")
      .attr("x1", config.margin.left)
      .attr("x2", config.width - config.margin.right)
      .attr("y1", (d) => yScale(d))
      .attr("y2", (d) => yScale(d))
      .attr("stroke-width", (d) => (d === 0 ? 2 : 1))
      .attr("stroke-opacity", (d) => (d === 0 ? 0.6 : 0.3));

    // Zero line glow and sheen
    updateZeroLine(config.margin);

    // ============================================
    // Axes
    // ============================================
    // Y-axis
    yAxis = svg
      .append("g")
      .attr("transform", `translate(${config.margin.left}, 0)`)
      .call(d3.axisLeft(yScale).ticks(5));

    yAxis
      .selectAll("text")
      .attr("fill", config.colors.text)
      .style("font-size", config.styles.axisText.fontSize)
      .style("font-family", config.styles.axisText.fontFamily);

    yAxis
      .selectAll(".domain, .tick line")
      .attr("stroke", config.colors.text)
      .attr("stroke-opacity", 0.6);

    // X-axis (at zero position)
    xAxis = svg
      .append("g")
      .attr("transform", `translate(0, ${yScale(0)})`)
      .call(d3.axisBottom(xScale));

    xAxis
      .selectAll("text")
      .attr("fill", config.styles.xAxisText.fill)
      .style("font-size", config.styles.xAxisText.fontSize)
      .style("font-weight", config.styles.xAxisText.fontWeight)
      .style("font-family", config.styles.xAxisText.fontFamily)
      .style("text-anchor", "end")
      .attr("transform", "rotate(-60)")
      .style("opacity", 0.6);

    xAxis
      .selectAll(".tick line")
      .attr("stroke", config.colors.text)
      .attr("stroke-opacity", 0.6);

    // Hide X-axis domain line (bottom thin line)
    xAxis.selectAll(".domain").attr("stroke", "none");

    // ============================================
    // Chart Line
    // ============================================
    lineGenerator = d3
      .line()
      .x((d) => xScale(d.month))
      .y((d) => yScale(d.value))
      .curve(d3.curveMonotoneX);

    // Create chart line (only once)
    const chartPath = svg
      .selectAll("path.chart-line")
      .data([data])
      .join("path")
      .attr("class", "chart-line")
      .attr("fill", "none")
      .attr("stroke", config.colors.line)
      .attr("stroke-width", config.styles.lineWidth)
      .attr("d", lineGenerator)
      .style("filter", `drop-shadow(0 0 3px ${config.colors.line})`);

    // ============================================
    // Data Points
    // ============================================
    svg
      .selectAll("circle")
      .data(data)
      .join("circle")
      .attr("cx", (d) => xScale(d.month))
      .attr("cy", (d) => yScale(d.value))
      .attr("r", (d) =>
        d.isQuarterMax || d.isQuarterMin
          ? config.styles.pointRadius + 3
          : config.styles.pointRadius,
      )
      .attr("fill", (d) => {
        if (d.isQuarterMax) return highlightColors.max;
        if (d.isQuarterMin) return highlightColors.min;
        return config.colors.line;
      })
      .attr("stroke", (d) =>
        d.isQuarterMax || d.isQuarterMin
          ? theme.background
          : config.colors.background,
      )
      .attr("stroke-width", (d) => (d.isQuarterMax || d.isQuarterMin ? 3 : 2))
      .style("filter", (d) =>
        d.isQuarterMax || d.isQuarterMin
          ? `drop-shadow(0 0 8px ${d.isQuarterMax ? highlightColors.max : highlightColors.min})`
          : `drop-shadow(0 0 4px ${config.colors.line})`,
      );

    const quarterHighlights = data.filter(
      (d) => d.isQuarterMax || d.isQuarterMin,
    );
    svg
      .selectAll("text.quarter-label")
      .data(quarterHighlights)
      .join("text")
      .attr("class", "quarter-label")
      .attr("x", (d) => xScale(d.month))
      .attr("y", (d) => yScale(d.value) + (d.isQuarterMin ? 18 : -12))
      .attr("text-anchor", "middle")
      .attr("fill", (d) =>
        d.isQuarterMax ? highlightColors.max : highlightColors.min,
      )
      .style("font-size", "10px")
      .style("font-family", "'Courier New', monospace")
      .style("pointer-events", "none")
      .text((d) => {
        if (d.isQuarterMax && d.isQuarterMin) return "Q MAX/MIN";
        return d.isQuarterMax ? "Q MAX" : "Q MIN";
      });

    // Create textarea and input after chart initialization, then fetch data
    createTextElements();

    // Initialize with fallback data, then try to fetch real data
    useFallbackData();
    fetchChartData();
  });

  // ============================================
  // Create Response Textarea and Input Field
  // ============================================
  function createTextElements() {
    // Check if chart is initialized
    if (!config || !svg) return;

    // Check if elements are already created
    if (
      document.getElementById("response-textarea") ||
      document.getElementById("input-field")
    ) {
      return; // Elements already created
    }

    // Response div (instead of textarea for markdown support)
    const responseDiv = document.createElement("div");
    responseDiv.id = "response-textarea";
    responseDiv.innerHTML = "Response will appear here...";
    responseDiv.setAttribute("aria-label", "Chat response area");
    responseDiv.setAttribute("aria-live", "polite");
    responseDiv.setAttribute("aria-describedby", "response-help");
    responseDiv.contentEditable = false;

    // Apply theme colors
    const bgOpacity = isDay ? 0.9 : 0.2;
    responseDiv.style.backgroundColor = hexToRgba(theme.background, bgOpacity);
    responseDiv.style.color = theme.text;
    responseDiv.style.borderColor = theme.text;

    // Create fullscreen button
    const fullscreenBtn = document.createElement("button");
    fullscreenBtn.className = "fullscreen-btn";
    fullscreenBtn.innerHTML = "FS";
    fullscreenBtn.title = "Toggle fullscreen (Esc to exit)";
    fullscreenBtn.setAttribute("aria-label", "Toggle fullscreen");
    fullscreenBtn.style.display = "flex";
    fullscreenBtn.style.position = "absolute";
    fullscreenBtn.style.top = "8px";
    fullscreenBtn.style.right = "8px";
    fullscreenBtn.style.zIndex = "9999";

    // Debug: Check if responseDiv exists and has proper styles
    console.log(
      "Response div position:",
      window.getComputedStyle(responseDiv).position,
    );
    console.log("Creating fullscreen button for:", responseDiv);

    // Add fullscreen button to response div
    responseDiv.appendChild(fullscreenBtn);

    // Debug: Check if button was added
    setTimeout(() => {
      const btn = document.querySelector(".fullscreen-btn");
      if (btn) {
        console.log("FS Button found! Styles:", window.getComputedStyle(btn));
        console.log("Button position:", btn.getBoundingClientRect());
      } else {
        console.error("FS Button NOT found!");
      }
    }, 100);

    // Input field (multi-line, resizable)
    const input = document.createElement("textarea");
    input.id = "input-field";
    input.rows = 2;
    input.placeholder = "Enter text... (Shift+Enter for new line)";
    input.setAttribute("aria-label", "Message input field");
    input.setAttribute("aria-describedby", "input-help");

    // Apply theme colors
    input.style.backgroundColor = hexToRgba(theme.background, bgOpacity);
    input.style.color = theme.text;
    input.style.borderColor = theme.text;
    input.style.borderTopColor = theme.text;
    input.style.borderLeft = "none";
    input.style.borderRight = "none";
    input.style.borderBottom = "none";
    input.style.caretColor = theme.text;

    // Input field handler (Enter sends text to Python backend)
    input.addEventListener("keydown", async (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        const currentText = responseDiv.innerHTML;
        const newText = input.value.trim();
        if (!newText) {
          e.preventDefault();
          return;
        }

        // Show processing message with loading state
        const processingMsg = "🤖 Processing...";
        responseDiv.innerHTML = currentText
          ? currentText + "\n" + processingMsg
          : processingMsg;
        input.value = "";
        responseDiv.classList.add("loading");
        input.disabled = true;
        e.preventDefault();

        try {
          // Send message to Python backend
          const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              message: newText,
            }),
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();

          // Clear processing message and loading state
          responseDiv.classList.remove("loading");
          input.disabled = false;
          const baseText = currentText || "";
          responseDiv.innerHTML = baseText;

          if (
            data.response &&
            data.response.includes("❌ Error processing request")
          ) {
            // Display error message
            responseDiv.innerHTML += "\n❌ Error: " + data.response;
          } else {
            // Display AI response with Markdown rendering
            const aiResponse = data.response || "No response";
            const userMessage = newText.replace(/\n/g, "<br>");
            const aiMessageHtml = marked.parse(aiResponse);

            responseDiv.innerHTML += `<br><br>👤 User: ${userMessage}<br><br>🤖 AI: ${aiMessageHtml}`;
          }
        } catch (error) {
          console.error("Error:", error);
          // Clear processing message, loading state and show connection error
          responseDiv.classList.remove("loading");
          input.disabled = false;
          const baseText = currentText || "";
          responseDiv.innerHTML =
            baseText + "\n❌ Connection error: " + error.message;
        }

        // Auto-scroll to bottom
        responseDiv.scrollTop = responseDiv.scrollHeight;
        // Return focus to input for better UX
        input.focus();
      }
    });

    // Function to redraw chart with animation
    const redrawChart = (
      newHeight,
      animate = true,
      hideXAxis = false,
      compressedMargins = null,
    ) => {
      const duration = animate ? 300 : 0; // Sync with CSS transition (0.3s)

      // Use compressed margins if provided, otherwise use standard margins
      const margins = compressedMargins || config.margin;

      // Animate SVG height change
      svg
        .transition()
        .duration(duration)
        .attr("height", newHeight)
        .on("end", () => {
          config.height = newHeight;
        });

      // Create interpolator for smooth scaling
      const startHeight = config.height;
      const startRange = [
        startHeight - config.margin.bottom,
        config.margin.top,
      ];
      const endRange = [newHeight - margins.bottom, margins.top];

      const interpolateRange = d3.interpolateArray(startRange, endRange);

      // Animate all chart elements
      const t = svg.transition().duration(duration);

      // Save start and end paths for line animation
      const pathElement = svg.select("path.chart-line");
      const startPath = pathElement.attr("d");
      yScale.range([newHeight - margins.bottom, margins.top]);
      const endPath = lineGenerator(data);
      yScale.range([startHeight - config.margin.bottom, config.margin.top]);

      // Animate chart line
      pathElement
        .transition()
        .duration(duration)
        .attrTween("d", () => {
          return (t) => {
            const currentRange = interpolateRange(t);
            yScale.range(currentRange);
            return lineGenerator(data);
          };
        });

      // Smoothly hide/show X-axis
      const axisOpacity = hideXAxis ? 0 : 0.6;
      xAxis
        .selectAll("text")
        .transition()
        .duration(duration)
        .style("opacity", axisOpacity);
      xAxis
        .selectAll(".domain, .tick line")
        .transition()
        .duration(duration)
        .attr("stroke-opacity", axisOpacity);

      // Update Y scaling during animation
      t.tween("height", () => {
        return (t) => {
          const currentRange = interpolateRange(t);
          yScale.range(currentRange);

          // Update grid
          svg
            .selectAll("g")
            .filter(function () {
              return this.getAttribute("stroke") === config.colors.grid;
            })
            .selectAll("line")
            .attr("y1", (d) => yScale(d))
            .attr("y2", (d) => yScale(d));

          // Update X-axis (position at zero level)
          xAxis.attr("transform", `translate(0, ${yScale(0)})`);

          // Update points - both X and Y coordinates
          svg
            .selectAll("circle")
            .attr("cx", (d) => xScale(d.month))
            .attr("cy", (d) => yScale(d.value));

          svg
            .selectAll("text.quarter-label")
            .attr("x", (d) => xScale(d.month))
            .attr("y", (d) => yScale(d.value) + (d.isQuarterMin ? 18 : -12));

          if (zeroLineBase) {
            const zeroY = yScale(0);
            zeroLineBase
              .attr("x1", margins.left)
              .attr("x2", config.width - margins.right)
              .attr("y1", zeroY)
              .attr("y2", zeroY);
          }

          if (zeroLineSheen) {
            const zeroY = yScale(0);
            zeroLineSheen
              .attr("x1", margins.left)
              .attr("x2", config.width - margins.right)
              .attr("y1", zeroY)
              .attr("y2", zeroY);
          }
        };
      });

      // After animation completes, update axes completely
      t.on("end", () => {
        config.height = newHeight;
        // Update config.margin for subsequent calls
        config.margin = margins;
        yScale.range([newHeight - margins.bottom, margins.top]);
        // Update xScale.range with new margins
        xScale.range([margins.left, config.width - margins.right]);

        // Clear old Y-axis elements before update
        yAxis.selectAll(".tick, .domain").remove();

        // Update grid with new margins
        svg
          .selectAll("g")
          .filter(function () {
            return this.getAttribute("stroke") === config.colors.grid;
          })
          .selectAll("line")
          .attr("x1", margins.left)
          .attr("x2", config.width - margins.right)
          .attr("y1", (d) => yScale(d))
          .attr("y2", (d) => yScale(d));

        // Update Y-axis
        yAxis.attr("transform", `translate(${margins.left}, 0)`);
        yAxis.call(d3.axisLeft(yScale).ticks(5));
        yAxis
          .selectAll("text")
          .attr("fill", config.colors.text)
          .style("font-size", config.styles.axisText.fontSize)
          .style("font-family", config.styles.axisText.fontFamily);
        yAxis
          .selectAll(".domain, .tick line")
          .attr("stroke", config.colors.text)
          .attr("stroke-opacity", 0.6);

        // Clear old X-axis elements before update
        xAxis.selectAll(".tick, .domain").remove();

        // Update X-axis
        xAxis.attr("transform", `translate(0, ${yScale(0)})`);
        xAxis.call(d3.axisBottom(xScale));

        // Hide or show X-axis
        const axisOpacity = hideXAxis ? 0 : 0.6;

        xAxis
          .selectAll("text")
          .attr("fill", config.styles.xAxisText.fill)
          .style("font-size", config.styles.xAxisText.fontSize)
          .style("font-weight", config.styles.xAxisText.fontWeight)
          .style("font-family", config.styles.xAxisText.fontFamily)
          .style("text-anchor", "end")
          .attr("transform", "rotate(-60)")
          .style("opacity", axisOpacity);
        xAxis
          .selectAll(".tick line")
          .attr("stroke", config.colors.text)
          .attr("stroke-opacity", axisOpacity);

        // Hide X-axis domain line (bottom thin line)
        xAxis.selectAll(".domain").attr("stroke", "none");

        // Final redraw of line and points
        const pathElement = svg.select("path.chart-line");
        if (pathElement.node()) {
          const finalPath = lineGenerator(data);
          pathElement.attr("d", finalPath);
        }

        svg
          .selectAll("circle")
          .attr("cx", (d) => xScale(d.month))
          .attr("cy", (d) => yScale(d.value));

        svg
          .selectAll("text.quarter-label")
          .attr("x", (d) => xScale(d.month))
          .attr("y", (d) => yScale(d.value) + (d.isQuarterMin ? 18 : -12));

        // Update zero line and restart sheen animation
        updateZeroLine(margins);
      });
    };

    // Handler for response div expand/collapse
    // By default response div is collapsed to give chart full screen
    let isExpanded = false;
    let isFullscreen = false;

    const toggleFullscreen = () => {
      isFullscreen = !isFullscreen;

      if (isFullscreen) {
        responseDiv.classList.remove("collapsed", "expanded");
        responseDiv.classList.add("fullscreen");

        // Hide the input field when in fullscreen
        input.style.display = "none";
      } else {
        responseDiv.classList.remove("fullscreen");
        input.style.display = "";

        // Return to the previous state
        if (isExpanded) {
          responseDiv.classList.add("expanded");
        } else {
          responseDiv.classList.add("collapsed");
        }
      }
    };

    const toggleTextarea = (e) => {
      e.preventDefault();
      e.stopPropagation();

      // If in fullscreen mode, exit fullscreen first
      if (isFullscreen) {
        toggleFullscreen();
        return;
      }

      isExpanded = !isExpanded;

      // Inverted logic: expanded = large response div, collapsed = compact
      if (isExpanded) {
        responseDiv.classList.remove("collapsed");
        responseDiv.classList.add("expanded");
        mainContainer.classList.add("chat-expanded");

        // When expanding response div, compress chart
        const newHeight = Math.floor(window.innerHeight * 0.35);

        // Reduced margins for compressed state
        const compressedMargins = {
          top: 5,
          bottom: 5,
          left: 60,
          right: 15,
        };

        // Redraw chart with animation, hide X-axis and use reduced margins
        redrawChart(newHeight, true, true, compressedMargins);
      } else {
        responseDiv.classList.remove("expanded");
        responseDiv.classList.add("collapsed");
        mainContainer.classList.remove("chat-expanded");

        // When collapsing response div, expand chart
        const fullHeight = Math.floor(window.innerHeight * 0.65);

        // Standard margins for expanded chart
        const expandedMargins = {
          top: 30,
          right: 15,
          bottom: 80,
          left: 60,
        };

        // Redraw chart with animation and show X-axis (use standard margins)
        redrawChart(fullHeight, true, false, expandedMargins);
      }
    };

    // Double-click on response expands/collapses the block
    responseDiv.addEventListener("dblclick", toggleTextarea);

    // Click on fullscreen button toggles fullscreen
    fullscreenBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleFullscreen();
    });

    // Escape key exits fullscreen
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && isFullscreen) {
        toggleFullscreen();
      }
    });

    // Add elements to main-container
    mainContainer.appendChild(responseDiv);
    mainContainer.appendChild(input);

    // Check agent status
    checkAgentStatus();
  }

  // Function to check agent status
  async function checkAgentStatus() {
    try {
      const response = await fetch("/api/status");
      const data = await response.json();

      let statusMessage = "";

      if (data.mcp_server_running) {
        statusMessage += `🔧 MCP Server: Running (PID: ${data.mcp_server_pid})\n`;
      } else {
        statusMessage += `❌ MCP Server: Not running\n`;
      }

      if (data.agent_initialized) {
        statusMessage += `🤖 Agent: Ready\n`;
        // If agent is ready, check tools
        await loadAgentTools();
      } else {
        statusMessage += `⏳ Agent: Initializing...\n`;
        // Show button for manual initialization
        showReinitializeButton();
        // Check status every 5 seconds
        setTimeout(checkAgentStatus, 5000);
      }

      const responseDiv = document.getElementById("response-textarea");
      if (responseDiv && !responseDiv.innerHTML.includes("User:")) {
        responseDiv.innerHTML = statusMessage;
      }
    } catch (error) {
      console.error("Status check failed:", error);
      const responseDiv = document.getElementById("response-textarea");
      if (responseDiv && !responseDiv.innerHTML) {
        responseDiv.innerHTML =
          "❌ Unable to connect to server, please check if backend is running.";
      }
    }
  }

  // Load available agent tools
  async function loadAgentTools() {
    try {
      const response = await fetch("/api/agent/tools");
      const data = await response.json();

      if (data.tools && data.tools.length > 0) {
        console.log("Available agent tools:", data.tools);
        // Can display tools somewhere in UI
      }
    } catch (error) {
      console.error("Failed to load tools:", error);
    }
  }

  // Show reinitialize button
  function showReinitializeButton() {
    const responseDiv = document.getElementById("response-textarea");
    if (responseDiv && !responseDiv.innerHTML.includes("🔄")) {
      responseDiv.innerHTML += "\n🔄 Click here to reinitialize agent";

      // Add click handler for reinitialization
      responseDiv.addEventListener("click", async function handler(e) {
        if (
          e.target === responseDiv &&
          responseDiv.innerHTML.includes("reinitialize")
        ) {
          responseDiv.innerHTML = "🔄 Reinitializing agent...";
          try {
            const response = await fetch("/api/agent/reinitialize", {
              method: "POST",
            });
            const data = await response.json();

            if (data.success) {
              responseDiv.innerHTML = "✅ Agent successfully reinitialized!";
              setTimeout(checkAgentStatus, 2000);
            } else {
              responseDiv.innerHTML = `❌ Reinitialization error: ${data.message}`;
            }
          } catch (error) {
            responseDiv.innerHTML = `❌ Error: ${error.message}`;
          }

          responseDiv.removeEventListener("click", handler);
        }
      });
    }
  }

  // Update chart and table dimensions on window resize
  window.addEventListener("resize", () => {
    // Update canvas size for Matrix effect
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const newColumns = canvas.width / fontSize;
    while (drops.length < newColumns) {
      drops.push(Math.random() * -100);
    }
    drops.splice(newColumns);

    // Check if chart is initialized
    if (
      !config ||
      !svg ||
      !xScale ||
      !yScale ||
      !yAxis ||
      !xAxis ||
      !lineGenerator
    )
      return;

    // Get current chart container width from Grid
    const newChartWidth = getChartWidth();

    // Update SVG size
    svg.attr("width", newChartWidth);
    config.width = newChartWidth;

    // Update scaling
    xScale.range([config.margin.left, config.width - config.margin.right]);

    // Update grid
    svg
      .selectAll("g")
      .filter(function () {
        return this.getAttribute("stroke") === config.colors.grid;
      })
      .selectAll("line")
      .attr("x2", config.width - config.margin.right);

    // Clear old axis elements before updating
    yAxis.selectAll(".tick, .domain").remove();
    xAxis.selectAll(".tick, .domain").remove();

    // Update axes
    yAxis
      .attr("transform", `translate(${config.margin.left}, 0)`)
      .call(d3.axisLeft(yScale).ticks(5));
    xAxis
      .attr("transform", `translate(0, ${yScale(0)})`)
      .call(d3.axisBottom(xScale));

    // Update axis styles
    yAxis.selectAll("text").attr("fill", config.colors.text);
    yAxis.selectAll(".domain, .tick line").attr("stroke", config.colors.text);
    xAxis
      .selectAll("text")
      .attr("fill", config.styles.xAxisText.fill)
      .style("font-size", config.styles.xAxisText.fontSize)
      .style("font-weight", config.styles.xAxisText.fontWeight)
      .style("font-family", config.styles.xAxisText.fontFamily)
      .style("text-anchor", "end")
      .attr("transform", "rotate(-60)");
    xAxis.selectAll(".tick line").attr("stroke", config.colors.text);

    // Hide X-axis domain line (bottom thin line)
    xAxis.selectAll(".domain").attr("stroke", "none");

    // Update chart line
    svg.select("path.chart-line").attr("d", lineGenerator);

    // Update points
    svg
      .selectAll("circle")
      .attr("cx", (d) => xScale(d.month))
      .attr("cy", (d) => yScale(d.value));

    svg
      .selectAll("text.quarter-label")
      .attr("x", (d) => xScale(d.month))
      .attr("y", (d) => yScale(d.value) + (d.isQuarterMin ? 18 : -12));
  });
}); // Close DOMContentLoaded event listener
