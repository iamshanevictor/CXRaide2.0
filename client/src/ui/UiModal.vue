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
  padding: 18px;
  z-index: 9999;
}

.modal {
  width: min(720px, 100%);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.head {
  padding: 14px 16px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}

.title { font-weight: 900; color: var(--text); }
.subtitle { margin-top: 2px; color: var(--muted); font-size: 13px; }

.x {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  cursor: pointer;
}

.x:hover { background: var(--surface-2); color: var(--text); }

.body { padding: 16px; }

.foot {
  padding: 14px 16px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
