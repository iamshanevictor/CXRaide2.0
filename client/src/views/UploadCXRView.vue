<template>
  <div class="app-layout">
    <!-- Sidebar Navigation -->
    <div class="nav-sidebar">
      <div class="logo-container">
        <img src="@/assets/LOGO1.png" alt="CXRaide Logo" class="sidebar-logo" />
      </div>
      <div class="nav-items">
        <div class="nav-item" @click="$router.push('/home')">
          <div class="nav-icon"><i class="bi bi-speedometer2"></i></div>
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
          <div class="panel-header">
            <h2>Upload Chest X-Ray</h2>
          </div>

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
                  <option value="CXR-SSDVG9">CXR-SSDVG9 (IT2 Model)</option>
                  <option value="CXR-SSDVG6plus3">
                    CXR-SSDVG6plus3 (IT2+IT3 Combined Model)
                  </option>
                </select>
                <div class="select-arrow">
                  <i class="bi bi-chevron-down"></i>
                </div>
              </div>
              <p class="model-description">
                {{
                  selectedModel === "CXR-SSDVG9"
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
            <button
              class="collapse-button"
              @click="isResultsPanelExpanded = !isResultsPanelExpanded"
            >
              <i class="bi bi-arrows-angle-expand"></i>
            </button>
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

              <!-- Loading state -->
              <transition name="fade">
                <a-i-model-loader v-if="isAnalyzing" />
              </transition>
            </div>

            <!-- AI Detection Results dropdown -->
            <div class="ai-detection-section">
              <div
                class="detection-header"
                @click="isResultsCollapsed = !isResultsCollapsed"
              >
                <h3>AI Detection Results:</h3>
                <button class="toggle-btn">
                  <i
                    :class="
                      isResultsCollapsed
                        ? 'bi bi-chevron-down'
                        : 'bi bi-chevron-up'
                    "
                  ></i>
                </button>
              </div>

              <div v-if="!isResultsCollapsed" class="detection-list">
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
            <a-i-model-loader v-if="isAnalyzing && !annotatedImage" />
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ModelService from "../services/modelService";
import AIModelLoader from "../components/AIModelLoader.vue";
import { logout } from "../utils/api";

export default {
  name: "UploadCXRView",
  components: {
    AIModelLoader,
  },
  data() {
    return {
      currentImage: null,
      selectedModel: "CXR-SSDVG6plus3", // Default to the combined model
      isAnalyzing: false,
      annotatedImage: null,
      aiPredictions: [],
      imageFile: null,
      modelType: null,
      isResultsCollapsed: false,
      isDragging: false,
      username: "User",
      showUserMenu: false,
      isResultsPanelExpanded: false,
      isUsingMockModel: false,
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

        // Set model type based on selection
        if (this.selectedModel === "CXR-SSDVG9") {
          this.modelType = "it2";
        } else {
          this.modelType = "combined";
        }

        // Create a FormData object if we need to specify model
        const formData = new FormData();
        formData.append("model_type", this.modelType);

        // Get predictions from the selected model
        const result = await ModelService.predict(this.imageFile, formData);

        // Check if using mock model
        if (result.using_mock_models) {
          this.isUsingMockModel = true;
        }

        // Update UI with results
        this.annotatedImage = result.annotatedImage;

        // Process predictions
        if (result.predictions && result.predictions.length > 0) {
          this.aiPredictions = result.predictions.map((pred) => ({
            ...pred,
            class: pred.class || "Unknown",
            score: pred.score || 0,
          }));
        } else {
          this.aiPredictions = [];
        }
      } catch (error) {
        console.error("Error analyzing image:", error);
        alert("An error occurred during image analysis. Please try again.");
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
  },
  mounted() {
    document.addEventListener("click", this.closeUserMenu);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.closeUserMenu);
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

.icon-button {
  background: rgba(15, 23, 42, 0.5);
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

.icon-button:hover {
  background: rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.icon-button .icon {
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e5e7eb;
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
  color: white;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
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
  height: calc(100vh - 150px);
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
}

.results-panel {
  flex: 1.05;
  position: relative;
  padding-bottom: 1rem;
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
  border-radius: 0.5rem 0.5rem 0 0;
  padding: 0.75rem 1rem;
  color: #e5e7eb;
  font-size: 0.95rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  margin-bottom: 0;
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
  border-radius: 0.75rem;
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
  height: 370px; /* Increased height to fill more space */
  margin-bottom: 1.5rem;
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
  margin-top: 0;
  padding: 1.25rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.75rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.model-selection-compact.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.model-selection-compact h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 0.75rem;
}

.model-selection-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.model-description {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.4;
  margin: 0;
}

.analyze-button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.analyze-button:hover:not(:disabled) {
  background: linear-gradient(90deg, #2563eb, #4f94ff);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.analyze-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.analyze-button i {
  font-size: 1.1rem;
}

.results-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94a3b8;
  text-align: center;
  padding: 2rem;
}

.results-placeholder i {
  font-size: 4rem;
  margin-bottom: 2rem;
  color: #3b82f6;
  opacity: 0.7;
}

.results-placeholder p {
  font-size: 1.1rem;
  color: #94a3b8;
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

.result-image-container {
  width: 100%;
  background: #000;
  margin-bottom: 1.5rem;
  border-radius: 0.5rem;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(59, 130, 246, 0.3);
  height: 500px; /* Fixed height */
  position: relative;
}

.result-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.action-button {
  flex: 1;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  color: #e5e7eb;
  font-size: 0.95rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.download-btn {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.4);
}

.download-btn:hover {
  background: rgba(16, 185, 129, 0.25);
}

.new-analysis-btn {
  background: rgba(59, 130, 246, 0.15);
}

.findings-section {
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid rgba(59, 130, 246, 0.2);
  margin-bottom: 1.5rem;
  position: relative;
}

.findings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  background: rgba(15, 23, 42, 0.9);
}

.findings-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.findings-container {
  background: rgba(15, 23, 42, 0.9);
  transition: all 0.3s ease;
  max-height: 500px;
  overflow-y: auto;
  padding: 1rem;
}

.findings-container.collapsed {
  max-height: 0;
  padding: 0;
  overflow: hidden;
}

/* New styles for the findings list view */
.findings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.finding-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.finding-color-bar {
  width: 4px;
  height: 24px;
  border-radius: 2px;
}

.finding-name {
  flex: 1;
  font-size: 1rem;
  font-weight: 500;
  color: #e5e7eb;
}

.finding-value {
  font-size: 1.1rem;
  font-weight: 700;
  min-width: 50px;
  text-align: right;
}

.confidence-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.confidence-bar {
  flex: 1;
  height: 8px;
  background: rgba(15, 23, 42, 0.7);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.confidence-fill {
  height: 100%;
  transition: width 0.5s ease-out;
  border-radius: 4px;
}

.confidence-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: #f3f4f6;
  min-width: 3.5rem;
  text-align: right;
}

.finding-column {
  width: 70%;
}

.confidence-column {
  width: 30%;
}

/* Media queries for responsiveness */
@media (max-width: 1400px) {
  .content-area {
    gap: 1.5rem;
  }

  .upload-panel,
  .results-panel {
    padding: 1.25rem;
  }
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Style for the expanded image */
.result-image-container.expanded {
  position: absolute;
  top: 0;
  left: -20px;
  right: -20px;
  height: 90vh;
  width: calc(100% + 40px);
  max-height: none;
  z-index: 100;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 0;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
}

.result-image-container.expanded .result-image {
  max-height: 85vh;
}

.upload-panel {
  flex: 0.95;
  background: #0f172a;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: auto;
  height: calc(100vh - 150px); /* Match results panel height */
  min-height: 700px;
}

.collapse-button {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
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

.collapse-button:hover {
  background: rgba(59, 130, 246, 0.25);
}

/* Update styling for more compact and professional upload panel */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.panel-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 0;
}

.upload-area {
  border: 2px dashed rgba(59, 130, 246, 0.4);
  border-radius: 0.75rem;
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
  height: 370px; /* Increased height to fill more space */
  margin-bottom: 1.5rem;
  flex-shrink: 0;
}

/* More compact model selection area */
.model-selection-compact {
  margin-top: 0;
  padding: 1.25rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.75rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.model-selection-compact.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.model-selection-compact h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 0.75rem;
}

.model-selection-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.model-description {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.4;
  margin: 0;
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
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden; /* Prevent scrollbars */
}

.xray-image {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1rem;
  border: 1px solid rgba(59, 130, 246, 0.3);
  height: 500px; /* Default taller height when collapsed */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: height 0.3s ease;
}

.xray-image.collapsed-view {
  height: 350px; /* Shorter height when detection panel is expanded */
}

.ai-image {
  width: 100%;
  height: 100%;
}

.standardized-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.ai-confidence-summary {
  flex: 1; /* Allow the confidence summary to expand to fill space */
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
  min-height: 60px; /* Keep header visible when collapsed */
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
  max-height: unset; /* Remove max height restriction */
  flex: 1; /* Allow it to expand */
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
  padding: 0.5rem 0.75rem; /* Reduced padding */
  border-left: 4px solid transparent;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 4px;
}

.confidence-item:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateX(2px);
}

.toggle-btn {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
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
  background: rgba(59, 130, 246, 0.25);
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
  height: 100%; /* Fill entire container */
  min-height: 400px;
  color: #94a3b8;
  text-align: center;
  padding: 2rem;
}

.placeholder-ai-message i {
  font-size: 4rem;
  margin-bottom: 2rem;
  color: #3b82f6;
  opacity: 0.7;
}

.placeholder-ai-message p {
  font-size: 1.1rem;
  color: #94a3b8;
}

/* Action buttons styling from AnnotateView.vue */
.action-buttons.annotation-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: auto;
  padding-top: 1rem;
}

.action-button {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.save-button,
.expert-button {
  background: linear-gradient(90deg, #f92672, #ff5e98);
  color: white;
  min-width: 160px;
}

.action-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(249, 38, 114, 0.4);
}

/* New styles for the model status banner */
.model-status-banner {
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.model-status-banner i {
  font-size: 1.2rem;
  color: #3b82f6;
}

.model-status-banner span {
  font-size: 0.95rem;
  color: #e5e7eb;
}

.confidence-list-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px; /* Ensure it takes at least this much space */
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
  background: rgba(15, 23, 42, 0.9);
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid rgba(59, 130, 246, 0.2);
  margin-bottom: 1rem;
  flex: 1; /* Take remaining space but don't overflow */
  display: flex;
  flex-direction: column;
}

.detection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  cursor: pointer;
}

.detection-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.detection-list {
  padding: 0;
  overflow-y: auto; /* Allow scrolling for many items */
  flex: 1; /* Take available space */
}

.detection-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem; /* Smaller padding */
  border-bottom: 1px solid rgba(30, 41, 59, 0.5);
}

.detection-item:last-child {
  border-bottom: none;
}

.detection-color-bar {
  width: 4px;
  height: 18px;
  border-radius: 2px;
  margin-right: 0.75rem;
}

.detection-name {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 500;
  color: #e5e7eb;
}

.detection-value {
  font-size: 1rem;
  font-weight: 700;
  min-width: 40px;
  text-align: right;
}

.xray-image {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1rem;
  border: 1px solid rgba(59, 130, 246, 0.3);
  height: 500px; /* Default taller height when collapsed */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: height 0.3s ease;
}

.xray-image.collapsed-view {
  height: 350px; /* Shorter height when detection panel is expanded */
}

.results-panel {
  flex: 1.05;
  background: #0f172a;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden; /* Changed from auto to hidden */
  position: relative;
}

.ai-annotations {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden; /* Prevent scrollbars */
}
</style>
