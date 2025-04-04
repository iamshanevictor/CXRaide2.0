<template>
  <div class="home">
    <div class="header">
      <h1>Welcome to CXRaide, {{ username }}</h1>
      <div class="actions">
        <button @click="runDiagnostics" class="btn btn-secondary">
          Run Network Diagnostics
        </button>
        <button @click="logout" class="btn btn-primary">Logout</button>
      </div>
    </div>

    <div class="content">
      <div class="info-panel">
        <h2>Connection Info</h2>
        <p>
          <strong>Status:</strong>
          <span
            :class="
              connectionStatus === 'Connected' ? 'status-good' : 'status-error'
            "
            >{{ connectionStatus }}</span
          >
        </p>
        <p><strong>API URL:</strong> {{ apiUrl }}</p>
        <p>
          <strong>Session:</strong>
          <span :class="isAuthenticated ? 'status-good' : 'status-error'">{{
            isAuthenticated ? "Active" : "Not Authenticated"
          }}</span>
        </p>
      </div>

      <div v-if="isLoading" class="loading">Loading...</div>
    </div>
  </div>
</template>

<script>
import { apiUrl, logout, checkSession } from "../utils/api";
import { runNetworkTest } from "../utils/network-test";

export default {
  data() {
    return {
      apiUrl: apiUrl,
      username: "User",
      isLoading: true,
      isAuthenticated: false,
      connectionStatus: "Checking...",
    };
  },
  async mounted() {
    // Check authentication status
    this.isLoading = true;

    try {
      // Extract username from token if available
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          // JWT tokens are in format header.payload.signature
          const payload = token.split(".")[1];
          const decodedData = JSON.parse(atob(payload));
          this.username = decodedData.username || "User";
          console.log("Authenticated as:", this.username);
        } catch (e) {
          console.error("Error parsing token:", e);
          this.username = "User";
        }
      }

      // Verify session is active
      const sessionResponse = await checkSession();
      this.isAuthenticated = sessionResponse.data.valid;
      this.connectionStatus = "Connected";
      console.log("Session check result:", sessionResponse.data);
    } catch (error) {
      console.error("Error checking session:", error);
      this.connectionStatus = "Error";
      this.isAuthenticated = false;

      // If session check fails, redirect to login
      if (error.response?.status === 401) {
        console.log("Session invalid, redirecting to login");
        this.$router.push("/login");
      }
    } finally {
      this.isLoading = false;
    }
  },
  methods: {
    async logout() {
      try {
        this.isLoading = true;
        await logout();
        this.$router.push("/login");
      } catch (error) {
        console.error("Logout error:", error);
      } finally {
        this.isLoading = false;
      }
    },
    runDiagnostics() {
      runNetworkTest();
    },
  },
};
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.btn:hover {
  opacity: 0.9;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-panel {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

h2 {
  margin-top: 0;
  color: #2c3e50;
}

.status-good {
  color: #27ae60;
  font-weight: bold;
}

.status-error {
  color: #e74c3c;
  font-weight: bold;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100px;
  font-size: 18px;
  color: #7f8c8d;
}
</style>
