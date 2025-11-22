/**
 * ============================================
 * CHART VISUALIZATION MODULE
 * ============================================
 */

class ChartManager {
  constructor(containerSelector, theme, highlightColors) {
    this.container = d3.select(containerSelector);
    this.theme = theme;
    this.highlightColors = highlightColors;
    this.data = [];

    // Apply theme class to container
    this.container.node().classList.add("night-theme");

    // Chart configuration
    this.config = {
      margin: { top: 20, right: 100, bottom: 60, left: 60 },
      styles: {
        pointRadius: 4,
        xAxisText: {
          fill: theme.text,
          fontSize: "11px",
          fontWeight: "400",
          fontFamily: "var(--font-mono)",
        },
      },
    };

    // Dynamic margin configuration
    this.updateMargins();

    // Chart elements
    this.svg = null;
    this.xScale = null;
    this.yScale = null;
    this.xAxis = null;
    this.yAxis = null;
    this.lineGenerator = null;
    this.zeroLineBase = null;
    this.zeroLineSheen = null;
    this.zeroLineLength = 0;
    this.zeroLineVisibleSegment = 0;

    this.colors = {
      line: theme.line,
      grid: theme.grid,
      text: theme.text,
    };
  }

  initialize() {
    console.log("Initializing chart with container:", this.container.node());

    // Clear any existing SVG content
    this.container.selectAll("*").remove();

    // Set up dimensions
    const containerRect = this.container.node().getBoundingClientRect();
    this.config.width =
      containerRect.width - this.config.margin.left - this.config.margin.right;
    this.config.height =
      containerRect.height - this.config.margin.top - this.config.margin.bottom;

    console.log("Chart dimensions:", {
      width: this.config.width,
      height: this.config.height,
      containerRect: containerRect,
    });

    // Create SVG
    this.svg = this.container
      .append("svg")
      .attr("width", "100%")
      .attr("height", "100%")
      .attr(
        "viewBox",
        `0 0 ${this.config.width + this.config.margin.left + this.config.margin.right} ${this.config.height + this.config.margin.top + this.config.margin.bottom}`,
      )
      .style("overflow", "visible");

    // Create scales
    this.xScale = d3.scaleBand().range([0, this.config.width]).padding(0.1);

    this.yScale = d3.scaleLinear().range([this.config.height, 0]);

    // Create axes
    this.xAxis = this.svg
      .append("g")
      .attr("class", "x-axis")
      .attr(
        "transform",
        `translate(${this.config.margin.left}, ${this.config.height + this.config.margin.top})`,
      );

    this.yAxis = this.svg
      .append("g")
      .attr("class", "y-axis")
      .attr(
        "transform",
        `translate(${this.config.margin.left}, ${this.config.margin.top})`,
      );

    // Create line generator
    this.lineGenerator = d3
      .line()
      .x((d) => this.xScale(d.month) + this.xScale.bandwidth() / 2)
      .y((d) => this.yScale(d.relativeValue || d.value)) // Use relativeValue if available, fallback to value
      .curve(d3.curveMonotoneX);

    // Create chart group
    this.chartGroup = this.svg
      .append("g")
      .attr("class", "chart-group")
      .attr(
        "transform",
        `translate(${this.config.margin.left}, ${this.config.margin.top})`,
      );

    // Create grid lines
    this.createGridLines();

    // Create chart line
    this.chartLine = this.chartGroup
      .append("path")
      .attr("class", "chart-line")
      .attr("fill", "none")
      .attr("stroke", this.colors.line)
      .attr("stroke-width", 4)
      .style("stroke", this.colors.line)
      .style("stroke-opacity", 1)
      .style("stroke-width", "4px")
      .style("z-index", 10);

    // Create zero line
    this.updateZeroLine();

    return this;
  }

  createGridLines() {
    const gridGroup = this.chartGroup.append("g").attr("class", "grid-lines");

    // Add grid lines function
    this.updateGridLines = (maxValue, usePercentage = false) => {
      const gridLines = [];

      if (usePercentage) {
        // Percentage scale: 0%, 10%, 20%, ..., 100%
        const gridStep = 10;
        for (let i = 0; i <= maxValue; i += gridStep) {
          gridLines.push(i);
        }
      } else {
        // Absolute scale: show both positive and negative grid lines
        const gridStep = maxValue / 10;
        for (let i = -maxValue; i <= maxValue; i += gridStep) {
          gridLines.push(i);
        }
      }

      const gridLinesSelection = gridGroup.selectAll("line").data(gridLines);

      gridLinesSelection
        .enter()
        .append("line")
        .merge(gridLinesSelection)
        .attr("x1", 0)
        .attr("x2", this.config.width)
        .attr("y1", (d) => this.yScale(d))
        .attr("y2", (d) => this.yScale(d))
        .attr("stroke", this.colors.grid)
        .attr("stroke-dasharray", "2,4")
        .attr("opacity", 0.5);

      gridLinesSelection.exit().remove();
    };
  }

  updateZeroLine() {
    let yZero;

    if (this.data && this.data.length > 0) {
      const useAbsoluteScaling = this.data[0]?.useAbsoluteScaling || false;

      if (useAbsoluteScaling) {
        // For absolute scaling, zero is at the actual zero position
        yZero = this.yScale(0);
      } else {
        // For percentage scaling, calculate where zero would be in the relative scale
        let zeroRelativePosition = 50; // Default to middle (50%)
        if (
          this.data[0].minValue !== undefined &&
          this.data[0].maxValue !== undefined
        ) {
          const { minValue, maxValue } = this.data[0];
          if (minValue <= 0 && maxValue >= 0) {
            // Zero is within the range, calculate relative position
            zeroRelativePosition =
              ((0 - minValue) / (maxValue - minValue)) * 100;
          } else if (minValue > 0) {
            // All values are positive, zero is below range
            zeroRelativePosition = -5; // Position slightly below 0%
          } else {
            // All values are negative, zero is above range
            zeroRelativePosition = 105; // Position slightly above 100%
          }
        }
        yZero = this.yScale(zeroRelativePosition);
      }
    } else {
      // Fallback if no data
      yZero = this.yScale(50);
    }

    this.zeroLineLength = Math.max(1, this.config.width);
    this.zeroLineVisibleSegment = Math.max(60, this.zeroLineLength * 0.22);

    if (!this.zeroLineBase) {
      this.zeroLineBase = this.chartGroup
        .append("line")
        .attr("class", "zero-line-base")
        .attr("stroke-linecap", "round")
        .style("pointer-events", "none");
    }

    this.zeroLineBase
      .attr("x1", 0)
      .attr("x2", this.config.width)
      .attr("y1", yZero)
      .attr("y2", yZero)
      .attr(
        "stroke",
        this.hexToRgba(this.theme.text, this.theme.isDay ? 0.45 : 0.55),
      )
      .attr("stroke-width", 3)
      .style(
        "filter",
        `drop-shadow(0 0 8px ${this.hexToRgba(this.theme.text, 0.4)})`,
      );

    if (!this.zeroLineSheen) {
      this.zeroLineSheen = this.chartGroup
        .append("line")
        .attr("class", "zero-line-sheen")
        .attr("stroke", "rgba(255,255,255,0.95)")
        .attr("stroke-width", 5)
        .attr("stroke-linecap", "round")
        .style("mix-blend-mode", "screen")
        .style("pointer-events", "none");
    }

    this.zeroLineSheen
      .attr("x1", 0)
      .attr("x2", this.config.width)
      .attr("y1", yZero)
      .attr("y2", yZero)
      .attr(
        "stroke-dasharray",
        `${this.zeroLineVisibleSegment} ${this.zeroLineLength}`,
      )
      .attr("stroke-dashoffset", 0)
      .style("opacity", this.theme.isDay ? 0.9 : 0.8);

    this.runZeroSheen();
  }

  runZeroSheen() {
    if (!this.zeroLineSheen || !this.zeroLineLength) return;
    const targetOffset = -(this.zeroLineLength + this.zeroLineVisibleSegment);
    this.zeroLineSheen.interrupt("zero-sheen");
    this.zeroLineSheen.attr("stroke-dashoffset", 0);
    this.zeroLineSheen
      .transition("zero-sheen")
      .duration(2600)
      .ease(d3.easeLinear)
      .attr("stroke-dashoffset", targetOffset)
      .on("end", () => this.runZeroSheen());
  }

  hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  calculateRelativeValues(data) {
    if (!data || data.length === 0) {
      return data;
    }

    // Find min and max values from the data
    const values = data.map((d) => d.value);
    const minPrice = Math.min(...values);
    const maxPrice = Math.max(...values);

    // Handle edge case where all values are the same
    if (minPrice === maxPrice) {
      return data.map((d) => ({
        ...d,
        relativeValue: 50, // Set all values to middle of range (50%)
        minValue: minPrice,
        maxValue: maxPrice,
      }));
    }

    // Check if there are negative values
    const hasNegativeValues = minPrice < 0;

    if (hasNegativeValues) {
      // For datasets with negative values, use absolute scaling to show full range
      return data.map((d) => ({
        ...d,
        relativeValue: d.value, // Use absolute values
        minValue: minPrice,
        maxValue: maxPrice,
        useAbsoluteScaling: true,
      }));
    } else {
      // For all-positive datasets, use relative percentage scaling
      return data.map((d) => {
        const relativeValue =
          ((d.value - minPrice) / (maxPrice - minPrice)) * 100;
        return {
          ...d,
          relativeValue: relativeValue,
          minValue: minPrice,
          maxValue: maxPrice,
          useAbsoluteScaling: false,
        };
      });
    }
  }

  updateData(newData) {
    this.data = newData;
    console.log("Chart updateData called with:", newData);

    if (!this.data || this.data.length === 0) {
      console.warn("No data available for chart");
      return;
    }

    // Calculate relative values
    const dataWithRelative = this.calculateRelativeValues(this.data);
    this.data = dataWithRelative;

    // Determine scaling mode based on data
    const useAbsoluteScaling = this.data[0]?.useAbsoluteScaling || false;

    let yDomain;
    if (useAbsoluteScaling) {
      // For absolute scaling, show the full range including negatives
      const { minValue, maxValue } = this.data[0];
      const absMax = Math.max(Math.abs(minValue), Math.abs(maxValue));
      yDomain = [-absMax, absMax];
    } else {
      // For relative scaling, use 0-100% range
      yDomain = [0, 100];
    }

    // Update scales
    this.yScale.domain(yDomain);
    this.xScale.domain(this.data.map((d) => d.month));

    // Update axes with appropriate formatting
    if (useAbsoluteScaling) {
      this.yAxis.call(d3.axisLeft(this.yScale)); // Absolute values
    } else {
      this.yAxis.call(d3.axisLeft(this.yScale).tickFormat((d) => d + "%")); // Percentage
    }
    this.xAxis.call(d3.axisBottom(this.xScale));

    // Style x-axis text
    this.xAxis
      .selectAll("text")
      .attr("fill", this.config.styles.xAxisText.fill)
      .style("font-size", this.config.styles.xAxisText.fontSize)
      .style("font-weight", this.config.styles.xAxisText.fontWeight)
      .style("font-family", this.config.styles.xAxisText.fontFamily)
      .style("text-anchor", "end")
      .attr("transform", "rotate(-60)");

    // Update grid lines based on scaling mode
    if (this.updateGridLines) {
      if (useAbsoluteScaling) {
        const { minValue, maxValue } = this.data[0];
        const absMax = Math.max(Math.abs(minValue), Math.abs(maxValue));
        this.updateGridLines(absMax, false); // Absolute range
      } else {
        this.updateGridLines(100, true); // Percentage range (0-100)
      }
    }

    // Update chart line
    if (this.chartLine) {
      const pathData = this.lineGenerator(this.data);
      console.log("Chart path data:", pathData);
      console.log("Chart line color:", this.colors.line);

      this.chartLine
        .datum(this.data)
        .transition()
        .duration(750)
        .attr("d", pathData)
        .attr("stroke", this.colors.line)
        .attr("stroke-width", 4)
        .style("stroke", this.colors.line)
        .style("stroke-opacity", 1)
        .style("stroke-width", "4px")
        .style("z-index", 10);
    } else {
      console.error("Chart line element not found");
    }

    // Update data points
    const circles = this.chartGroup.selectAll("circle").data(this.data);

    circles.exit().remove();

    circles
      .enter()
      .append("circle")
      .merge(circles)
      .transition()
      .duration(750)
      .attr("cx", (d) => this.xScale(d.month) + this.xScale.bandwidth() / 2)
      .attr("cy", (d) => this.yScale(d.relativeValue || d.value))
      .attr("r", (d) =>
        d.isQuarterMax || d.isQuarterMin
          ? this.config.styles.pointRadius + 3
          : this.config.styles.pointRadius,
      )
      .attr("fill", (d) => {
        if (d.isQuarterMax) return this.highlightColors.max;
        if (d.isQuarterMin) return this.highlightColors.min;
        return this.colors.line;
      });

    // Update quarter labels
    const quarterHighlights = this.data.filter(
      (d) => d.isQuarterMax || d.isQuarterMin,
    );
    const quarterLabels = this.chartGroup
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
      .attr("x", (d) => this.xScale(d.month) + this.xScale.bandwidth() / 2)
      .attr(
        "y",
        (d) =>
          this.yScale(d.relativeValue || d.value) + (d.isQuarterMin ? 18 : -12),
      )
      .attr("text-anchor", "middle")
      .attr("fill", (d) =>
        d.isQuarterMax ? this.highlightColors.max : this.highlightColors.min,
      )
      .style("font-size", "10px")
      .style("font-family", "var(--font-mono)")
      .style("pointer-events", "none")
      .text((d) => {
        if (d.isQuarterMax && d.isQuarterMin) return "Q MAX/MIN";
        return d.isQuarterMax ? "Q MAX" : "Q MIN";
      });

    // Update zero line
    this.updateZeroLine();
  }

  updateTheme(newTheme, newHighlightColors) {
    this.theme = newTheme;
    this.highlightColors = newHighlightColors;
    this.colors = {
      line: newTheme.line,
      grid: newTheme.grid,
      text: newTheme.text,
    };

    // Update theme class on container
    const containerElement = this.container.node();
    containerElement.classList.remove("day-theme", "night-theme");
    containerElement.classList.add(
      this.theme === colorSchemes.day ? "day-theme" : "night-theme",
    );

    // Update existing elements with new theme
    if (this.svg) {
      if (this.chartLine) {
        this.chartLine
          .style("stroke", this.colors.line)
          .attr("stroke", this.colors.line);
      }

      this.xAxis
        .selectAll("text")
        .attr("fill", (this.config.styles.xAxisText.fill = this.colors.text));

      this.updateZeroLine();
    }
  }

  updateMargins() {
    const mainContainer = document.getElementById("main-container");
    const isFullscreen =
      mainContainer && mainContainer.classList.contains("fullscreen-data");

    if (isFullscreen) {
      // Reduce margins for better full-screen utilization
      this.config.margin = {
        top: 20,
        right: 40,
        bottom: 40,
        left: 50,
      };
      this.config.styles.pointRadius = 6;
      this.config.styles.xAxisText.fontSize = "14px";
    } else {
      // Standard margins for split view
      this.config.margin = {
        top: 20,
        right: 100,
        bottom: 60,
        left: 60,
      };
      this.config.styles.pointRadius = 4;
      this.config.styles.xAxisText.fontSize = "11px";
    }
  }

  resize() {
    if (!this.svg) return;

    // Update margins based on current layout
    this.updateMargins();

    // Get new container dimensions
    const containerRect = this.container.node().getBoundingClientRect();
    this.config.width =
      containerRect.width - this.config.margin.left - this.config.margin.right;
    this.config.height =
      containerRect.height - this.config.margin.top - this.config.margin.bottom;

    // Update SVG viewBox
    this.svg.attr(
      "viewBox",
      `0 0 ${this.config.width + this.config.margin.left + this.config.margin.right} ${this.config.height + this.config.margin.top + this.config.margin.bottom}`,
    );

    // Update scales with new dimensions
    this.xScale.range([0, this.config.width]);
    this.yScale.range([this.config.height, 0]);

    // Update axes positions
    this.xAxis.attr(
      "transform",
      `translate(${this.config.margin.left}, ${this.config.height + this.config.margin.top})`,
    );
    this.yAxis.attr(
      "transform",
      `translate(${this.config.margin.left}, ${this.config.margin.top})`,
    );

    // Redraw the chart with data
    if (this.data.length > 0) {
      this.updateData(this.data);
    }
  }

  // Real-time update methods
  updateDataRealtime(newData, options = {}) {
    const { animated = true, duration = 300 } = options;

    console.log("🔄 Real-time chart update:", newData);

    // Store old data for comparison
    const oldData = [...this.data];

    // Update the data
    this.data = newData;

    if (!this.data || this.data.length === 0) {
      console.warn("⚠️ No data available for real-time chart update");
      return;
    }

    // Calculate relative values
    const dataWithRelative = this.calculateRelativeValues(this.data);
    this.data = dataWithRelative;

    // Determine scaling mode based on data
    const useAbsoluteScaling = this.data[0]?.useAbsoluteScaling || false;

    let yDomain;
    if (useAbsoluteScaling) {
      const { minValue, maxValue } = this.data[0];
      const absMax = Math.max(Math.abs(minValue), Math.abs(maxValue));
      yDomain = [-absMax, absMax];
    } else {
      yDomain = [0, 100];
    }

    // Update scales
    this.yScale.domain(yDomain);
    this.xScale.domain(this.data.map((d) => d.month));

    // Update axes
    if (useAbsoluteScaling) {
      this.yAxis.call(d3.axisLeft(this.yScale));
    } else {
      this.yAxis.call(d3.axisLeft(this.yScale).tickFormat((d) => d + "%"));
    }
    this.xAxis.call(d3.axisBottom(this.xScale));

    // Style x-axis text
    this.xAxis
      .selectAll("text")
      .attr("fill", this.config.styles.xAxisText.fill)
      .style("font-size", this.config.styles.xAxisText.fontSize)
      .style("font-weight", this.config.styles.xAxisText.fontWeight)
      .style("font-family", this.config.styles.xAxisText.fontFamily)
      .style("text-anchor", "end")
      .attr("transform", "rotate(-60)");

    // Update grid lines
    if (this.updateGridLines) {
      if (useAbsoluteScaling) {
        const { minValue, maxValue } = this.data[0];
        const absMax = Math.max(Math.abs(minValue), Math.abs(maxValue));
        this.updateGridLines(absMax, false);
      } else {
        this.updateGridLines(100, true);
      }
    }

    // Animate the transition if requested
    const transition = animated
      ? this.chartLine.transition().duration(duration)
      : this.chartLine;

    // Update chart line with animation
    if (this.chartLine) {
      const pathData = this.lineGenerator(this.data);
      transition
        .attr("d", pathData)
        .attr("stroke", this.colors.line)
        .attr("stroke-width", 4)
        .style("stroke", this.colors.line)
        .style("stroke-opacity", 1)
        .style("stroke-width", "4px")
        .style("z-index", 10);
    }

    // Update data points with animation
    const circles = this.chartGroup.selectAll("circle").data(this.data);

    circles.exit().remove();

    const circlesEnter = circles
      .enter()
      .append("circle")
      .attr("cx", (d) => this.xScale(d.month) + this.xScale.bandwidth() / 2)
      .attr("cy", this.yScale(0)) // Start from zero
      .attr("r", 0) // Start with radius 0
      .attr("fill", this.colors.line);

    const circlesUpdate = circlesEnter.merge(circles);

    if (animated) {
      circlesUpdate
        .transition()
        .duration(duration)
        .attr("cx", (d) => this.xScale(d.month) + this.xScale.bandwidth() / 2)
        .attr("cy", (d) => this.yScale(d.relativeValue || d.value))
        .attr("r", (d) =>
          d.isQuarterMax || d.isQuarterMin
            ? this.config.styles.pointRadius + 3
            : this.config.styles.pointRadius,
        )
        .attr("fill", (d) => {
          if (d.isQuarterMax) return this.highlightColors.max;
          if (d.isQuarterMin) return this.highlightColors.min;
          return this.colors.line;
        });
    } else {
      circlesUpdate
        .attr("cx", (d) => this.xScale(d.month) + this.xScale.bandwidth() / 2)
        .attr("cy", (d) => this.yScale(d.relativeValue || d.value))
        .attr("r", (d) =>
          d.isQuarterMax || d.isQuarterMin
            ? this.config.styles.pointRadius + 3
            : this.config.styles.pointRadius,
        )
        .attr("fill", (d) => {
          if (d.isQuarterMax) return this.highlightColors.max;
          if (d.isQuarterMin) return this.highlightColors.min;
          return this.colors.line;
        });
    }

    // Update quarter labels
    const quarterHighlights = this.data.filter(
      (d) => d.isQuarterMax || d.isQuarterMin,
    );
    const quarterLabels = this.chartGroup
      .selectAll("text.quarter-label")
      .data(quarterHighlights);

    quarterLabels.exit().remove();

    const labelsEnter = quarterLabels
      .enter()
      .append("text")
      .attr("class", "quarter-label")
      .attr("opacity", 0);

    const labelsUpdate = labelsEnter.merge(quarterLabels);

    if (animated) {
      labelsUpdate
        .transition()
        .duration(duration)
        .attr("x", (d) => this.xScale(d.month) + this.xScale.bandwidth() / 2)
        .attr(
          "y",
          (d) =>
            this.yScale(d.relativeValue || d.value) +
            (d.isQuarterMin ? 18 : -12),
        )
        .attr("text-anchor", "middle")
        .attr("fill", (d) =>
          d.isQuarterMax ? this.highlightColors.max : this.highlightColors.min,
        )
        .style("font-size", "10px")
        .style("font-family", "var(--font-mono)")
        .style("pointer-events", "none")
        .attr("opacity", 1)
        .text((d) => {
          if (d.isQuarterMax && d.isQuarterMin) return "Q MAX/MIN";
          return d.isQuarterMax ? "Q MAX" : "Q MIN";
        });
    } else {
      labelsUpdate
        .attr("x", (d) => this.xScale(d.month) + this.xScale.bandwidth() / 2)
        .attr(
          "y",
          (d) =>
            this.yScale(d.relativeValue || d.value) +
            (d.isQuarterMin ? 18 : -12),
        )
        .attr("text-anchor", "middle")
        .attr("fill", (d) =>
          d.isQuarterMax ? this.highlightColors.max : this.highlightColors.min,
        )
        .style("font-size", "10px")
        .style("font-family", "var(--font-mono)")
        .style("pointer-events", "none")
        .attr("opacity", 1)
        .text((d) => {
          if (d.isQuarterMax && d.isQuarterMin) return "Q MAX/MIN";
          return d.isQuarterMax ? "Q MAX" : "Q MIN";
        });
    }

    // Update zero line
    this.updateZeroLine();

    // Show a brief highlight to indicate data was updated
    if (animated && options.highlight !== false) {
      this._showUpdateIndicator();
    }
  }

  _showUpdateIndicator() {
    // Create a temporary highlight effect to show data was updated
    const chartWrapper = this.container.node().parentElement;
    if (!chartWrapper) return;

    chartWrapper.style.transition = "box-shadow 0.3s ease-in-out";
    chartWrapper.style.boxShadow = "0 0 20px rgba(52, 152, 219, 0.5)";

    setTimeout(() => {
      chartWrapper.style.boxShadow = "";
    }, 500);
  }

  // Force refresh of chart data (useful for manual refresh)
  async refreshData() {
    try {
      const response = await fetch("/api/chart/monthly-totals?months=12");
      const result = await response.json();

      if (result.data) {
        this.updateDataRealtime(result.data, {
          animated: true,
          duration: 500,
          highlight: true,
        });
        return true;
      }
      return false;
    } catch (error) {
      console.error("❌ Failed to refresh chart data:", error);
      return false;
    }
  }

  destroy() {
    if (this.svg) {
      this.svg.remove();
    }
  }
}
