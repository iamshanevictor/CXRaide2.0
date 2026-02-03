<template>
  <div class="public-layout">
    <PublicTopNav />
    <main class="content">
      <slot />
    </main>
  </div>
</template>

<script>
import PublicTopNav from "@/components/PublicTopNav.vue";

export default {
  name: "PublicLayout",
  components: { PublicTopNav },
};
</script>

<style scoped>
.public-layout {
  min-height: 100vh;
  background:
    radial-gradient(900px 320px at 20% 0%, rgba(37, 99, 235, 0.10), transparent 55%),
    radial-gradient(900px 360px at 80% 10%, rgba(14, 165, 233, 0.10), transparent 55%),
    var(--bg);
}

.content {
  min-height: calc(100vh - 68px);
}
</style>
