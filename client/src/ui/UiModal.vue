<template>
  <teleport to="body">
    <transition name="fade">
      <div v-if="open" class="backdrop" @click.self="$emit('close')">
        <div class="modal" role="dialog" aria-modal="true" :aria-label="title">
          <div class="head">
            <div>
              <div class="title">{{ title }}</div>
              <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
            </div>
            <button class="x" type="button" @click="$emit('close')" aria-label="Close">
              <i class="bi bi-x" />
            </button>
          </div>
          <div class="body">
            <slot />
          </div>
          <div v-if="$slots.footer" class="foot">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script>
export default {
  name: "UiModal",
  emits: ["close"],
  props: {
    open: { type: Boolean, default: false },
    title: { type: String, default: "" },
    subtitle: { type: String, default: "" },
  },
};
</script>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2,6,23,0.55);
  display: grid;
  place-items: center;
  padding: 10px;
  z-index: 9999;
}

.modal {
  width: min(860px, 100%);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.head {
  padding: 9px 10px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}

.title { font-weight: 850; color: var(--text); font-size: 13px; }
.subtitle { margin-top: 1px; color: var(--muted); font-size: 11px; }

.x {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  cursor: pointer;
}

.x:hover { background: var(--surface-2); color: var(--text); }

.body { padding: 10px; }

.foot {
  padding: 9px 10px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}
</style>
