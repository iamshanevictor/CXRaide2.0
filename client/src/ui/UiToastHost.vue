<template>
  <div class="toast-host" aria-live="polite" aria-relevant="additions removals">
    <transition-group name="toast" tag="div">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.variant">
        <div class="toast-icon">
          <i :class="iconFor(t.variant)" />
        </div>
        <div class="toast-body">
          <div v-if="t.title" class="toast-title">{{ t.title }}</div>
          <div class="toast-msg">{{ t.message }}</div>
        </div>
        <button class="toast-close" type="button" @click="removeToast(t.id)" aria-label="Dismiss">
          <i class="bi bi-x" />
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { useToast } from "./useToast";

export default {
  name: "UiToastHost",
  setup() {
    const { toasts, removeToast } = useToast();
    const iconFor = (variant) => {
      switch (variant) {
        case "success":
          return "bi bi-check-circle-fill";
        case "warning":
          return "bi bi-exclamation-triangle-fill";
        case "danger":
          return "bi bi-x-octagon-fill";
        default:
          return "bi bi-info-circle-fill";
      }
    };
    return { toasts, removeToast, iconFor };
  },
};
</script>

<style scoped>
.toast-host {
  position: fixed;
  right: 18px;
  top: 18px;
  z-index: 9999;
  display: grid;
  gap: 10px;
}

.toast {
  width: min(420px, calc(100vw - 36px));
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--shadow-md);
  display: grid;
  grid-template-columns: 34px 1fr 34px;
  align-items: start;
  gap: 10px;
  padding: 12px;
}

.toast-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--surface-2);
  color: var(--primary);
}

.toast.success .toast-icon { color: var(--success); }
.toast.warning .toast-icon { color: var(--warning); }
.toast.danger .toast-icon { color: var(--danger); }

.toast-title {
  font-weight: 650;
  font-size: 13px;
  color: var(--text);
  margin-bottom: 2px;
}

.toast-msg {
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.35;
}

.toast-close {
  border: 0;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  width: 34px;
  height: 34px;
  border-radius: 10px;
}

.toast-close:hover {
  background: var(--surface-2);
  color: var(--text);
}

.toast-enter-active, .toast-leave-active { transition: all .18s ease; }
.toast-enter-from { opacity: 0; transform: translateY(-8px); }
.toast-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
