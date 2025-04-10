<template>
  <div class="ai-model-loader">
    <div class="loader-content">
      <div class="scanner-container">
        <div class="scanner-light"></div>
        <div class="scan-line"></div>
        <div class="scanner-frame">
          <div class="corner top-left"></div>
          <div class="corner top-right"></div>
          <div class="corner bottom-left"></div>
          <div class="corner bottom-right"></div>
        </div>
      </div>

      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
      </div>

      <div class="loader-details">
        <h3 class="loader-title">{{ title || "Processing Image" }}</h3>
        <div class="loader-message">
          {{ message || "Analyzing with AI model..." }}
        </div>
        <div class="ai-steps">
          <div
            class="step"
            :class="{ active: currentStep >= 1, completed: currentStep > 1 }"
          >
            <div class="step-icon">
              <i class="bi bi-image"></i>
            </div>
            <div class="step-label">Image Processing</div>
          </div>
          <div
            class="step"
            :class="{ active: currentStep >= 2, completed: currentStep > 2 }"
          >
            <div class="step-icon">
              <i class="bi bi-cpu"></i>
            </div>
            <div class="step-label">AI Analysis</div>
          </div>
          <div
            class="step"
            :class="{ active: currentStep >= 3, completed: currentStep > 3 }"
          >
            <div class="step-icon">
              <i class="bi bi-bounding-box"></i>
            </div>
            <div class="step-label">Generating Results</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AIModelLoader",
  props: {
    title: {
      type: String,
      default: "Processing Image",
    },
    message: {
      type: String,
      default: "Analyzing with AI model...",
    },
  },
  data() {
    return {
      currentStep: 1,
      intervalId: null,
    };
  },
  mounted() {
    // Simulate progress through steps for better user experience
    this.intervalId = setInterval(() => {
      if (this.currentStep < 3) {
        this.currentStep++;
      }
    }, 1500);
  },
  beforeUnmount() {
    clearInterval(this.intervalId);
  },
};
</script>

<style scoped>
.ai-model-loader {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    rgba(9, 12, 20, 0.92) 0%,
    rgba(16, 23, 42, 0.92) 100%
  );
  backdrop-filter: blur(8px);
  z-index: 1000;
}

.loader-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 500px;
  width: 90%;
}

.scanner-container {
  position: relative;
  width: 240px;
  height: 240px;
  margin-bottom: 20px;
  overflow: hidden;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.2);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
}

.scanner-light {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at center,
    rgba(59, 130, 246, 0.15) 0%,
    rgba(59, 130, 246, 0.05) 30%,
    rgba(59, 130, 246, 0) 70%
  );
  animation: pulse 3s infinite;
}

.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(59, 130, 246, 0.7) 50%,
    transparent 100%
  );
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.7);
  animation: scan 2s ease-in-out infinite;
}

.scanner-frame {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
}

.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border-color: #3b82f6;
  border-style: solid;
  border-width: 0;
}

.top-left {
  top: 0;
  left: 0;
  border-top-width: 3px;
  border-left-width: 3px;
  border-top-left-radius: 5px;
}

.top-right {
  top: 0;
  right: 0;
  border-top-width: 3px;
  border-right-width: 3px;
  border-top-right-radius: 5px;
}

.bottom-left {
  bottom: 0;
  left: 0;
  border-bottom-width: 3px;
  border-left-width: 3px;
  border-bottom-left-radius: 5px;
}

.bottom-right {
  bottom: 0;
  right: 0;
  border-bottom-width: 3px;
  border-right-width: 3px;
  border-bottom-right-radius: 5px;
}

.progress-container {
  width: 240px;
  margin: 10px 0 15px;
}

.progress-bar {
  height: 6px;
  background: rgba(59, 130, 246, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  width: 0;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
  border-radius: 3px;
  animation: progress 6s ease-in-out;
  animation-fill-mode: forwards;
}

.loader-details {
  text-align: center;
}

.loader-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #f3f4f6;
  margin: 0 0 8px 0;
}

.loader-message {
  font-size: 1rem;
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.ai-steps {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 10px;
  position: relative;
}

.ai-steps::before {
  content: "";
  position: absolute;
  top: 25px;
  left: 40px;
  right: 40px;
  height: 2px;
  background: rgba(59, 130, 246, 0.2);
  z-index: 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 80px;
  z-index: 1;
}

.step-icon {
  width: 40px;
  height: 40px;
  background: rgba(15, 23, 42, 0.9);
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  position: relative;
  transition: all 0.3s ease;
}

.step-icon i {
  color: #94a3b8;
  font-size: 1.1rem;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 0.75rem;
  color: #94a3b8;
  text-align: center;
  transition: all 0.3s ease;
}

.step.active .step-icon {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.step.active .step-icon i {
  color: #3b82f6;
}

.step.active .step-label {
  color: #e5e7eb;
  font-weight: 500;
}

.step.completed .step-icon {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.step.completed .step-icon i {
  color: #10b981;
}

@keyframes scan {
  0% {
    top: 0;
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    top: 100%;
    opacity: 0;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

@keyframes progress {
  0% {
    width: 0;
  }
  20% {
    width: 30%;
  }
  50% {
    width: 60%;
  }
  80% {
    width: 85%;
  }
  100% {
    width: 100%;
  }
}
</style>
