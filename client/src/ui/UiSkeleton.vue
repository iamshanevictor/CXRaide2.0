<template>
  <div class="sk" :style="style" aria-hidden="true" />
</template>

<script>
export default {
  name: "UiSkeleton",
  props: {
    w: { type: [Number, String], default: "100%" },
    h: { type: [Number, String], default: 12 },
    r: { type: [Number, String], default: 12 },
  },
  computed: {
    style() {
      const toCss = (v) => (typeof v === "number" ? `${v}px` : v);
      return {
        width: toCss(this.w),
        height: toCss(this.h),
        borderRadius: toCss(this.r),
      };
    },
  },
};
</script>

<style scoped>
.sk {
  background: linear-gradient(90deg, var(--surface-2), rgba(37,99,235,0.10), var(--surface-2));
  background-size: 200% 100%;
  animation: shimmer 1.2s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 0% 0%; }
  100% { background-position: -200% 0%; }
}
</style>
