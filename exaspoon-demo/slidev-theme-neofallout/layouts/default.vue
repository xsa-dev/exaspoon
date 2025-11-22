<template>
  <div class="layout">
    <header>
      <slot name="title"></slot>
    </header>

    <main>
      <slot></slot>
    </main>

    <footer>
      <slot name="footer"></slot>
    </footer>
  </div>
</template>

<style scoped>
.layout {
  width: 100%;
  height: 100%;
  padding: 40px;
  background: linear-gradient(
    135deg,
    var(--color-bg-dark),
    var(--color-bg-surface)
  );
  border: 6px solid var(--color-rust1);
  box-shadow: 0 0 40px rgba(46, 255, 120, 0.4);
}

header {
  margin-bottom: 40px;
}

footer {
  margin-top: 50px;
  opacity: 0.6;
  font-size: 0.8em;
}
</style>
