<template>
  <div class="nav-sidebar">
    <div class="logo-container">
      <img
        src="@/assets/LOGO1.png"
        alt="CXRaide Logo"
        class="sidebar-logo"
      />
    </div>
    <div class="nav-items">
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
      <div class="nav-item">
        <div class="nav-icon"><i class="bi bi-file-earmark-text"></i></div>
        <div class="nav-label">Reports</div>
      </div>
      <div class="nav-item">
        <div class="nav-icon"><i class="bi bi-database"></i></div>
        <div class="nav-label">Datasets</div>
      </div>
      <div class="nav-item">
        <div class="nav-icon"><i class="bi bi-gear"></i></div>
        <div class="nav-label">Settings</div>
      </div>
    </div>
    <div class="nav-footer">
      <div class="nav-item" @click="logout">
        <div class="nav-icon"><i class="bi bi-box-arrow-right"></i></div>
        <div class="nav-label">Logout</div>
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
  width: 240px !important;
  background: rgba(15, 23, 42, 0.8) !important;
  backdrop-filter: blur(10px) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
  display: flex !important;
  flex-direction: column !important;
  height: 100vh !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  z-index: 100 !important;
}

.app-layout-container .logo-container {
  padding: 1.5rem !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.app-layout-container .sidebar-logo {
  max-width: 160px !important;
  height: auto !important;
}

.app-layout-container .nav-items {
  flex-grow: 1 !important;
  padding: 1rem 0 !important;
  overflow-y: auto !important;
}

.app-layout-container .nav-item {
  display: flex !important;
  align-items: center !important;
  padding: 0.85rem 1.5rem !important;
  color: #94a3b8 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  border-left: 3px solid transparent !important;
}

.app-layout-container .nav-item:hover {
  background-color: rgba(59, 130, 246, 0.1) !important;
  color: #e2e8f0 !important;
}

.app-layout-container .nav-item.active {
  background-color: rgba(59, 130, 246, 0.15) !important;
  color: #3b82f6 !important;
  border-left: 3px solid #3b82f6 !important;
}

.app-layout-container .nav-icon {
  font-size: 1.2rem !important;
  width: 24px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.app-layout-container .nav-label {
  margin-left: 1rem !important;
  font-weight: 500 !important;
  font-size: 0.95rem !important;
}

.app-layout-container .nav-footer {
  padding: 1rem 0 !important;
  border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
}
</style> 