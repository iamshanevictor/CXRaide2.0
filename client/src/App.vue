<template>
  <div id="app">
    <router-view v-if="!errorOccurred" />
    <div v-else class="error-screen">
      <h2>Application Error</h2>
      <button @click="reloadApp">Reload Application</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      errorOccurred: false,
    };
  },
  errorCaptured(err, vm, info) {
    this.errorOccurred = true;
    console.error("Captured error:", err, "Component:", vm, "Info:", info);
    return false;
  },
  methods: {
    reloadApp() {
      window.location.reload();
    },
  },
};
</script>

<style>
.error-screen {
  padding: 2rem;
  text-align: center;
}
</style>
