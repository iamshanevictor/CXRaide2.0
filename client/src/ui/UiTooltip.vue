<template>
  <span class="tip">
    <slot />
    <span v-if="text" class="bubble" role="tooltip">{{ text }}</span>
  </span>
</template>

<script>
export default {
  name: "UiTooltip",
  props: {
    text: { type: String, default: "" },
  },
};
</script>

<style scoped>
.tip {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.bubble {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 8px);
  transform: translateX(-50%);
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-md);
  border-radius: 12px;
  padding: 8px 10px;
  font-size: 12.5px;
  font-weight: 650;
  color: var(--text);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity .12s ease, transform .12s ease;
}

.tip:hover .bubble {
  opacity: 1;
  transform: translateX(-50%) translateY(-2px);
}
</style>
