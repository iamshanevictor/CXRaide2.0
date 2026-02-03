<template>
  <div class="ui-card" :class="{ padded }">
    <div v-if="title || $slots.header" class="ui-card__header">
      <div v-if="$slots.header"><slot name="header" /></div>
      <div v-else class="ui-card__title">
        <div class="title">{{ title }}</div>
        <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
      </div>
      <div v-if="$slots.actions" class="ui-card__actions"><slot name="actions" /></div>
    </div>
    <div class="ui-card__body"><slot /></div>
  </div>
</template>

<script>
export default {
  name: "UiCard",
  props: {
    title: { type: String, default: "" },
    subtitle: { type: String, default: "" },
    padded: { type: Boolean, default: true },
  },
};
</script>

<style scoped>
.ui-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.ui-card.padded .ui-card__body { padding: 16px; }

.ui-card__header {
  padding: 14px 16px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}

.title { font-weight: 700; font-size: 14px; color: var(--text); }
.subtitle { margin-top: 2px; font-size: 12.5px; color: var(--muted); }

.ui-card__actions { display: flex; gap: 10px; align-items: center; }
</style>
