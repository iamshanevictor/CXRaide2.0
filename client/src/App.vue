<template>
  <div id="app">
    <transition name="fade" mode="out-in">
      <div v-if="isLoading" class="loading-screen">
        <div class="loading-container">
          <div class="loader-ring">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
          <div class="loading-text">Loading CXRaide</div>
          <div class="loading-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
      <router-view
        v-else-if="!errorOccurred"
        @loading-start="startLoading"
        @loading-end="stopLoading"
      />
      <div v-else class="error-screen">
        <div class="error-container">
          <div class="error-icon">
            <i class="bi bi-exclamation-triangle-fill"></i>
          </div>
          <h2>Application Error</h2>
          <p>We encountered an unexpected issue. Please try again.</p>
          <button @click="reloadApp" class="reload-button">
            <i class="bi bi-arrow-clockwise"></i> Reload Application
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  data() {
    return {
      errorOccurred: false,
      isLoading: false,
      loadingTimeout: null,
    };
  },
  created() {
    // Setup global navigation guards to show loading state
    this.$router.beforeEach((to, from, next) => {
      this.startLoading();
      next();
    });
    this.$router.afterEach(() => {
      // Delay hiding loader slightly to prevent flashing on fast loads
      setTimeout(() => {
        this.stopLoading();
      }, 300);
    });
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
    startLoading() {
      clearTimeout(this.loadingTimeout);
      this.isLoading = true;
    },
    stopLoading() {
      // Use timeout to prevent quick flashes of loading screen
      this.loadingTimeout = setTimeout(() => {
        this.isLoading = false;
      }, 300);
    },
  },
};
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap");
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");

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

/* Error screen */
.error-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(9, 12, 20, 0.95);
  z-index: 9999;
}

.error-container {
  background: rgba(15, 23, 42, 0.8);
  border-radius: 12px;
  padding: 2.5rem;
  text-align: center;
  box-shadow: 0 0 40px rgba(59, 130, 246, 0.2);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  max-width: 400px;
}

.error-icon {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-container h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #f3f4f6;
}

.error-container p {
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.reload-button {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin: 0 auto;
  transition: transform 0.2s, box-shadow 0.2s;
}

.reload-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* Loading screen */
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(9, 12, 20, 0.95) 0%,
    rgba(16, 23, 42, 0.95) 100%
  );
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(5px);
}

.loading-container {
  text-align: center;
}

.loader-ring {
  display: inline-block;
  position: relative;
  width: 80px;
  height: 80px;
}

.loader-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 64px;
  height: 64px;
  margin: 8px;
  border: 6px solid #3b82f6;
  border-radius: 50%;
  animation: loader-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border-color: #3b82f6 transparent transparent transparent;
}

.loader-ring div:nth-child(1) {
  animation-delay: -0.45s;
}

.loader-ring div:nth-child(2) {
  animation-delay: -0.3s;
}

.loader-ring div:nth-child(3) {
  animation-delay: -0.15s;
}

@keyframes loader-ring {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 1.5rem;
  font-size: 1.2rem;
  font-weight: 500;
  color: #e5e7eb;
  letter-spacing: 0.5px;
}

.loading-dots {
  display: flex;
  justify-content: center;
  margin-top: 0.75rem;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  margin: 0 4px;
  background-color: #3b82f6;
  border-radius: 50%;
  display: inline-block;
  animation: dots 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes dots {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.2;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
