<template>
  <div class="nav-sidebar">
    <div class="logo-container">
      <img src="@/assets/LOGO1.png" alt="CXRaide Logo" class="sidebar-logo" />
    </div>
    <div class="nav-items">
      <div 
        class="nav-item" 
        :class="{ active: currentRoute === 'home' }"
        @click="navigate('/home')"
      >
        <div class="nav-icon"><i class="bi bi-clipboard2-pulse"></i></div>
        <div class="nav-label">Dashboard</div>
      </div>
      <div 
        class="nav-item" 
        :class="{ active: currentRoute === 'upload-cxr' }"
        @click="navigate('/upload-cxr')"
      >
        <div class="nav-icon"><i class="bi bi-cloud-upload"></i></div>
        <div class="nav-label">Upload CXR</div>
      </div>
      <div 
        class="nav-item" 
        :class="{ active: currentRoute === 'annotate' }"
        @click="navigate('/annotate')"
      >
        <div class="nav-icon"><i class="bi bi-pen"></i></div>
        <div class="nav-label">Annotate</div>
      </div>
      <div 
        class="nav-item"
        :class="{ active: currentRoute === 'reports' }"
        @click="navigate('/reports')"
      >
        <div class="nav-icon"><i class="bi bi-file-earmark-text"></i></div>
        <div class="nav-label">Reports</div>
      </div>
      <div 
        class="nav-item"
        :class="{ active: currentRoute === 'datasets' }"
        @click="navigate('/datasets')"
      >
        <div class="nav-icon"><i class="bi bi-database"></i></div>
        <div class="nav-label">Datasets</div>
      </div>
      <div 
        class="nav-item"
        :class="{ active: currentRoute === 'settings' }"
        @click="navigate('/settings')"
      >
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
  name: 'AppSidebar',
  props: {
    currentRoute: {
      type: String,
      default: 'home'
    }
  },
  methods: {
    navigate(route) {
      // Only navigate if we're not already on the page
      if (this.$router.currentRoute.value.path !== route) {
        this.$router.push(route);
      }
    },
    logout() {
      this.$emit('logout');
    }
  }
};
</script>

<style scoped>
/* Sidebar Navigation Styles */
.nav-sidebar {
  width: 240px;
  background: rgba(15, 23, 42, 0.8);
  border-right: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  padding: 25px 0;
}

.sidebar-logo {
  width: 180px;
  height: auto;
  filter: drop-shadow(0 0 8px rgba(93, 175, 255, 0.4));
}

.nav-items {
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.9rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(59, 130, 246, 0.1);
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.15);
  border-left: 3px solid #3b82f6;
}

.nav-icon {
  margin-right: 1rem;
  font-size: 1.1rem;
  opacity: 0.8;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
}

.nav-icon i {
  font-size: 1.2rem;
}

.nav-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #e5e7eb;
}

.nav-footer {
  padding: 1.5rem 0;
  border-top: 1px solid rgba(59, 130, 246, 0.1);
}
</style> 