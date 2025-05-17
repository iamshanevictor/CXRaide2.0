<template>
  <div class="header-bar">
    <h1>
      <slot name="title">Dashboard</slot>
      <slot name="subtitle"></slot>
    </h1>
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
  name: "HeaderBar",
  data() {
    return {
      showUserMenu: false,
    };
  },
  props: {
    username: {
      type: String,
      default: "",
    },
  },
  methods: {
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    openUserSettings() {
      // Placeholder for future implementation
      this.showUserMenu = false; 
    },
    logout() {
      localStorage.removeItem("authToken");
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

h1 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
}

.highlight {
  color: #3b82f6;
  position: relative;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-button {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: #94a3b8;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-button:hover {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.icon {
  font-size: 1.2rem;
}

.user-dropdown {
  position: relative;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(45deg, #3b82f6, #93c5fd);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: transform 0.2s;
}

.user-avatar:hover {
  transform: translateY(-2px);
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 50px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  width: 200px;
  z-index: 100;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.dropdown-item {
  padding: 0.8rem 1rem;
  display: flex;
  align-items: center;
  color: #e2e8f0;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: rgba(59, 130, 246, 0.1);
}

.dropdown-icon {
  margin-right: 0.75rem;
  width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style> 