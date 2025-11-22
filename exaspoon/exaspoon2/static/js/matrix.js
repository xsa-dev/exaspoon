/**
 * ============================================
 * MATRIX RAIN ANIMATION
 * ============================================
 */

class MatrixRain {
    constructor(canvasId, theme) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return;
        }

        this.ctx = this.canvas.getContext("2d");
        this.theme = theme;
        this.animationId = null;

        this.setupCanvas();
        this.initializeDrops();
        this.bindEvents();
    }

    setupCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    initializeDrops() {
        this.fontSize = 14;
        this.columns = this.canvas.width / this.fontSize;
        this.drops = [];

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
        this.chars = matrixChars.split("");

        // Initialize drops
        for (let i = 0; i < this.columns; i++) {
            this.drops[i] = Math.random() * -100;
        }
    }

    draw() {
        // Semi-transparent background for trail effect
        this.ctx.fillStyle = this.theme.background + "08";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.fillStyle = this.theme.matrix;
        this.ctx.font = this.fontSize + "px monospace";

        for (let i = 0; i < this.drops.length; i++) {
            const text = this.chars[Math.floor(Math.random() * this.chars.length)];
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;

            // Trail gradient effect
            const opacity = Math.max(0, 1 - this.drops[i] * 0.01);
            this.ctx.globalAlpha = opacity;
            this.ctx.fillText(text, x, y);

            // Reset drops with random speed
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }

            this.drops[i]++;
        }

        this.ctx.globalAlpha = 1.0;
        this.animationId = requestAnimationFrame(() => this.draw());
    }

    start() {
        if (!this.animationId) {
            this.draw();
        }
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    updateTheme(newTheme) {
        this.theme = newTheme;
    }

    bindEvents() {
        window.addEventListener("resize", () => {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
            const newColumns = this.canvas.width / this.fontSize;
            while (this.drops.length < newColumns) {
                this.drops.push(Math.random() * -100);
            }
            this.drops.splice(newColumns);
        });
    }

    destroy() {
        this.stop();
        window.removeEventListener("resize", this.handleResize);
    }
}

