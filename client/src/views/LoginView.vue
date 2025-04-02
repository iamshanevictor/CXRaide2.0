<template>
  <div class="login">
    <h1>CXRaide Login</h1>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="Username" />
      <input v-model="password" type="password" placeholder="Password" />
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      username: "",
      password: "",
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post(
          import.meta.env.VITE_API_URL + "/login",
          {
            username: this.username,
            password: this.password,
          }
        );

        localStorage.setItem("authToken", response.data.token);
        this.$router.push("/");
      } catch (error) {
        alert("Login failed: " + error.response?.data?.message);
      }
    },
  },
};
</script>
