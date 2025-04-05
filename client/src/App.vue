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
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap");

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: "Montserrat", sans-serif;
  background: linear-gradient(135deg, #090c14 0%, #10172a 100%);
  color: #ffffff;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

a {
  color: #64a5ff;
  text-decoration: none;
  transition: color 0.3s ease;
}

a:hover {
  color: #3b82f6;
  text-decoration: underline;
}

button {
  font-family: "Montserrat", sans-serif;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6);
}

::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.6);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.8);
}

/* Glow selection */
::selection {
  background: rgba(59, 130, 246, 0.3);
  color: #ffffff;
}

.error-screen {
  padding: 2rem;
  text-align: center;
}
</style>
