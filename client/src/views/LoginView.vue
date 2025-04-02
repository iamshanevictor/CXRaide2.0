<template>
  <div class="login">
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
          "https://cxraide-backend.onrender.com/login",
          {
            username: this.username,
            password: this.password,
          }
        );

        localStorage.setItem("authToken", response.data.token);
        this.$router.push("/");
      } catch (error) {
        alert("Login failed");
      }
    },
  },
};
</script>
