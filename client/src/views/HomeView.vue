<template>
  <div class="home">
    <h1>Welcome to CXRaide</h1>
    <button @click="handleLogout">Logout</button>
  </div>
</template>

<script>
export default {
  methods: {
    handleLogout() {
      localStorage.removeItem("authToken");
      this.$router.push("/login");
    },
  },
};
</script>
