<template>
  <span class="ui-badge" :class="variant">
    <slot />
  </span>
</template>

<script>
export default {
  name: "UiBadge",
  props: {
    variant: { type: String, default: "info" }, // info|success|warning|danger|neutral
  },
};
</script>

<style scoped>
.ui-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text-2);
}

.ui-badge.info { background: var(--primary-soft); border-color: rgba(37, 99, 235, 0.25); color: var(--primary-2); }
.ui-badge.success { background: rgba(22, 163, 74, 0.12); border-color: rgba(22, 163, 74, 0.22); color: var(--success); }
.ui-badge.warning { background: rgba(217, 119, 6, 0.12); border-color: rgba(217, 119, 6, 0.22); color: var(--warning); }
.ui-badge.danger { background: rgba(220, 38, 38, 0.10); border-color: rgba(220, 38, 38, 0.20); color: var(--danger); }
.ui-badge.neutral { background: var(--surface); }
</style>
