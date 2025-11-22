<template>
  <div class="layout-image">
    <div class="content-container">
      <slot></slot>
    </div>
    <div class="image-container">
      <img v-if="image" :src="image" />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  image: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.layout-image {
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  background: linear-gradient(
    135deg,
    var(--color-bg-dark),
    var(--color-bg-surface)
  );
  border: 6px solid var(--color-rust1);
  box-shadow: 0 0 40px rgba(46, 255, 120, 0.4);
}

.image-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 0;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
}

.content-container {
  width: 100%;
  height: 100%;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow-y: auto;
}
</style>

