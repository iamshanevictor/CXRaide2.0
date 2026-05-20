<template>
  <div class="nav-sidebar">
    <div class="logo-container">
      <RouterLink class="logo-link" to="/" aria-label="Go to main page">
        <img
          src="@/assets/LOGO1.png"
          alt="CXRaide Logo"
          class="sidebar-logo"
        />
      </RouterLink>
    </div>
    <div class="nav-items">
      <div class="nav-section">Research Demo</div>
      <div 
        class="nav-item" 
        :class="{ active: currentRoute === '/demo' }"
        @click="navigateTo('/demo')"
      >
        <div class="nav-icon"><i class="bi bi-layout-text-sidebar-reverse"></i></div>
        <div class="nav-label">Demo Workspace</div>
      </div>

      <div class="nav-section">Main Page</div>
      <div class="nav-item" @click="navigateTo('/#features')">
        <div class="nav-icon"><i class="bi bi-stars"></i></div>
        <div class="nav-label">Features</div>
      </div>
      <div class="nav-item" @click="navigateTo('/#study')">
        <div class="nav-icon"><i class="bi bi-journal-text"></i></div>
        <div class="nav-label">Study</div>
      </div>
      <div class="nav-item" @click="navigateTo('/#metrics')">
        <div class="nav-icon"><i class="bi bi-graph-up"></i></div>
        <div class="nav-label">Metrics</div>
      </div>
      <div class="nav-item" @click="navigateTo('/#about')">
        <div class="nav-icon"><i class="bi bi-people"></i></div>
        <div class="nav-label">About</div>
      </div>

      <div class="nav-section">Legacy App</div>
      <div 
        class="nav-item" 
        :class="{ active: currentRoute === '/home' }"
        @click="navigateTo('/home')"
      >
        <div class="nav-icon"><i class="bi bi-clipboard2-pulse"></i></div>
        <div class="nav-label">Dashboard</div>
      </div>
      <div 
        class="nav-item" 
        :class="{ active: currentRoute === '/upload-cxr' }"
        @click="navigateTo('/upload-cxr')"
      >
        <div class="nav-icon"><i class="bi bi-cloud-upload"></i></div>
        <div class="nav-label">Upload CXR</div>
      </div>
      <div 
        class="nav-item" 
        :class="{ active: currentRoute === '/annotate' }"
        @click="navigateTo('/annotate')"
      >
        <div class="nav-icon"><i class="bi bi-pen"></i></div>
        <div class="nav-label">Annotate</div>
      </div>
    </div>
    <div class="nav-footer">
      <div v-if="hasToken" class="nav-item" @click="logout">
        <div class="nav-icon"><i class="bi bi-box-arrow-right"></i></div>
        <div class="nav-label">Logout</div>
      </div>
      <div v-else class="nav-item" @click="navigateTo('/login')">
        <div class="nav-icon"><i class="bi bi-box-arrow-in-right"></i></div>
        <div class="nav-label">Sign in</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NavSidebar',
  computed: {
    currentRoute() {
      return this.$route.path;
    },
    hasToken() {
      return Boolean(localStorage.getItem('authToken'));
    }
  },
  methods: {
    navigateTo(route) {
      if (this.currentRoute !== route) {
        this.$router.push(route);
      }
    },
    logout() {
      localStorage.removeItem('authToken');
      this.$router.push('/login');
    }
  }
}
</script>

<style>
/* Sidebar styling with higher specificity and !important flags */
.app-layout-container .nav-sidebar {
  width: 196px !important;
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  display: flex !important;
  flex-direction: column !important;
  height: 100vh !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  z-index: 100 !important;
}

.app-layout-container .logo-container {
  padding: 0.7rem 0.8rem !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  border-bottom: 1px solid var(--border) !important;
}

.app-layout-container .logo-link {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  border-radius: 8px !important;
  padding: 4px 6px !important;
  transition: background 0.2s ease !important;
}

.app-layout-container .logo-link:hover {
  background: var(--surface-2) !important;
}

.app-layout-container .sidebar-logo {
  height: 25px !important;
  width: auto !important;
  max-width: 190px !important;
  display: block !important;
}

.app-layout-container .nav-items {
  flex-grow: 1 !important;
  padding: 0.45rem 0 !important;
  overflow-y: auto !important;
}

.app-layout-container .nav-section {
  padding: 0.35rem 0.9rem 0.15rem 0.9rem !important;
  font-size: 0.62rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
  opacity: 0.9 !important;
  margin-top: 0.25rem !important;
}

.app-layout-container .nav-item {
  display: flex !important;
  align-items: center !important;
  padding: 0.55rem 0.9rem !important;
  color: var(--text-2) !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  border-left: 3px solid transparent !important;
}

.app-layout-container .nav-item:hover {
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
}

.app-layout-container .nav-item.active {
  background-color: var(--primary-soft) !important;
  color: var(--primary) !important;
  border-left: 3px solid var(--primary) !important;
}

.app-layout-container .nav-icon {
  font-size: 0.95rem !important;
  width: 18px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.app-layout-container .nav-label {
  margin-left: 0.65rem !important;
  font-weight: 500 !important;
  font-size: 0.78rem !important;
}

.app-layout-container .nav-footer {
  padding: 0.45rem 0 !important;
  border-top: 1px solid var(--border) !important;
}
</style> 
