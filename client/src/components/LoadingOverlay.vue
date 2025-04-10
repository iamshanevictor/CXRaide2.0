<template>
  <div class="loading-overlay" :class="{ 'fixed-position': fixed }">
    <div class="loading-container">
      <div class="loader-ring">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      <div class="loading-text">
        {{ message || "Loading..." }}
      </div>
      <div class="loading-dots"><span></span><span></span><span></span></div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LoadingOverlay",
  props: {
    message: {
      type: String,
      default: "Loading...",
    },
    fixed: {
      type: Boolean,
      default: true,
    },
  },
};
</script>

<style scoped>
.loading-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(
    135deg,
    rgba(9, 12, 20, 0.9) 0%,
    rgba(16, 23, 42, 0.9) 100%
  );
  backdrop-filter: blur(5px);
  z-index: 9999;
}

.fixed-position {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.loading-container {
  text-align: center;
}

.loader-ring {
  display: inline-block;
  position: relative;
  width: 80px;
  height: 80px;
}

.loader-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 64px;
  height: 64px;
  margin: 8px;
  border: 6px solid #3b82f6;
  border-radius: 50%;
  animation: loader-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border-color: #3b82f6 transparent transparent transparent;
}

.loader-ring div:nth-child(1) {
  animation-delay: -0.45s;
}

.loader-ring div:nth-child(2) {
  animation-delay: -0.3s;
}

.loader-ring div:nth-child(3) {
  animation-delay: -0.15s;
}

.loading-text {
  margin-top: 1.5rem;
  font-size: 1.2rem;
  font-weight: 500;
  color: #e5e7eb;
  letter-spacing: 0.5px;
}

.loading-dots {
  display: flex;
  justify-content: center;
  margin-top: 0.75rem;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  margin: 0 4px;
  background-color: #3b82f6;
  border-radius: 50%;
  display: inline-block;
  animation: dots 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loader-ring {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dots {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.2;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
