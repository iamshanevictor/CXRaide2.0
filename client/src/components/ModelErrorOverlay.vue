<template>
  <div class="model-error-overlay">
    <div class="error-container">
      <div class="error-icon">
        <i class="bi bi-exclamation-triangle-fill"></i>
      </div>
      <div class="error-content">
        <h3 class="error-title">{{ title }}</h3>
        <p class="error-message">{{ message }}</p>
        <button v-if="showRetry" @click="$emit('retry')" class="retry-button">
          <i class="bi bi-arrow-clockwise"></i>
          <span>Try Again</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ModelErrorOverlay",
  props: {
    title: {
      type: String,
      default: "Model could not be loaded",
    },
    message: {
      type: String,
      default: "Please try again later.",
    },
    showRetry: {
      type: Boolean,
      default: true,
    },
  },
  emits: ["retry"],
};
</script>

<style scoped>
.model-error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  z-index: 1000;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: 8px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  text-align: center;
}

.error-icon {
  font-size: 2.5rem;
  color: rgb(220, 38, 38);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(220, 38, 38, 0.1);
}

.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #f3f4f6;
  margin: 0 0 0.75rem 0;
}

.error-message {
  font-size: 1rem;
  color: #d1d5db;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.retry-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f3f4f6;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.retry-button:active {
  transform: translateY(0);
}

.retry-button i {
  font-size: 1.1rem;
}
</style>
