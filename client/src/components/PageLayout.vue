<template>
  <div class="page-container">
    <!-- Error state display -->
    <div v-if="hasError" class="error-panel">
      <h2>Application Error</h2>
      <p>{{ errorMessage }}</p>
      <div class="error-details" v-if="showErrorDetails">
        <div class="api-info">
          <p><strong>API URL:</strong> {{ apiUrl }}</p>
          <p><strong>Status:</strong> {{ connectionStatus }}</p>
          <p>
            <strong>Auth Token:</strong> {{ hasToken ? "Present" : "Missing" }}
          </p>
        </div>
        <pre v-if="errorDetails" class="error-trace">{{ errorDetails }}</pre>
      </div>
      <div class="error-actions">
        <button
          @click="toggleErrorDetails"
          class="btn-secondary"
        >
          <span class="icon"><i class="bi bi-clipboard-data"></i></span>
          {{ localShowErrorDetails ? "Hide" : "Show" }} Details
        </button>
        <button @click="$emit('run-diagnostics')" class="btn-secondary">
          <span class="icon"><i class="bi bi-activity"></i></span> Diagnostics
        </button>
        <button @click="$emit('retry')" class="btn-secondary">
          <span class="icon"><i class="bi bi-arrow-clockwise"></i></span> Retry
          Connection
        </button>
        <button @click="$emit('back-to-login')" class="btn-primary">
          <span class="icon"><i class="bi bi-box-arrow-left"></i></span> Back to
          Login
        </button>
      </div>
    </div>

    <!-- Mock model notification -->
    <div v-if="showMockWarning" class="mock-model-notification">
      <div class="notification-content">
        <i class="bi bi-info-circle"></i>
        <span>Using demo predictions with mock model</span>
      </div>
      <div class="notification-details">
        The predictions shown are simulated examples and do not represent actual
        AI analysis.
      </div>
    </div>

    <!-- Main content -->
    <div v-if="!hasError" class="app-layout">
      <!-- Left Navigation Sidebar -->
      <app-sidebar 
        :currentRoute="currentRoute" 
        @logout="$emit('logout')" 
      />

      <div class="page-wrapper">
        <!-- Page Header -->
        <app-header :username="username" @logout="$emit('logout')">
          <template #title>
            <slot name="header-title"></slot>
          </template>
        </app-header>

        <!-- Page Content -->
        <div class="page-content">
          <slot></slot>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isLoading && !hasError" class="loader-overlay">
      <div class="spinner-container">
        <i class="bi bi-arrow-repeat spin"></i>
        <p>Loading content...</p>
      </div>
    </div>
  </div>
</template>

<script>
import AppHeader from './AppHeader.vue';
import AppSidebar from './AppSidebar.vue';

export default {
  name: 'PageLayout',
  components: {
    AppHeader,
    AppSidebar
  },
  data() {
    return {
      localShowErrorDetails: this.showErrorDetails
    };
  },
  props: {
    // Error handling props
    hasError: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: ''
    },
    errorDetails: {
      type: String,
      default: null
    },
    showErrorDetails: {
      type: Boolean,
      default: false
    },
    connectionStatus: {
      type: String,
      default: 'Unknown'
    },
    hasToken: {
      type: Boolean,
      default: false
    },
    apiUrl: {
      type: String,
      default: ''
    },
    
    // User information
    username: {
      type: String,
      default: 'User'
    },
    
    // Page state
    isLoading: {
      type: Boolean,
      default: false
    },
    currentRoute: {
      type: String,
      default: 'home'
    },
    
    // Features
    showMockWarning: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    toggleErrorDetails() {
      this.localShowErrorDetails = !this.localShowErrorDetails;
      this.$emit('update:showErrorDetails', this.localShowErrorDetails);
    }
  },
  watch: {
    showErrorDetails(newVal) {
      this.localShowErrorDetails = newVal;
    }
  },
  emits: [
    'logout', 
    'retry', 
    'run-diagnostics', 
    'back-to-login',
    'update:showErrorDetails'
  ]
};
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  position: relative;
}

/* App Layout with Sidebar */
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Page wrapper for content next to sidebar */
.page-wrapper {
  flex: 1;
  padding: 1.5rem;
  margin-left: 240px;
  max-width: calc(100% - 240px);
}

.page-content {
  width: 100%;
}

/* Error panel styling */
.error-panel {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 2rem auto;
}

.error-panel h2 {
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-details {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
}

.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.error-trace {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0.5rem;
  font-family: monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
  word-break: break-all;
  color: #f87171;
  max-height: 200px;
  overflow-y: auto;
}

/* Button styles */
.btn-primary, .btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-size: 0.875rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

.btn-secondary {
  background: rgba(15, 23, 42, 0.5);
  color: #e5e7eb;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.btn-secondary:hover {
  background: rgba(15, 23, 42, 0.7);
  border-color: rgba(59, 130, 246, 0.5);
}

/* Mock model notification */
.mock-model-notification {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  color: #f59e0b;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.notification-details {
  font-size: 0.875rem;
  opacity: 0.8;
}

.loader-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(9, 12, 20, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  backdrop-filter: blur(2px);
}

.spinner-container {
  background-color: rgba(15, 23, 42, 0.9);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.spinner-container i {
  font-size: 2.5rem;
  color: #3b82f6;
  animation: spin 1s infinite linear;
}

.spinner-container p {
  color: #e5e7eb;
  font-size: 1rem;
  margin: 0;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 