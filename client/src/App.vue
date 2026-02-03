<template>
  <div id="app">
    <UiToastHost />
    <!-- Offline mode notification -->
    <div v-if="isOfflineMode" class="offline-notification">
      <i class="bi bi-wifi-off"></i>
      <span>Offline Mode - Limited Functionality</span>
    </div>
    
    <router-view v-slot="{ Component }">
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

        <div v-else-if="errorOccurred" class="error-screen">
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

        <!-- Public/blank layout pages (Landing, Login, etc.) -->
        <component
          v-else-if="$route.meta && $route.meta.layout === 'blank'"
          :is="Component"
          @loading-start="startLoading"
          @loading-end="stopLoading"
        />

        <!-- Public pages that should have the top navbar (no sidebar) -->
        <PublicLayout v-else-if="$route.meta && $route.meta.layout === 'public'">
          <component
            :is="Component"
            :key="$route.fullPath"
            @loading-start="startLoading"
            @loading-end="stopLoading"
          />
        </PublicLayout>

        <!-- Authenticated app pages -->
        <AppLayout v-else>
          <component
            :is="Component"
            :key="$route.fullPath"
            @loading-start="startLoading"
            @loading-end="stopLoading"
          />
        </AppLayout>
      </transition>
    </router-view>
  </div>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue';
import PublicLayout from '@/components/PublicLayout.vue';
import UiToastHost from '@/ui/UiToastHost.vue';

export default {
  components: {
    AppLayout,
    PublicLayout,
    UiToastHost,
  },
  data() {
    return {
      errorOccurred: false,
      isLoading: false,
      loadingTimeout: null,
      isOfflineMode: false,
    };
  },
  created() {
    // Theme: default to dark (original blue). Use theme-light only when explicitly chosen.
    try {
      const savedTheme = localStorage.getItem('cxraide_theme');
      document.body.classList.toggle('theme-light', savedTheme === 'light');
    } catch (e) {
      // ignore
    }

    // Check if we're in offline mode
    this.checkOfflineMode();
    
    // Setup interval to check offline mode every minute
    setInterval(this.checkOfflineMode, 60000);
    
    // Setup global navigation guards to show loading state
    this.$router.beforeEach((to, from, next) => {
      // Use a longer loading time when coming from the annotation page
      if (from.name === 'annotate') {
        this.startLoading(true); // Use extended loading for annotation page transitions
      } else {
        this.startLoading();
      }
      next();
    });
    this.$router.afterEach(() => {
      // Check offline status after each navigation
      this.checkOfflineMode();
      
      // Use a longer delay for hiding loader after navigation from annotation page
      setTimeout(() => {
        this.stopLoading();
      }, 500); // Increase from 300ms to 500ms
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
    startLoading(extended = false) {
      clearTimeout(this.loadingTimeout);
      this.isLoading = true;

      // If coming from annotation page, force a small delay to ensure proper cleanup
      if (extended) {
        console.log("[App] Using extended loading sequence");
        // Force component cleanup during loading
        setTimeout(() => {
          // Clear any hanging DOM references
          Array.from(document.querySelectorAll('canvas')).forEach(canvas => {
            const context = canvas.getContext('2d');
            if (context) {
              context.clearRect(0, 0, canvas.width, canvas.height);
            }
          });
        }, 100);
      }
    },
    stopLoading() {
      // Use timeout to prevent quick flashes of loading screen
      this.loadingTimeout = setTimeout(() => {
        this.isLoading = false;
      }, 300);
    },
    checkOfflineMode() {
      try {
        // Check if token exists
        const token = localStorage.getItem('authToken');
        if (!token) {
          this.isOfflineMode = false;
          return;
        }
        
        // Check if it's an offline token
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        this.isOfflineMode = decoded.offline_mode === true;
      } catch (error) {
        console.error('[App] Error checking offline mode:', error);
        this.isOfflineMode = false;
      }
    }
  },
};
</script>

<style>
/* App-level helpers kept intentionally small; most styling lives in src/styles */
.offline-notification {
  position: fixed;
  left: 16px;
  bottom: 16px;
  z-index: 9998;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-md);
  color: var(--text-2);
}

.loading-screen,
.error-screen {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--bg);
}

select option {
  background-color: rgba(15, 23, 42, 0.95);
  color: #f3f4f6;
  padding: 10px;
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

/* Offline mode notification */
.offline-notification {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: rgba(244, 63, 94, 0.9);
  color: white;
  padding: 0.5rem;
  text-align: center;
  font-size: 0.9rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.offline-notification i {
  font-size: 1rem;
}
</style>
