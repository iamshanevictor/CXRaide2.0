<template>
  <div class="header-bar">
    <h1>
      <slot name="title">Dashboard</slot>
      <slot name="subtitle"></slot>
    </h1>
    <div class="header-actions">
      <button class="icon-button dark-mode-toggle" type="button" @click="toggleTheme" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
        <span class="icon"><i :class="isDark ? 'bi bi-sun' : 'bi bi-moon'" /></span>
      </button>

      <button class="icon-button notifications" type="button" title="Notifications (demo)">
        <span class="icon"><i class="bi bi-bell" /></span>
      </button>

      <div v-if="hasToken" class="user-dropdown">
        <div class="user-avatar" @click="toggleUserMenu" :title="username || 'User'">
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

      <button v-else class="sign-in" type="button" @click="$router.push('/login')">
        Sign in
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "HeaderBar",
  data() {
    return {
      showUserMenu: false,
      isDark: true,
    };
  },
  props: {
    username: {
      type: String,
      default: "",
    },
  },
  computed: {
    hasToken() {
      return Boolean(localStorage.getItem("authToken"));
    },
  },
  mounted() {
    // Initialize theme from storage
    const saved = localStorage.getItem("cxraide_theme");
    // Default is dark unless user explicitly set light
    this.isDark = saved !== "light";
    document.body.classList.toggle("theme-light", !this.isDark);
  },
  methods: {
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    toggleTheme() {
      this.isDark = !this.isDark;
      document.body.classList.toggle("theme-light", !this.isDark);
      localStorage.setItem("cxraide_theme", this.isDark ? "dark" : "light");
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
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

h1 {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.highlight {
  color: var(--primary);
  position: relative;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-button {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--muted);
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
  background: var(--surface-2);
  color: var(--primary);
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
  background: linear-gradient(45deg, var(--primary), rgba(147, 197, 253, 1));
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
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 200px;
  z-index: 100;
  box-shadow: var(--shadow-md);
}

.dropdown-item {
  padding: 0.8rem 1rem;
  display: flex;
  align-items: center;
  color: var(--text);
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: var(--surface-2);
}

.dropdown-icon {
  margin-right: 0.75rem;
  width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sign-in {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  padding: 10px 12px;
  border-radius: 10px;
  font-weight: 650;
  cursor: pointer;
}

.sign-in:hover { background: var(--surface-2); }
</style> 