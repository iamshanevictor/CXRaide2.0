<template>
  <div class="app-layout-container">
    <NavSidebar />
    
    <div class="app-content">
      <slot></slot>
    </div>
  </div>
</template>

<script>
import NavSidebar from './NavSidebar.vue';

export default {
  name: 'AppLayout',
  components: {
    NavSidebar
  }
}
</script>

<style>
.app-layout-container {
  display: flex !important;
  min-height: 100vh !important;
  width: 100% !important;
  position: relative !important;
}

.app-layout-container .app-content {
  flex: 1 !important;
  margin-left: 240px !important; /* Matches sidebar width */
  min-height: 100vh !important;
  width: calc(100% - 240px) !important;
  padding: 0 !important;
  overflow-x: hidden !important;
  background: var(--bg) !important;
}
</style> 