---
theme: slidev-theme-neofallout
background: ./images/4.png
title: "ExaSpoon: AI CFO for Hybrid Finance"
info: |
  ## ExaSpoon: AI CFO for Hybrid Finance (SpoonOS/Neo)
  5-minute hackathon presentation for AI-powered financial management.
class: text-center
drawings:
  persist: false
transition: slide-left
mdc: true
duration: 5min

layout: image-left
image: ./images/9.png
---

# ExaSpoon: AI CFO for Hybrid Finance {.text-5xl.font-black.text-white.drop-shadow-2xl.mb-2.text-center}

## SPOONOS/NEO {.text-3xl.font-bold.text-cyan-300.mb-2.drop-shadow-lg.text-center}

### AI-Powered Financial Command Center {.text-2xl.font-semibold.text-yellow-300.mb-4.text-center}

<div class="bg-black/60 backdrop-blur-md rounded-2xl p-4 max-w-3xl mx-auto border border-white/20">
  <div v-click class="text-red-400 font-bold text-lg mb-3 flex items-center gap-2 bg-red-900/20 p-2 rounded-lg" style="margin: 5px;">
    <span class="text-2xl">❌</span> 
    <div>Bank feeds, wallets, DeFi don't talk to each other</div>
  </div>
  <div v-click class="text-green-400 font-bold text-lg flex items-center gap-2 bg-green-900/20 p-2 rounded-lg" style="margin: 5px;">
    <span class="text-2xl">✅</span> 
    <div>Unified AI copilot for hybrid finance</div>
  </div>
</div>

<!--
Narration (30 seconds): "We're solving hybrid finance chaos. Finance teams juggle bank feeds, wallets, and DeFi dashboards that don't communicate. ExaSpoon unifies everything under one AI-powered command center built on SpoonOS/Neo."
-->

---
layout: image-right
image: ./images/2.png
---

# AI CFO Command Center {.text-xl.font-black.bg-gradient-to-r.from-green-400.via-blue-500.to-purple-600.bg-clip-text.text-transparent.mb-1.text-center}

## Core Capabilities {.text-lg.text-blue-300.font-bold.mb-2.text-center}

<div v-click="1" class="feature-card">
  <div class="text-yellow-300 font-bold text-sm mb-0.5">🤖 Multi-Agent Brain</div>
  <div class="text-gray-400 text-xs">Intelligent orchestration of financial operations</div>
  <div class="tech-badge mt-0.5">SpoonAi + SpoonOS</div>
</div>

<div v-click="2" class="feature-card">
  <div class="text-yellow-300 font-bold text-sm mb-0.5">🔧 MCP Tools</div>
  <div class="text-gray-200 text-xs">Current: FastMCP Python → Planned: Rust migration</div>
  <div class="tech-badge mt-0.5">Database Integration</div>
</div>

<div v-click="3" class="feature-card">
  <div class="text-yellow-300 font-bold text-sm mb-0.5">🌐 Real-Time Chat UI</div>
  <div class="text-gray-200 text-xs">Interactive charts and instant insights</div>
  <div class="tech-badge mt-0.5">FastAPI + WebSocket</div>
</div>

<div v-click="4" class="feature-card">
  <div class="text-yellow-300 font-bold text-sm mb-0.5">⚡ Smart Categorization</div>
  <div class="text-gray-200 text-xs">AI-powered transaction classification</div>
  <div class="tech-badge mt-0.5">Embeddings + Vector DB</div>
</div>

<div v-click="5" class="feature-card">
  <div class="text-xl mb-0.5">🔗</div>
  <div class="text-yellow-300 font-bold text-sm mb-0.5">Web3 Automation</div>
  <div class="text-gray-400 text-xs">n8n workflows for DeFi integration</div>
  <div class="tech-badge mt-0.5">Smart Contract Monitoring</div>
</div>

<style>
.feature-card {
  @apply p-1.5 mb-1 bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-lg border border-gray-700 hover:border-blue-400 transition-all duration-500 hover:scale-105 hover:shadow-xl hover:shadow-blue-400/20 backdrop-blur-sm;
  margin: 5px !important;
}
.tech-badge {
  @apply text-xs bg-blue-900/50 px-1.5 py-0.5 rounded-full text-blue-300 border border-blue-700/50;
}
</style>

<!--
Narration (60 seconds): "ExaSpoon combines a 

multi-agent brain with MCP tools and a real-time web UI. It ingests bank data and crypto wallets, classifies transactions with AI embeddings, and answers financial questions instantly. Teams can ask for P&L reports, add expenses, and monitor everything through chat or automated workflows."
-->

---
layout: image-right
image: ./images/6.png
---

# Architecture Overview {.text-3xl.font-black.text-purple-300.mb-2.text-center}

## 🏗️ Unified Financial Graph {.text-xl.text-green-400.mb-3.text-center}

<div class="space-y-2">
  <div v-click="1" class="arch-item">
    <div class="flex items-center gap-2">
      <span class="text-2xl">🌐</span>
      <div>
        <div class="text-blue-400 font-bold text-base">UI Layer</div>
        <div class="text-gray-400 text-xs">FastAPI + D3.js + React WebSocket</div>
      </div>
    </div>
  </div>

  <div v-click="2" class="arch-item">
    <div class="flex items-center gap-2">
      <span class="text-2xl">🧠</span>
      <div>
        <div class="text-purple-400 font-bold text-base">AI Brain</div>
        <div class="text-gray-400 text-xs">Multi-Agent System + SpoonAi + SpoonOS</div>
      </div>
    </div>
  </div>

  <div v-click="3" class="arch-item">
    <div class="flex items-center gap-2">
      <span class="text-2xl">🔧</span>
      <div>
        <div class="text-yellow-400 font-bold text-base">MCP Tools</div>
        <div class="text-gray-400 text-xs">FastMCP Python → Rust Migration Planned</div>
      </div>
    </div>
  </div>

  <div v-click="4" class="arch-item">
    <div class="flex items-center gap-2">
      <span class="text-2xl">💾</span>
      <div>
        <div class="text-cyan-400 font-bold text-base">Data Layer</div>
        <div class="text-gray-400 text-xs">Supabase + pgvector + Embeddings</div>
      </div>
    </div>
  </div>

  <div v-click="5" class="arch-item">
    <div class="flex items-center gap-2">
      <span class="text-2xl">⚡</span>
      <div>
        <div class="text-orange-400 font-bold text-base">Web3 Automation</div>
        <div class="text-gray-400 text-xs">n8n Workflows + Smart Contract Monitoring</div>
      </div>
    </div>
  </div>
</div>

<style>
.arch-item {
  @apply p-2 bg-gradient-to-r from-gray-800/80 to-gray-900/80 rounded-lg border border-gray-700 backdrop-blur-sm;
  margin: 5px !important;
}
</style>



<!--
Narration (45 seconds): "Our architecture unifies everything in a single financial graph. A chat UI calls the multi-agent brain, which routes to a Rust MCP server for database operations. Off-chain bank data and on-chain wallet balances flow into the same Supabase database, powering both charts and AI conversations."
-->

---
layout: image-right
image: ./images/7.png
---

# Why SpoonOS/Neo {.text-xl.font-black.text-yellow-300.mb-0.5.text-center}

## 🎯 Built for Neo {.text-base.text-orange-400.mb-1.5.text-center}

<div v-click="1" class="advantage-card multi-agent mb-1">
  <div class="absolute -top-0.5 -right-0.5 text-lg opacity-15">🕸️</div>
  <div class="text-green-400 font-bold text-xs mb-0.5">Multi-Agent Graph Pattern</div>
  <div class="text-gray-300 text-xs mb-0.5">Optimized for complex agent orchestration</div>
  <div class="vs-section">
    <div class="text-red-400 text-xs mb-0.5">❌ Traditional: Sequential processing</div>
    <div class="text-green-400 text-xs">✅ Neo: Parallel agent collaboration</div>
  </div>
</div>

<div v-click="2" class="advantage-card mcp-tools mb-1">
  <div class="absolute -top-0.5 -right-0.5 text-lg opacity-15">🔧</div>
  <div class="text-blue-400 font-bold text-xs mb-0.5">MCP Tools Evolution</div>
  <div class="text-gray-300 text-xs mb-0.5">FastMCP Python → Rust Migration</div>
  <div class="vs-section">
    <div class="text-yellow-400 text-xs mb-0.5">🔄 Current: FastMCP (Basic DB ops)</div>
    <div class="text-green-400 text-xs">✅ Future: Rust (Type-safe + Performance)</div>
  </div>
</div>

<div v-click="3" class="advantage-card prompts mb-1">
  <div class="absolute -top-0.5 -right-0.5 text-lg opacity-15">🌍</div>
  <div class="text-yellow-400 font-bold text-xs mb-0.5">Language-First (Multilang)</div>
  <div class="text-gray-300 text-xs mb-0.5">Natural language interactions</div>
  <div class="vs-section">
    <div class="text-red-400 text-xs mb-0.5">❌ CLI: Command memorization</div>
    <div class="text-green-400 text-xs">✅ Neo: Intuitive conversations</div>
  </div>
</div>

<div v-click="4" class="advantage-card extension">
  <div class="absolute -top-0.5 -right-0.5 text-lg opacity-15">⚡</div>
  <div class="text-purple-400 font-bold text-xs mb-0.5">Easy Tool Extension</div>
  <div class="text-gray-300 text-xs mb-0.5">Rapid feature development</div>
  <div class="vs-section">
    <div class="text-red-400 text-xs mb-0.5">❌ Monolith: Slow deployment</div>
    <div class="text-green-400 text-xs">✅ Neo: Hot-swappable tools</div>
  </div>
</div>

<style>
.advantage-card {
  @apply relative p-1.5 bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-lg border-2 shadow-lg transform transition-all duration-700 hover:scale-105 hover:-translate-y-1 backdrop-blur-sm;
  margin: 5px !important;
}

.multi-agent { @apply border-green-400 hover:border-green-300 hover:shadow-green-400/30; }
.mcp-tools { @apply border-blue-400 hover:border-blue-300 hover:shadow-blue-400/30; }
.prompts { @apply border-yellow-400 hover:border-yellow-300 hover:shadow-yellow-400/30; }
.extension { @apply border-purple-400 hover:border-purple-300 hover:shadow-purple-400/30; }

.vs-section {
  @apply mt-0.5 p-1 bg-gray-800/60 rounded border border-gray-700/50;
}
</style>

<!-- 
Narration (30 seconds): "We built ExaSpoon natively for SpoonOS/Neo, leveraging multi-agent patterns and MCP tools. The platform is designed for Language first (Multilang) prompts and makes tool extension simple, allowing rapid development of new financial capabilities."
-->

---
transition: slide-left
layout: image-right
image: ./images/6.png
---

# Live Demo: E2E Tests {.text-3xl.mb-3.text-center}

## Complete Test Flow {.text-xl.mb-2.text-center}

<div class="space-y-2">
  <div v-click="1" class="step-item">
    <div class="flex items-center gap-2">
      <span class="text-2xl">📝</span>
      <div>
        <div class="text-yellow-300 font-bold text-base">Step 1: Add Transaction & Real-Time Updates</div>
        <div class="text-gray-400 text-xs">CFO adds transactions via native text interface • Instant UI refresh</div>
      </div>
    </div>
  </div>

  <div v-click="2" class="step-item">
    <div class="flex items-center gap-2">
      <span class="text-2xl">📊</span>
      <div>
        <div class="text-yellow-300 font-bold text-base">Step 2: Display Latest Transactions</div>
        <div class="text-gray-400 text-xs">Real-time graph • Totals table • Category breakdown • Text query reports</div>
      </div>
    </div>
  </div>

  <div v-click="3" class="step-item">
    <div class="flex items-center gap-2">
      <span class="text-2xl">🔗</span>
      <div>
        <div class="text-yellow-300 font-bold text-base">Step 3: n8n Integration & Blockchain Sync</div>
        <div class="text-gray-400 text-xs">NEO blockchain monitoring • Balance export • Transaction sync to ExaSpoon DB</div>
      </div>
    </div>
  </div>
</div>

<style>
.step-item {
  @apply p-2 bg-gradient-to-r from-gray-800/80 to-gray-900/80 rounded-lg border border-gray-700 backdrop-blur-sm;
  margin: 5px !important;
}
</style>

<!--
Narration (30 seconds): "Let me walk you through our end-to-end test flow. First, we add transactions in natural language. Then we generate comprehensive P&L reports with interactive visualizations. Finally, we monitor Web3 wallets automatically. This demonstrates how ExaSpoon unifies traditional finance and crypto operations in one seamless workflow."
-->

---
layout: image-right
image: ./images/5.png
---

# Step 1: Add Transaction & Real-Time Updates {.text-3xl.mb-3.text-center}

<div class="mb-3" style="margin: 5px;">

<div class="text-base mb-2 text-gray-200">
Using SpoonOS tools for data operations, the CFO can add transactions through the native text interface and immediately see results on screen.
</div>

<div class="bg-gradient-to-r from-green-900/30 to-blue-900/30 p-2 rounded-lg border border-green-400/50 mb-2">
<div class="text-green-300 font-bold text-sm mb-1">💬 Example Input:</div>
<div class="text-gray-200 text-sm italic">"Spent 100 USD on infrastructure yesterday from primary bank account"</div>
</div>

<div class="text-sm mt-2">
✅ AI categorizes automatically as 'Infrastructure expense'<br>
✅ Interface updates in real-time via WebSocket<br>
<em class="text-xs">SpoonOS Tools • Embeddings • Vector DB • 95% Accuracy</em>
</div>

</div>

<!--
Narration (30 seconds): "In step one, we use SpoonOS tools for data operations. The CFO can add transactions through our native text interface and immediately see the results on screen. The interface updates in real-time, showing the new transaction, its category, and updated totals - all powered by SpoonOS's seamless data integration."
-->
---
layout: image-right
image: ./images/4.png
---

# Step 2: Display Latest Transactions {.text-3xl.mb-3.text-center}

<div class="mb-3" style="margin: 5px;">

<div class="text-base mb-2 text-gray-200">
The screen displays a real-time updated graph, a table with totals and expense categories used in the program. Based on this data, ExaSpoon generates reports via text queries through the interface.
</div>

<div class="space-y-2">
  <div class="feature-box">
    <div class="text-green-300 font-bold text-sm mb-1">📈 Real-Time Graph</div>
    <div class="text-gray-400 text-xs">Live updates as transactions are added</div>
  </div>

  <div class="feature-box">
    <div class="text-blue-300 font-bold text-sm mb-1">📊 Totals & Categories Table</div>
    <div class="text-gray-400 text-xs">Expense breakdown by category with running totals</div>
  </div>

  <div class="feature-box">
    <div class="text-purple-300 font-bold text-sm mb-1">💬 Text Query Reports</div>
    <div class="text-gray-400 text-xs">ExaSpoon generates reports based on natural language queries</div>
  </div>
</div>

</div>

<style>
.feature-box {
  @apply p-2 bg-gradient-to-r from-gray-800/80 to-gray-900/80 rounded-lg border border-gray-700 backdrop-blur-sm;
  margin: 3px !important;
}
</style>

<!--
Narration (30 seconds): "Step two showcases our real-time visualization capabilities. The screen displays a continuously updated graph showing transaction trends, alongside a comprehensive table with totals and expense categories. Users can query this data through natural language - asking questions like 'show me infrastructure spending this month' and ExaSpoon generates instant reports."
-->
---
layout: image-right
image: ./images/11.png
---

# Step 3: n8n Integration & Blockchain Sync {.text-3xl.mb-3.text-center}

<div class="mb-3" style="margin: 5px;">

<div class="text-base mb-2 text-gray-200">
We developed an integration with the no-code platform n8n, teaching it to work with the NEO blockchain. The workflow exports current balances and updates this data in the ExaSpoon database, fetching transactions from wallets and transaction information.
</div>

<div class="space-y-2">
  <div class="integration-box">
    <div class="text-yellow-300 font-bold text-sm mb-1">🔗 n8n Workflow Integration</div>
    <div class="text-gray-400 text-xs">No-code automation platform connected to NEO blockchain</div>
  </div>

  <div class="integration-box">
    <div class="text-cyan-300 font-bold text-sm mb-1">⛓️ NEO Blockchain Monitoring</div>
    <div class="text-gray-400 text-xs">Real-time wallet balance tracking and transaction fetching</div>
  </div>

  <div class="integration-box">
    <div class="text-green-300 font-bold text-sm mb-1">💾 ExaSpoon Database Sync</div>
    <div class="text-gray-400 text-xs">Automatic updates of balances and transactions in unified storage</div>
  </div>
</div>

</div>

<style>
.integration-box {
  @apply p-2 bg-gradient-to-r from-gray-800/80 to-gray-900/80 rounded-lg border border-gray-700 backdrop-blur-sm;
  margin: 3px !important;
}
</style>

<!--
Narration (35 seconds): "Step three demonstrates our Web3 integration capabilities. We've built a custom integration with n8n, a no-code automation platform, teaching it to interact with the NEO blockchain. The workflow continuously monitors wallet balances, fetches transaction data, and automatically syncs everything to the ExaSpoon database. This creates a seamless bridge between on-chain and off-chain financial data."
-->

---
layout: image-left
image: ./images/10.png
class: mcp-arch-slide
---

<style>
.mcp-arch-slide img,
.mcp-arch-slide .image-container img,
.mcp-arch-slide [class*="image"] img {
  object-fit: contain !important;
  width: 100% !important;
  height: 100% !important;
  max-width: 100% !important;
  max-height: 100% !important;
  object-position: center !important;
}
</style>

# MCP Architecture {.text-4xl.font-black.text-white.drop-shadow-2xl.mb-3.text-center}

## ⚡ Blazing Fast {.text-xl.text-orange-400.drop-shadow-lg.mb-5.text-center}

<div class="space-y-3 max-w-xl mx-auto">
  <div v-click="1" class="arch-component">
    <div class="flex items-center gap-3">
      <span class="text-2xl">🦀</span>
      <div class="flex-1">
        <div class="text-yellow-300 font-bold text-base">Rust Server</div>
        <div class="text-gray-200 text-xs">rmcp crate • Type-safe • High performance</div>
      </div>
    </div>
  </div>

  <div v-click="2" class="arch-component">
    <div class="flex items-center gap-3">
      <span class="text-2xl">🐍</span>
      <div class="flex-1">
        <div class="text-green-300 font-bold text-base">Python CLI</div>
        <div class="text-gray-200 text-xs">MCPToolClient • FastMCP integration</div>
      </div>
    </div>
  </div>

  <div v-click="3" class="arch-component">
    <div class="flex items-center gap-3">
      <span class="text-2xl">💾</span>
      <div class="flex-1">
        <div class="text-cyan-300 font-bold text-base">Supabase DB</div>
        <div class="text-gray-200 text-xs">pgvector + Embeddings • Unified storage</div>
      </div>
    </div>
  </div>
</div>

<div v-click="4" class="mt-5 max-w-lg mx-auto">
  <div class="bg-gradient-to-r from-orange-900/50 to-yellow-900/50 p-3 rounded-xl border-2 border-orange-400/60 backdrop-blur-md shadow-lg" style="margin: 5px;">
    <div class="text-orange-300 font-bold text-center text-base mb-1">⚡ Lightning-Fast Communication</div>
    <div class="text-gray-200 text-xs text-center">Direct connections between components</div>
  </div>
</div>

<style>
.arch-component {
  @apply p-3 bg-gradient-to-r from-gray-800/95 to-gray-900/95 rounded-lg border-2 border-gray-600/60 backdrop-blur-md shadow-lg;
  margin: 3px !important;
}
</style>

<!--
Narration (40 seconds): "Our MCP architecture is built for speed and reliability. A Rust server using the rmcp crate provides type-safe, high-performance database operations. The Python CLI with MCPToolClient handles FastMCP integration seamlessly. All data flows into Supabase with pgvector for embeddings storage. This architecture enables lightning-fast communication between components, ensuring that financial queries and operations execute in milliseconds, not seconds."
-->

---
layout: image-right
image: ./images/8.png
class: image-slide
---

# Join the Revolution {.text-3xl.font-black.text-transparent.bg-clip-text.bg-gradient-to-r.from-green-400.via-blue-500.to-purple-600.mb-2.text-center}

<div class="text-xl font-bold text-green-400 mb-2 animate-pulse text-center">
    Built natively on SpoonOS/Neo
</div>

<div class="text-lg text-yellow-300 mb-3 font-semibold text-center">
  ExaSpoon: AI CFO for Hybrid Finance
</div>

<div class="space-y-2 text-sm text-gray-200 mb-3 max-w-xl mx-auto">
  <div class="cta-card">
    <div class="flex items-center gap-2">
      <span class="text-xl">🔗</span>
      <div class="text-left">
        <div class="text-green-400 font-bold text-base">GitHub</div>
        <div class="text-gray-400 text-xs">MIT License • Deploy Today</div>
      </div>
    </div>
  </div>
  
  <div class="cta-card">
    <div class="flex items-center gap-2">
      <span class="text-xl">🚀</span>
      <div class="text-left">
        <div class="text-blue-400 font-bold text-base">Live Demo</div>
        <div class="text-gray-400 text-xs">Interactive Instance Available</div>
      </div>
    </div>
  </div>
  
  <div class="cta-card">
    <div class="flex items-center gap-2">
      <span class="text-xl">⚡</span>
      <div class="text-left">
        <div class="text-purple-400 font-bold text-base">What's Next</div>
        <div class="text-gray-400 text-xs">Risk/KYC MCP • Production Deploy</div>
      </div>
    </div>
  </div>
</div>

<div class="text-2xl font-bold text-orange-400 mb-2 animate-bounce text-center">
  Questions?
</div>

<div class="text-base text-gray-200 italic bg-gradient-to-r from-gray-800/80 to-gray-900/80 p-3 rounded-xl border border-orange-400/50 backdrop-blur-sm max-w-lg mx-auto shadow-xl" style="margin: 5px;">
  "Unified finance operations for the crypto-native world"
</div>

<style>
.cta-card {
  @apply flex items-center gap-2 p-2 bg-gradient-to-r from-gray-800/80 to-gray-900/80 rounded-lg border border-gray-700/50 transform transition-all duration-500 hover:scale-105 hover:shadow-xl hover:border-gray-600 backdrop-blur-sm;
  margin: 5px !important;
}
</style>

<!--
Narration (30 seconds): "ExaSpoon is ready to deploy today with MIT license. We have a working demo and are adding risk and KYC tools next. We invite you to join us in building unified financial operations for crypto-native companies. Thank you!"
-->
