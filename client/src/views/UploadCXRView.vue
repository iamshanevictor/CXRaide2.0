<template>
  <div class="annotate-container">
    <!-- Error state display (reused from AnnotateView) -->
    <div v-if="hasError" class="error-panel">
      <h2>Application Error</h2>
      <p>{{ errorMessage }}</p>
      <div class="error-details" v-if="showErrorDetails">
        <div class="api-info">
          <p><strong>API URL:</strong> {{ apiUrl }}</p>
          <p><strong>Status:</strong> {{ connectionStatus }}</p>
          <p>
            <strong>Auth Token:</strong> {{ hasToken ? "Present" : "Missing" }}
          </p>
        </div>
        <pre v-if="errorDetails" class="error-trace">{{ errorDetails }}</pre>
      </div>
      <div class="error-actions">
        <button
          @click="showErrorDetails = !showErrorDetails"
          class="btn-secondary"
        >
          <span class="icon"><i class="bi bi-clipboard-data"></i></span>
          {{ showErrorDetails ? "Hide" : "Show" }} Details
        </button>
        <button @click="runDiagnostics" class="btn-secondary">
          <span class="icon"><i class="bi bi-activity"></i></span> Diagnostics
        </button>
        <button @click="retryLoading" class="btn-secondary">
          <span class="icon"><i class="bi bi-arrow-clockwise"></i></span> Retry
          Connection
        </button>
        <button @click="backToLogin" class="btn-primary">
          <span class="icon"><i class="bi bi-box-arrow-left"></i></span> Back to
          Login
        </button>
      </div>
    </div>

    <!-- Mock model notification -->
    <div
      v-if="isUsingMockModel"
      class="mock-model-notification"
    >
      <div class="notification-content">
        <i class="bi bi-info-circle"></i>
        <span>Using demo predictions with mock model</span>
      </div>
      <div class="notification-details">
        The predictions shown are simulated examples and do not represent actual
        AI analysis.
      </div>
    </div>

    <!-- Main content -->
    <div v-else class="app-layout">
      <!-- Left Navigation Bar (reused from AnnotateView) -->
      <div class="nav-sidebar">
        <div class="logo-container">
          <img
            src="@/assets/LOGO1.png"
            alt="CXRaide Logo"
            class="sidebar-logo"
          />
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

      <div class="annotate-wrapper">
        <!-- Header -->
        <div class="annotate-header">
          <h1>
            Upload CXR :
            <span class="highlight">Analyze with AI</span>
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

        <!-- Main annotation area -->
        <div class="annotation-container">
          <!-- Main image display area -->
          <div class="image-container">
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

            <div
              class="upload-area"
              :class="{ 'has-image': currentImage }"
              @click="!currentImage && triggerFileUpload()"
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
                  Click to upload or drag & drop<br />Supported formats: JPEG,
                  PNG
                </p>
              </div>
              <div
                v-else
                class="xray-image-container"
              >
                <img :src="currentImage" alt="X-ray image" />
                <button class="remove-image-btn" @click.stop="removeImage">
                  <i class="bi bi-x-circle-fill"></i>
                </button>
              </div>
              <input
                type="file"
                ref="fileInput"
                accept="image/*"
                @change="handleFileUpload"
                class="hidden-file-input"
              />

              <!-- Model Selection Panel -->
              <div class="abnormality-selection-container" @click.stop>
                <div class="abnormality-selector">
                  <div class="selector-label">AI Model Selection:</div>
                  <div class="selector-dropdown-container">
                    <select
                      class="select-dropdown"
                      v-model="selectedModel"
                      @click.stop
                    >
                      <option value="CXR-IT3">SSD300_VGG16-CXR6plus3 v1</option>
                      <option value="CXR-IT2">SSD300_VGG16-CXR9 v2</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action buttons -->
            <div class="action-buttons">
              <button
                class="analyze-with-ai-button"
                :disabled="!currentImage || isAnalyzing"
                @click="analyzeImage"
              >
                <i class="bi bi-search"></i> Analyze with AI
              </button>
            </div>
          </div>

          <!-- Right sidebar with AI annotations -->
          <div class="ai-annotations">
            <!-- Add AI Results header -->
            <div class="results-header">
              <h2>AI Results</h2>
            </div>

            <!-- Mock model banner -->
            <div
              v-if="isUsingMockModel"
              class="model-status-banner"
            >
              <i class="bi bi-info-circle-fill"></i>
              <span
                >Using mock AI predictions (server is using lightweight
                model)</span
              >
            </div>

            <div class="xray-image ai-image">
              <!-- Use the pre-rendered annotated image with bounding boxes -->
              <img
                v-if="annotatedImage"
                :src="annotatedImage"
                alt="AI annotated X-ray"
                class="standardized-image"
              />
              <!-- Fallback to the original image if no annotated image yet -->
              <img
                v-else-if="currentImage && !isAnalyzing"
                :src="currentImage"
                alt="X-ray"
              />

              <!-- Professional analyzing indicator (matching AnnotateView) -->
              <transition name="fade">
                <a-i-model-loader v-if="isAnalyzing && !annotatedImage && !modelError" title="Analyzing Image" message="AI model is processing your chest X-ray..." />
              </transition>

              <!-- Empty state -->
              <div
                v-if="!currentImage && !annotatedImage"
                class="placeholder-ai-message"
              >
                <i class="bi bi-robot"></i>
                <p>AI annotations will appear here</p>
              </div>
            </div>

            <!-- Error state -->
            <transition name="fade">
              <model-error-overlay
                v-if="modelError"
                :title="'Model could not be loaded'"
                :message="modelError"
                :show-retry="true"
                @retry="analyzeImage"
              />
            </transition>

            <!-- AI Detection Results section -->
            <div
              v-if="annotatedImage && aiPredictions.length > 0"
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

            <div v-if="annotatedImage" class="action-buttons annotation-actions">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { logout } from "../utils/api";
import ModelService from "@/services/modelService";
import ModelErrorOverlay from "../components/ModelErrorOverlay.vue";

export default {
  name: "UploadCXRView",
  components: {
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
      isUsingMockModel: false,
      modelError: null,
      processingStep: 1, // Track which processing step is active (1, 2, or 3)
      processingInterval: null, // For interval timer
      // Error handling
      hasError: false,
      errorMessage: "",
      errorDetails: null,
      showErrorDetails: false,
      connectionStatus: "Unknown",
      hasToken: false,
      apiUrl: "",
    };
  },
  created() {
    try {
      // Extract username from token if available
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          this.hasToken = true;
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
        "Nodule/Mass": "#3b82f6", // Blue
        "Pleural Effusion": "#f59e0b", // Orange
        "Cardiomegaly": "#ef4444", // Red
        "Infiltration": "#10b981", // Green
        "Pleural Thickening": "#9c59ff", // Purple
        "Pulmonary Fibrosis": "#ec4899", // Pink
        "Consolidation": "#6366f1", // Indigo
        "Atelectasis": "#8b5cf6", // Violet
        "Pneumothorax": "#64748b", // Slate
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
    },
    // Error handling methods
    runDiagnostics() {
      console.log("[Upload] Running diagnostics");
      alert("Diagnostic feature coming soon!");
    },
    retryLoading() {
      console.log("[Upload] Retrying connection");
      this.hasError = false;
    },
    backToLogin() {
      this.$router.push("/login");
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
/* Base Layout Styles */
.annotate-container {
  min-height: 100vh;
  width: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.app-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

/* Navigation sidebar styles */
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

/* Main workspace area */
.annotate-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 240px;
  width: calc(100% - 240px);
}

/* Header styles */
.annotate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.annotate-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f3f4f6;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.highlight {
  color: #3b82f6;
  font-weight: 600;
  font-size: 0.9em;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Header buttons */
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
  background: rgba(13, 31, 65, 0.9);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.icon-button:hover {
  background: rgba(23, 41, 75, 0.9);
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.4);
  transform: translateY(-2px);
}

.icon-button .icon {
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-dropdown {
  position: relative;
}

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
  font-size: 1rem;
  opacity: 0.8;
}

/* Annotation container */
.annotation-container {
  display: flex;
  height: calc(100vh - 86px);
  padding: 1rem;
  gap: 1rem;
  overflow: hidden;
}

/* Image container styles */
.image-container {
  flex: 1;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.15);
  max-width: 60%;
}

.ai-annotations {
  flex: 1;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.15);
}

.results-header {
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.8);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.results-header h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #3b82f6;
  margin: 0;
}

.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.8);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  color: #e5e7eb;
  font-size: 0.875rem;
}

.upload-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.upload-btn:hover {
  background: #2563eb;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

.upload-btn:disabled {
  background: #6b7280;
  cursor: not-allowed;
}

.upload-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.3);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  border: 2px dashed rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  background: rgba(15, 23, 42, 0.5);
  transition: all 0.2s ease;
  width: 80%;
  max-width: 400px;
  cursor: pointer;
}

.upload-placeholder.dragging {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
}

.upload-placeholder i {
  font-size: 3rem;
  color: #3b82f6;
}

.upload-placeholder p {
  color: #e5e7eb;
  text-align: center;
  font-size: 0.875rem;
}

.hidden-file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.xray-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.xray-image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.remove-image-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(15, 23, 42, 0.7);
  border: none;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #f3f4f6;
  font-size: 1.2rem;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
  z-index: 5;
}

.remove-image-btn:hover {
  background: #ef4444;
  transform: scale(1.1);
}

/* AI image styles */
.xray-image.ai-image {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.3);
}

.xray-image.ai-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.standardized-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* Model status banner */
.model-status-banner {
  padding: 0.75rem 1rem;
  background: rgba(249, 115, 22, 0.1);
  border-bottom: 1px solid rgba(249, 115, 22, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #f97316;
  font-size: 0.875rem;
}

.model-status-banner i {
  font-size: 1rem;
}

/* AI processing overlay */
.ai-processing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 5;
}

.processing-frame {
  width: 80%;
  max-width: 500px;
  height: 300px;
  border: 2px solid rgba(59, 130, 246, 0.5);
  border-radius: 0.5rem;
  position: relative;
  overflow: hidden;
  margin-bottom: 2rem;
}

.processing-scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.8);
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% {
    top: 0;
  }
  100% {
    top: 300px;
  }
}

.processing-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.processing-status h3 {
  color: #3b82f6;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.processing-status p {
  color: #e5e7eb;
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

.processing-steps {
  display: flex;
  gap: 1.5rem;
}

.processing-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.processing-step i {
  font-size: 1.5rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.processing-step span {
  font-size: 0.75rem;
  color: #94a3b8;
}

.processing-step.active {
  opacity: 1;
}

.processing-step.active i {
  color: #3b82f6;
}

.processing-step.active span {
  color: #e5e7eb;
}

/* Placeholder message */
.placeholder-ai-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  gap: 1rem;
}

.placeholder-ai-message i {
  font-size: 3rem;
  color: #3b82f6;
  opacity: 0.5;
}

.placeholder-ai-message p {
  color: #94a3b8;
  font-size: 1rem;
}

/* Abnormality selection */
.abnormality-selection-container {
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.9);
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.abnormality-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 250px;
}

.selector-label {
  font-size: 0.875rem;
  color: #e5e7eb;
  white-space: nowrap;
}

.selector-dropdown-container {
  flex: 1;
}

.select-dropdown {
  width: 100%;
  padding: 0.5rem;
  border-radius: 0.375rem;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #e5e7eb;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
}

.select-dropdown:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

/* AI Detection Results */
.ai-detection-section {
  background: rgba(15, 23, 42, 0.8);
  border-top: 1px solid rgba(59, 130, 246, 0.2);
}

.detection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
}

.detection-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.toggle-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.detection-list {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, padding 0.3s ease;
}

.detection-list.expanded {
  max-height: 300px;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.detection-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
}

.detection-color-bar {
  width: 3px;
  height: 1.5rem;
  border-radius: 1px;
}

.detection-name {
  font-size: 0.875rem;
  color: #e5e7eb;
  flex: 1;
}

.detection-value {
  font-size: 0.875rem;
  font-weight: 600;
}

/* Actions buttons */
.action-buttons {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  background: rgba(15, 23, 42, 0.9);
}

.analyze-with-ai-button {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
  flex: 1;
  justify-content: center;
}

.analyze-with-ai-button:hover {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}

.analyze-with-ai-button:disabled {
  background: linear-gradient(135deg, #64748b, #94a3b8);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.action-button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
  flex: 1;
}

.save-button {
  background: #10b981;
  color: white;
  border: none;
}

.save-button:hover {
  background: #059669;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

.expert-button {
  background: transparent;
  color: #e5e7eb;
  border: 1px solid #64748b;
}

.expert-button:hover {
  background: rgba(100, 116, 139, 0.1);
  border-color: #94a3b8;
}

/* Mock model notification */
.mock-model-notification {
  background: rgba(234, 88, 12, 0.05);
  border: 1px solid rgba(234, 88, 12, 0.2);
  margin: 1rem;
  border-radius: 0.5rem;
  overflow: hidden;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #f97316;
  font-weight: 600;
}

.notification-content i {
  font-size: 1.2rem;
}

.notification-details {
  padding: 0.75rem 1rem;
  border-top: 1px solid rgba(234, 88, 12, 0.2);
  font-size: 0.875rem;
  color: #f97316;
  opacity: 0.8;
}

/* Error panel */
.error-panel {
  padding: 2rem;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.5rem;
  margin: 2rem auto;
  max-width: 800px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.error-panel h2 {
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-panel p {
  color: #e5e7eb;
  margin-bottom: 1.5rem;
}

.error-details {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.api-info p {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.error-trace {
  font-family: monospace;
  font-size: 0.75rem;
  color: #ef4444;
  white-space: pre-wrap;
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.375rem;
  max-height: 300px;
  overflow-y: auto;
}

.error-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-secondary,
.btn-primary {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary {
  background: rgba(100, 116, 139, 0.1);
  color: #e5e7eb;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.btn-secondary:hover {
  background: rgba(100, 116, 139, 0.2);
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #2563eb;
}

/* Fade transition for loading state */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Make the UI mobile responsive */
@media (max-width: 1200px) {
  .annotation-container {
    flex-direction: column;
    height: auto;
  }

  .image-container,
  .ai-annotations {
    max-width: 100%;
    height: 50vh;
  }
}

@media (max-width: 768px) {
  .nav-sidebar {
    width: 60px;
  }

  .nav-label {
    display: none;
  }

  .nav-icon {
    margin-right: 0;
  }

  .annotate-wrapper {
    margin-left: 60px;
    width: calc(100% - 60px);
  }

  .nav-item {
    justify-content: center;
  }

  .sidebar-logo {
    width: 40px;
  }

  .annotate-header h1 {
    font-size: 1.2rem;
  }

  .highlight {
    display: none;
  }
}

@media (max-width: 576px) {
  .abnormality-selection-container {
    flex-direction: column;
  }

  .abnormality-selector {
    min-width: 100%;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
