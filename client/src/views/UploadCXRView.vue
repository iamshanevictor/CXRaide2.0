<template>
  <div class="app-layout">
    <!-- Sidebar Navigation -->
    <div class="nav-sidebar">
      <div class="logo-container">
        <img src="@/assets/LOGO1.png" alt="CXRaide Logo" class="sidebar-logo" />
      </div>
      <div class="nav-items">
        <div class="nav-item" @click="$router.push('/home')">
          <div class="nav-icon"><i class="bi bi-clipboard2-pulse"></i></div>
          <div class="nav-label">Dashboard</div>
        </div>
        <div class="nav-item active">
          <div class="nav-icon"><i class="bi bi-cloud-upload"></i></div>
          <div class="nav-label">Upload CXR</div>
        </div>
        <div class="nav-item" @click="$router.push('/annotate')">
          <div class="nav-icon"><i class="bi bi-pen"></i></div>
          <div class="nav-label">Annotate</div>
        </div>
        <div class="nav-item">
          <div class="nav-icon"><i class="bi bi-file-earmark-text"></i></div>
          <div class="nav-label">Reports</div>
        </div>
        <div class="nav-item">
          <div class="nav-icon"><i class="bi bi-database"></i></div>
          <div class="nav-label">Datasets</div>
        </div>
        <div class="nav-item">
          <div class="nav-icon"><i class="bi bi-gear"></i></div>
          <div class="nav-label">Settings</div>
        </div>
      </div>
      <div class="nav-footer">
        <div class="nav-item" @click="logout">
          <div class="nav-icon"><i class="bi bi-box-arrow-right"></i></div>
          <div class="nav-label">Logout</div>
        </div>
      </div>
    </div>

    <div class="upload-cxr-container">
      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>Upload CXR</h1>
          <p class="subtitle">Upload and analyze chest X-rays with AI</p>
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
                <span class="dropdown-icon"
                  ><i class="bi bi-person-gear"></i
                ></span>
                <span>User Settings</span>
              </div>
              <div class="dropdown-item" @click="logout">
                <span class="dropdown-icon"
                  ><i class="bi bi-box-arrow-right"></i
                ></span>
                <span>Logout</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="content-area">
        <!-- Upload Panel -->
        <div class="upload-panel">
          <div class="file-info-bar">
            <span
              >Raw CXRay Name:
              {{ imageFile ? imageFile.name : "No file selected" }}</span
            >
            <button
              class="upload-btn"
              @click="triggerFileUpload"
              :disabled="isAnalyzing"
            >
              <i class="bi bi-cloud-arrow-up"></i> Upload X-ray
            </button>
          </div>

          <!-- Upload area or preview -->
          <div
            class="upload-area"
            :class="{ 'has-image': currentImage }"
            @click="triggerFileUpload"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleFileDrop"
          >
            <div
              v-if="!currentImage"
              class="upload-placeholder"
              :class="{ dragging: isDragging }"
            >
              <i class="bi bi-cloud-arrow-up"></i>
              <p>
                Click to upload or drag & drop<br />Supported formats: JPEG, PNG
              </p>
            </div>
            <div v-else class="image-preview">
              <img :src="currentImage" alt="Chest X-Ray Preview" />
              <button class="remove-image-btn" @click.stop="removeImage">
                <i class="bi bi-x-circle-fill"></i>
              </button>
            </div>
            <input
              type="file"
              ref="fileInput"
              accept="image/*"
              class="file-input"
              @change="handleFileUpload"
            />
          </div>

          <!-- Model Selection - Simplified UI -->
          <div
            class="model-selection-compact"
            :class="{ disabled: !currentImage }"
          >
            <h3>AI Model Selection</h3>
            <div class="model-selection-container">
              <div class="select-container">
                <select
                  v-model="selectedModel"
                  :disabled="!currentImage || isAnalyzing"
                >
                  <option value="CXR-IT2">SSD300_VGG16-CXR9 v2</option>
                  <option value="CXR-IT3">SSD300_VGG16-CXR6plus3 v1</option>
                </select>
                <div class="select-arrow">
                  <i class="bi bi-chevron-down"></i>
                </div>
              </div>
              <p class="model-description">
                {{
                  selectedModel === "CXR-IT2"
                    ? "SSD-based model for detecting 9 types of thoracic pathologies."
                    : "Enhanced combined model with improved detection of subtle findings."
                }}
              </p>
            </div>
            <button
              class="analyze-button"
              :disabled="!currentImage || isAnalyzing"
              @click="analyzeImage"
            >
              <i class="bi bi-search"></i> Analyze with AI
            </button>
          </div>
        </div>

        <!-- Results Panel -->
        <div class="results-panel">
          <div class="results-header">
            <h2>AI Results</h2>
          </div>

          <div
            v-if="!annotatedImage && !isAnalyzing"
            class="placeholder-ai-message"
          >
            <i class="bi bi-robot"></i>
            <p>AI annotations will appear here</p>
          </div>

          <!-- AI annotations - matching the structure from AnnotateView.vue -->
          <div v-if="annotatedImage" class="ai-annotations">
            <!-- Mock model banner -->
            <div v-if="isUsingMockModel" class="model-status-banner">
              <i class="bi bi-info-circle-fill"></i>
              <span
                >Using mock AI predictions (server is using lightweight
                model)</span
              >
            </div>

            <!-- Xray image container with dynamic sizing based on results collapsed state -->
            <div
              class="xray-image ai-image"
              :class="{ 'collapsed-view': !isResultsCollapsed }"
            >
              <!-- Use the pre-rendered annotated image with bounding boxes -->
              <img
                :src="annotatedImage"
                alt="AI annotated X-ray"
                class="standardized-image result-image"
              />

              <!-- Loading state with blue filter and indicators -->
              <div
                v-if="isAnalyzing && !annotatedImage && !modelError"
                class="ai-processing-overlay"
              >
                <div class="processing-frame">
                  <div class="processing-scan-line"></div>
                </div>
                <div class="processing-status">
                  <h3>Processing Image</h3>
                  <p>Analyzing with AI model...</p>

                  <div class="processing-steps">
                    <div
                      class="processing-step"
                      :class="{ active: processingStep === 1 }"
                    >
                      <i class="bi bi-image"></i>
                      <span>Image Processing</span>
                    </div>
                    <div
                      class="processing-step"
                      :class="{ active: processingStep === 2 }"
                    >
                      <i class="bi bi-cpu"></i>
                      <span>AI Analysis</span>
                    </div>
                    <div
                      class="processing-step"
                      :class="{ active: processingStep === 3 }"
                    >
                      <i class="bi bi-grid"></i>
                      <span>Generating Results</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI Detection Results section - now always shown but visibility managed by CSS -->
            <div
              class="ai-detection-section"
              :class="{ expanded: !isResultsCollapsed }"
            >
              <div class="detection-header" @click="toggleResults($event)">
                <h3>AI Detection Results:</h3>
                <button class="toggle-btn" @click.stop="toggleResults($event)">
                  <i
                    :class="
                      isResultsCollapsed
                        ? 'bi bi-chevron-down'
                        : 'bi bi-chevron-up'
                    "
                  ></i>
                </button>
              </div>

              <div
                class="detection-list"
                :class="{ expanded: !isResultsCollapsed }"
              >
                <div
                  class="detection-item"
                  v-for="(prediction, index) in aiPredictions"
                  :key="index"
                >
                  <div
                    class="detection-color-bar"
                    :style="{
                      backgroundColor: getColorForFinding(prediction.class),
                    }"
                  ></div>
                  <div class="detection-name">{{ prediction.class }}:</div>
                  <div
                    class="detection-value"
                    :style="{ color: getColorForFinding(prediction.class) }"
                  >
                    {{ formatConfidence(prediction.score) }}
                  </div>
                </div>
              </div>
            </div>

            <div class="action-buttons annotation-actions">
              <button class="action-button save-button" @click="downloadResult">
                <i class="bi bi-download"></i> Download
              </button>
              <button
                class="action-button expert-button"
                @click="resetAnalysis"
              >
                <i class="bi bi-arrow-counterclockwise"></i> New Analysis
              </button>
            </div>
          </div>

          <!-- Loading overlay -->
          <transition name="fade">
            <model-error-overlay
              v-if="modelError"
              :title="'Model could not be loaded'"
              :message="modelError"
              :show-retry="true"
              @retry="analyzeImage"
            />
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import { apiUrl, logout } from "../utils/api"; // Original line with unused apiUrl
import { logout } from "../utils/api"; // Keep only logout since apiUrl isn't used
import ModelService from "@/services/modelService";
// Remove or comment out the unused import
// import AIModelLoader from "../components/AIModelLoader.vue";
import ModelErrorOverlay from "../components/ModelErrorOverlay.vue";

export default {
  name: "UploadCXRView",
  components: {
    // Remove AIModelLoader from components if we're not using it
    // AIModelLoader,
    ModelErrorOverlay,
  },
  data() {
    return {
      currentImage: null,
      selectedModel: "CXR-IT3", // Default to the combined model
      isAnalyzing: false,
      annotatedImage: null,
      aiPredictions: [],
      imageFile: null,
      modelType: null,
      isResultsCollapsed: false, // Default to expanded results (visible)
      isDragging: false,
      username: "User",
      showUserMenu: false,
      isResultsPanelExpanded: false,
      isUsingMockModel: false,
      modelError: null, // Add this to track model errors
      processingStep: 1, // Track which processing step is active (1, 2, or 3)
      processingInterval: null, // For interval timer
    };
  },
  created() {
    try {
      // Extract username from token if available
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          const payload = token.split(".")[1];
          const decodedData = JSON.parse(atob(payload));
          this.username = decodedData.username || "User";
        } catch (e) {
          console.error("[Upload] Error parsing token:", e);
          this.username = "User";
        }
      }
    } catch (e) {
      console.error("[Upload] Error accessing localStorage:", e);
    }

    // Check model status on initialization
    this.checkModelStatus();
  },
  methods: {
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    openUserSettings() {
      console.log("[Upload] User settings clicked (not implemented yet)");
      this.showUserMenu = false;
      alert("User settings feature coming soon!");
    },
    closeUserMenu(e) {
      if (this.showUserMenu && !e.target.closest(".user-dropdown")) {
        this.showUserMenu = false;
      }
    },
    triggerFileUpload() {
      if (!this.isAnalyzing) {
        this.$refs.fileInput.click();
      }
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      // Check if the file is an image
      if (!file.type.match("image.*")) {
        alert("Please select an image file");
        return;
      }

      this.imageFile = file;
      const reader = new FileReader();

      reader.onload = (e) => {
        this.currentImage = e.target.result;
        // Reset results when new image is uploaded
        this.annotatedImage = null;
        this.aiPredictions = [];
      };

      reader.readAsDataURL(file);
    },
    handleFileDrop(event) {
      this.isDragging = false;
      const file = event.dataTransfer.files[0];
      if (!file) return;

      // Check if the file is an image
      if (!file.type.match("image.*")) {
        alert("Please select an image file");
        return;
      }

      this.imageFile = file;
      const reader = new FileReader();

      reader.onload = (e) => {
        this.currentImage = e.target.result;
        // Reset results when new image is uploaded
        this.annotatedImage = null;
        this.aiPredictions = [];
      };

      reader.readAsDataURL(file);
    },
    removeImage() {
      this.currentImage = null;
      this.annotatedImage = null;
      this.aiPredictions = [];
      this.imageFile = null;
      this.$refs.fileInput.value = "";
    },
    async analyzeImage() {
      if (!this.currentImage || this.isAnalyzing) return;

      try {
        this.isAnalyzing = true;
        this.modelError = null; // Reset any previous errors
        this.processingStep = 1; // Start with step 1 active

        // Set up a timer to cycle through the processing steps
        this.processingInterval = setInterval(() => {
          if (this.processingStep < 3) {
            this.processingStep++;
          } else {
            this.processingStep = 1;
          }
        }, 2000); // Change step every 2 seconds

        // First check model status
        const modelStatus = await ModelService.checkModelStatus();

        if (modelStatus.status === "loading") {
          clearInterval(this.processingInterval);
          this.modelError =
            "Model is still loading. Please wait a moment and try again.";
          return;
        } else if (
          modelStatus.status === "error" ||
          modelStatus.status === "not_loaded"
        ) {
          clearInterval(this.processingInterval);
          this.modelError =
            "Model could not be loaded. Please try again later.";
          return;
        }

        // Set model type based on selection
        if (this.selectedModel === "CXR-IT2") {
          this.modelType = "IT2";
        } else if (this.selectedModel === "CXR-IT3") {
          this.modelType = "IT3";
        } else {
          this.modelType = "combined"; // Default to combined model
        }

        // Create a FormData object to specify model
        const formData = new FormData();
        formData.append("model_type", this.modelType);

        // Download the image from the URL if we don't have the file object
        let imageFile = this.imageFile;
        if (!imageFile && this.currentImage) {
          const response = await fetch(this.currentImage);
          const blob = await response.blob();
          imageFile = new File([blob], "image.jpg", { type: "image/jpeg" });
        }

        // Get predictions from model service
        const result = await ModelService.predict(imageFile, formData);

        // Stop the step cycling interval
        clearInterval(this.processingInterval);

        // Check if using mock model
        if (result.using_mock_models) {
          this.isUsingMockModel = true;
        }

        // Update the annotated image
        this.annotatedImage = result.annotatedImage;

        // Process predictions
        if (result.predictions && result.predictions.length > 0) {
          this.aiPredictions = result.predictions.map((pred) => ({
            ...pred,
            class: pred.class || "Unknown",
            score: pred.score || 0,
            confidenceText: this.formatConfidence(
              pred.confidence || pred.score || 0
            ),
            color: this.getColorForFinding(pred.class || "Unknown"),
          }));
        } else {
          this.aiPredictions = [];
        }
      } catch (error) {
        clearInterval(this.processingInterval);
        console.error("Error analyzing image:", error);
        this.modelError =
          error.message || "Failed to analyze image. Please try again.";
      } finally {
        this.isAnalyzing = false;
      }
    },
    formatConfidence(score) {
      return `${Math.round(score * 100)}%`;
    },
    getConfidenceColor(score) {
      if (score >= 0.7) return "#10b981"; // Green for high confidence
      if (score >= 0.4) return "#f59e0b"; // Orange for medium confidence
      return "#ef4444"; // Red for low confidence
    },
    getColorForFinding(findingClass) {
      // Return specific colors for each finding type to match the colored bars in image
      const colorMap = {
        "Pleural thickening": "#9c59ff", // Purple
        Cardiomegaly: "#ef4444", // Red
        Infiltration: "#10b981", // Green
        "Pleural effusion": "#f59e0b", // Orange
        "Pulmonary fibrosis": "#ec4899", // Pink
      };

      return colorMap[findingClass] || "#3b82f6"; // Default to blue if not found
    },
    downloadResult() {
      if (!this.annotatedImage) return;

      // Create a temporary link element
      const link = document.createElement("a");
      link.href = this.annotatedImage;
      link.download = `CXRaide_${this.selectedModel}_${new Date()
        .toISOString()
        .slice(0, 10)}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    resetAnalysis() {
      this.annotatedImage = null;
      this.aiPredictions = [];
    },
    async logout() {
      try {
        await logout();
        localStorage.removeItem("authToken");
        this.$router.push("/login");
      } catch (error) {
        console.error("Logout error:", error);
        this.$router.push("/login");
      }
    },
    async checkModelStatus() {
      try {
        const modelStatus = await ModelService.checkModelStatus();

        // Check for model errors
        if (modelStatus.status === "loading") {
          this.modelError =
            "Model is still loading. Please wait a moment and try again.";
        } else if (
          modelStatus.status === "error" ||
          modelStatus.status === "not_loaded"
        ) {
          this.modelError =
            "Model could not be loaded. Please try again later.";
        }

        // Check if using mock models
        if (modelStatus.using_mock_models) {
          this.isUsingMockModel = true;
        }
      } catch (error) {
        console.error("Error checking model status:", error);
        this.modelError =
          "Unable to connect to model service. Please try again later.";
      }
    },
    toggleResults(event) {
      // Stop event propagation to prevent interference with image
      if (event) {
        event.stopPropagation();
      }

      // Toggle the collapsed state
      this.isResultsCollapsed = !this.isResultsCollapsed;

      // Allow time for the animation to complete
      if (!this.isResultsCollapsed) {
        // When expanding, ensure all items are visible
        setTimeout(() => {
          const detectionList = document.querySelector(".detection-list");
          if (detectionList) {
            detectionList.scrollTop = 0;
          }
        }, 300);
      }

      console.log("Results collapsed:", this.isResultsCollapsed);
    },
  },
  mounted() {
    document.addEventListener("click", this.closeUserMenu);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.closeUserMenu);
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
    }
  },
};
</script>

<style scoped>
/* Add navigation styles */
.app-layout {
  display: flex;
  min-height: 100vh;
}

.nav-sidebar {
  width: 240px;
  background: rgba(15, 23, 42, 0.8);
  border-right: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  padding: 25px 0;
}

.sidebar-logo {
  width: 180px;
  height: auto;
  filter: drop-shadow(0 0 8px rgba(93, 175, 255, 0.4));
}

.nav-items {
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.9rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(59, 130, 246, 0.1);
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.15);
  border-left: 3px solid #3b82f6;
}

.nav-icon {
  margin-right: 1rem;
  font-size: 1.1rem;
  opacity: 0.8;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
}

.nav-icon i {
  font-size: 1.2rem;
}

.nav-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #e5e7eb;
}

.nav-footer {
  padding: 1.5rem 0;
  border-top: 1px solid rgba(59, 130, 246, 0.1);
}

.upload-cxr-container {
  min-height: 100vh;
  padding: 1.5rem 2rem;
  margin: 0 auto;
  margin-left: 240px; /* Match sidebar width */
  width: calc(100% - 240px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-left {
  text-align: left;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #f3f4f6;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #94a3b8;
  font-size: 1rem;
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
  color: #e5e7eb;
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
  color: #e5e7eb;
}

.dropdown-item:not(:last-child) {
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.content-area {
  display: flex;
  gap: 2rem;
  height: calc(100vh - 120px);
  width: 100%;
  margin: 0;
  align-items: stretch;
}

.upload-panel,
.results-panel {
  flex: 1;
  background: #0f172a;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: auto;
}

.upload-panel {
  flex: 0.95;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 1rem;
  padding: 0 0 130px 0;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  position: relative;
}

.results-panel {
  flex: 1.05;
  background: rgba(15, 23, 42, 0.7);
  border-radius: 1rem;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  position: relative;
}

.upload-panel h2,
.results-panel h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  padding-bottom: 0.75rem;
}

.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #0f172a;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  color: #e5e7eb;
  font-size: 0.95rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  margin-bottom: 3px;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #4f94ff;
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.65rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-btn:hover:not(:disabled) {
  background: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-area {
  border: 2px dashed rgba(59, 130, 246, 0.4);
  border-radius: 0 0 0.75rem 0.75rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #0f172a;
  position: relative;
  overflow: hidden;
  height: 520px;
  margin-bottom: auto;
  flex-shrink: 0;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: rgba(15, 23, 42, 0.6);
}

.upload-area.has-image {
  border-style: solid;
  border-color: rgba(59, 130, 246, 0.6);
  padding: 0;
}

.upload-placeholder {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.upload-placeholder.dragging {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
}

.upload-placeholder i {
  font-size: 4rem;
  color: #3b82f6;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.upload-placeholder p {
  color: #94a3b8;
  font-size: 1.05rem;
  line-height: 1.6;
}

.image-preview {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 0.75rem;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}

.remove-image-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(239, 68, 68, 0.25);
  border: none;
  border-radius: 50%;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 10;
}

.remove-image-btn i {
  color: #ef4444;
  font-size: 1.4rem;
}

.remove-image-btn:hover {
  background: rgba(239, 68, 68, 0.4);
  transform: scale(1.1);
}

.file-input {
  display: none;
}

.model-selection-compact {
  margin-top: auto;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.75rem 0.75rem 0.75rem 0.75rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-left: 1rem;
  margin-right: 1rem;
  margin-bottom: 1rem;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

.model-selection-compact.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.model-selection-compact h3 {
  font-size: 1.05rem;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 0.4rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
}

.model-selection-container {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 0.5rem;
}

.model-description {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.4;
  margin: 0;
  padding-left: 0.5rem;
}

.select-container {
  position: relative;
  width: 100%;
}

.select-container select {
  width: 100%;
  padding: 0.85rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(59, 130, 246, 0.3);
  background: #0f172a;
  color: #e5e7eb;
  font-size: 0.95rem;
  appearance: none;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.select-container select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

.select-arrow {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #3b82f6;
}

.result-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
}

.analysis-result {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.ai-annotations {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: auto;
  overflow: visible;
  background: transparent;
  border: none;
  box-shadow: none;
}

.xray-image {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 1rem;
  overflow: hidden;
  margin-bottom: 1rem;
  border: none;
  height: 400px; /* Default height */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: height 0.3s ease;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.xray-image.collapsed-view {
  height: 250px; /* Smaller height when results are showing */
}

.ai-image {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #000;
  border-radius: 1rem;
}

.standardized-image {
  max-width: 85%;
  max-height: 85%;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.ai-confidence-summary {
  flex: 1;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid rgba(59, 130, 246, 0.2);
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: all 0.3s ease;
}

.ai-confidence-summary.collapsed {
  flex: 0;
  min-height: 60px;
}

.ai-confidence-summary.collapsed .confidence-list-wrapper {
  display: none;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  background: rgba(15, 23, 42, 0.9);
  cursor: pointer;
}

.confidence-list {
  padding: 0.75rem;
  max-height: unset;
  flex: 1;
  transition: all 0.3s ease;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.confidence-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-left: 4px solid transparent;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 4px;
}

.confidence-item:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateX(2px);
}

.toggle-btn {
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #e5e7eb;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background: rgba(59, 130, 246, 0.15);
}

.confidence-label {
  font-size: 1rem;
  font-weight: 500;
  color: #e5e7eb;
}

.confidence-value {
  font-size: 1.1rem;
  font-weight: 700;
  min-width: 50px;
  text-align: right;
}

.summary-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.placeholder-ai-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94a3b8;
  text-align: center;
  padding: 2rem;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 1rem;
  backdrop-filter: blur(8px);
}

.placeholder-ai-message i {
  font-size: 4rem;
  margin-bottom: 2rem;
  color: #3b82f6;
  opacity: 0.7;
}

.placeholder-ai-message p {
  font-size: 1.05rem;
  line-height: 1.6;
  color: #94a3b8;
}

/* Action buttons styling from AnnotateView.vue */
.action-buttons.annotation-actions {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1.5rem;
  padding: 0;
}

.action-button {
  padding: 0.85rem 1.75rem;
  border: none;
  border-radius: 1rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.2s ease;
}

.save-button {
  background: linear-gradient(90deg, #f92672, #ff5e98);
  color: white;
  min-width: 160px;
  box-shadow: 0 4px 10px rgba(249, 38, 114, 0.3);
}

.expert-button {
  background: rgba(15, 23, 42, 0.6);
  color: white;
  min-width: 160px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.save-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(249, 38, 114, 0.4);
}

.expert-button:hover {
  transform: translateY(-3px);
  background: rgba(15, 23, 42, 0.8);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
}

/* New styles for the model status banner */
.model-status-banner {
  background: rgba(255, 152, 0, 0.1);
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.model-status-banner i {
  font-size: 1.2rem;
  color: #ff9800;
}

.model-status-banner span {
  font-size: 0.95rem;
  color: #e5e7eb;
}

.confidence-list-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px;
  padding: 0.75rem;
  overflow-y: auto;
}

.confidence-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* AI detection section styling to match AnnotateView */
.ai-detection-section {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.75rem;
  overflow: hidden;
  border: none;
  margin-bottom: 1rem;
  position: relative;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  z-index: 10;
  transform-origin: top;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.ai-detection-section.expanded {
  transform: translateY(0);
  opacity: 1;
}

.detection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.25rem;
  background: rgba(15, 23, 42, 0.8);
  cursor: pointer;
  border-bottom: none;
}

.detection-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.detection-list {
  padding: 0;
  overflow: auto;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  max-height: 0;
  transition: max-height 0.3s ease, padding 0.3s ease;
  overflow: hidden;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}

.detection-list.expanded {
  max-height: 300px;
  padding: 0.75rem 0;
  overflow-y: auto;
}

.detection-list::-webkit-scrollbar {
  display: none; /* Chrome, Safari and Opera */
}

.detection-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.25rem;
  border-bottom: none;
  transition: background 0.2s ease;
}

.detection-item:hover {
  background: rgba(15, 23, 42, 0.6);
}

.detection-item:last-child {
  border-bottom: none;
}

.detection-color-bar {
  width: 4px;
  height: 22px;
  border-radius: 2px;
  margin-right: 1rem;
}

.detection-name {
  flex: 1;
  font-size: 1rem;
  font-weight: 500;
  color: #e5e7eb;
}

.detection-value {
  font-size: 1.05rem;
  font-weight: 700;
  min-width: 40px;
  text-align: right;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.results-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}

/* Clean up the model status banner */
.model-status-banner {
  background: rgba(255, 152, 0, 0.1);
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.model-status-banner i {
  font-size: 1.2rem;
  color: #ff9800;
}

.model-status-banner span {
  font-size: 0.95rem;
  color: #e5e7eb;
}

/* placeholder message */
.placeholder-ai-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94a3b8;
  text-align: center;
  padding: 2rem;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 1rem;
  backdrop-filter: blur(8px);
}

.analyze-button {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 600;
  font-size: 1.05rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  margin-top: 0.4rem;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.analyze-button:hover:not(:disabled) {
  background: linear-gradient(90deg, #2563eb, #4f94ff);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4);
}

.analyze-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Add these styles to your existing CSS */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 250px;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}

/* Add processing overlay styles */
.ai-processing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(5px);
  border-radius: 1rem;
  z-index: 50;
}

.processing-frame {
  width: 240px;
  height: 240px;
  border: 2px solid #3b82f6;
  border-radius: 0.5rem;
  position: relative;
  margin-bottom: 2rem;
  background: rgba(15, 23, 42, 0.5);
}

.processing-frame::before {
  content: "";
  position: absolute;
  top: -5px;
  left: -5px;
  width: 30px;
  height: 30px;
  border-top: 3px solid #3b82f6;
  border-left: 3px solid #3b82f6;
  border-top-left-radius: 5px;
}

.processing-frame::after {
  content: "";
  position: absolute;
  bottom: -5px;
  right: -5px;
  width: 30px;
  height: 30px;
  border-bottom: 3px solid #3b82f6;
  border-right: 3px solid #3b82f6;
  border-bottom-right-radius: 5px;
}

.processing-scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(
    90deg,
    transparent,
    #3b82f6,
    #60a5fa,
    transparent
  );
  animation: scan-animation 2s ease-in-out infinite;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.7);
}

@keyframes scan-animation {
  0% {
    top: 0;
  }
  50% {
    top: calc(100% - 3px);
  }
  100% {
    top: 0;
  }
}

.processing-status {
  text-align: center;
  color: #e5e7eb;
}

.processing-status h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.processing-status p {
  font-size: 1rem;
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.processing-steps {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1rem;
}

.processing-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.processing-step.active {
  opacity: 1;
}

.processing-step i {
  font-size: 1.5rem;
  color: #3b82f6;
  margin-bottom: 0.5rem;
}

.processing-step span {
  font-size: 0.8rem;
  color: #94a3b8;
}
</style>
