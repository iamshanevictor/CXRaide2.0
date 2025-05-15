<template>
  <div class="app-header">
    <div class="page-title">
      <h1>
        <slot name="title">Page Title</slot>
      </h1>
    </div>
    
    <div class="header-actions">
      <button class="icon-button dark-mode-toggle">
        <span class="icon"><i class="bi bi-moon"></i></span>
      </button>
      <button class="icon-button notifications">
        <span class="icon"><i class="bi bi-bell"></i></span>
      </button>
      <div class="user-dropdown">
        <div class="user-avatar" @click="toggleUserMenu">
          {{ username ? username.charAt(0).toUpperCase() : "U" }}
        </div>
        <div class="dropdown-menu" v-show="showUserMenu">
          <div class="dropdown-item" @click="openUserSettings">
            <span class="dropdown-icon"><i class="bi bi-person-gear"></i></span>
            <span>User Settings</span>
          </div>
          <div class="dropdown-item" @click="logout">
            <span class="dropdown-icon"><i class="bi bi-box-arrow-right"></i></span>
            <span>Logout</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppHeader',
  props: {
    username: {
      type: String,
      default: 'User'
    }
  },
  data() {
    return {
      showUserMenu: false
    };
  },
  mounted() {
    // Add click event listener to document to close dropdown when clicking outside
    document.addEventListener('click', this.closeUserMenu);
  },
  beforeUnmount() {
    // Remove event listener when component is destroyed
    document.removeEventListener('click', this.closeUserMenu);
  },
  methods: {
    toggleUserMenu(event) {
      event.stopPropagation();
      this.showUserMenu = !this.showUserMenu;
    },
    openUserSettings() {
      console.log('Open user settings');
      this.showUserMenu = false;
      this.$emit('open-settings');
    },
    closeUserMenu(e) {
      // Close the menu when clicking outside
      if (this.showUserMenu && !e.target.closest('.user-dropdown')) {
        this.showUserMenu = false;
      }
    },
    logout() {
      this.$emit('logout');
    }
  }
};
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  width: 100%;
}

.page-title h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0;
  color: #f3f4f6;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Default styling for all icon buttons */
.icon-button {
  border: none;
  border-radius: 50%;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Dark styling specifically for dark mode and notification buttons */
.dark-mode-toggle,
.notifications {
  background: rgba(13, 31, 65, 0.9);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.dark-mode-toggle:hover,
.notifications:hover {
  background: rgba(23, 41, 75, 0.9);
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.4);
  transform: translateY(-2px);
}

/* Blue styling for user avatar */
.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
  color: white;
}

.icon-button .icon {
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 200px;
  background: rgba(15, 23, 42, 0.95);
  border-radius: 0.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3), 0 0 5px rgba(59, 130, 246, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: hidden;
  z-index: 100;
  transform-origin: top right;
  animation: dropdown-appear 0.2s ease-out forwards;
}

@keyframes dropdown-appear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.dropdown-item {
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: rgba(59, 130, 246, 0.15);
}

.dropdown-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  width: 20px;
}

.dropdown-item:not(:last-child) {
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}
</style> 