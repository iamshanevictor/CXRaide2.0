<template>
  <button
    class="ui-btn"
    :class="[variant, size, { loading, block }]"
    :type="type"
    :disabled="disabled || loading"
  >
    <span v-if="loading" class="spinner" aria-hidden="true" />
    <i v-else-if="icon" :class="icon" class="btn-icon" aria-hidden="true" />
    <span class="btn-label"><slot /></span>
  </button>
</template>

<script>
export default {
  name: "UiButton",
  props: {
    variant: { type: String, default: "primary" }, // primary|secondary|ghost|danger
    size: { type: String, default: "md" }, // sm|md|lg
    type: { type: String, default: "button" },
    icon: { type: String, default: "" },
    loading: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
    block: { type: Boolean, default: false },
  },
};
</script>

<style scoped>
.ui-btn {
  border: 1px solid transparent;
  border-radius: 12px;
  padding: 10px 14px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.12s ease, background 0.12s ease, border-color 0.12s ease, color 0.12s ease;
}

.ui-btn.block { width: 100%; }

.ui-btn:disabled { opacity: 0.55; cursor: not-allowed; }

.ui-btn.primary {
  background: var(--primary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.ui-btn.primary:hover:not(:disabled) { background: var(--primary-2); transform: translateY(-1px); }

.ui-btn.secondary {
  background: var(--surface);
  color: var(--text);
  border-color: var(--border);
}

.ui-btn.secondary:hover:not(:disabled) { background: var(--surface-2); transform: translateY(-1px); }

.ui-btn.ghost {
  background: transparent;
  color: var(--text);
  border-color: var(--border);
}

.ui-btn.ghost:hover:not(:disabled) { background: var(--surface-2); }

.ui-btn.danger {
  background: var(--danger);
  color: white;
}

.ui-btn.danger:hover:not(:disabled) { filter: brightness(0.98); transform: translateY(-1px); }

.ui-btn.sm { padding: 8px 12px; font-size: 13px; border-radius: 11px; }
.ui-btn.lg { padding: 12px 16px; font-size: 15px; border-radius: 14px; }

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid rgba(255,255,255,0.45);
  border-top-color: rgba(255,255,255,0.95);
  animation: spin 0.8s linear infinite;
}

.secondary .spinner, .ghost .spinner {
  border-color: rgba(15,23,42,0.20);
  border-top-color: rgba(15,23,42,0.55);
}

.btn-icon { font-size: 16px; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
