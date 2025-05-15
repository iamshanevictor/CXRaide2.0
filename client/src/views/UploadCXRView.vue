<template>
  <page-layout
    :hasError="hasError"
    :errorMessage="errorMessage"
    :errorDetails="errorDetails"
    v-model:showErrorDetails="showErrorDetails"
    :connectionStatus="connectionStatus"
    :hasToken="hasToken"
    :apiUrl="apiUrl"
    :username="username"
    :isLoading="isLoading"
    :showMockWarning="isUsingMockModel"
    currentRoute="upload-cxr"
    @logout="logout"
    @retry="retryLoading"
    @run-diagnostics="runDiagnostics"
    @back-to-login="backToLogin"
  >
    <template #header-title>
      Upload CXR : <span class="highlight">Analyze with AI</span>
    </template>

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
        </div>

        <!-- Abnormality Selection Panel styled to match AnnotateView -->
        <div class="abnormality-type-container" @click.stop>
          <div class="abnormality-type-row">
            <div class="abnormality-label">AI Model Selection:</div>
            <div class="select-wrapper">
              <select
                class="abnormality-select custom-select"
                v-model="selectedModel"
                @click.stop
              >
                <option value="SSD300_VGG16-CXR6plus3 v1">SSD300_VGG16-CXR6plus3 v1</option>
                <option value="FRCNN_ResNet50-CXRmulti v2">FRCNN_ResNet50-CXRmulti v2</option>
              </select>
            </div>
          </div>
          <div class="abnormality-type-row">
            <div class="abnormality-label">Display Type:</div>
            <div class="select-wrapper">
              <select
                class="display-type-select custom-select"
                v-model="displayType"
              >
                <option value="Show Annotations">Show Annotations</option>
                <option value="Original Only">Original Only</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Results Panel -->
      <div class="results-container">
        <div class="results-header">
          <h2>AI Results</h2>
        </div>

        <div
          v-if="!hasResults && !isAnalyzing"
          class="results-placeholder"
        >
          <div class="ai-icon">
            <i class="bi bi-robot"></i>
          </div>
          <p>AI annotations will appear here</p>
        </div>

        <div v-if="isAnalyzing" class="analyzing-indicator">
          <div class="analyzing-spinner">
            <i class="bi bi-arrow-repeat"></i>
          </div>
          <p>Analyzing image...</p>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: analyzeProgress + '%' }"
            ></div>
          </div>
        </div>

        <!-- Results content when we have analysis -->
        <div v-if="hasResults && !isAnalyzing" class="ai-results-content">
          <div class="abnormality-list">
            <div
              v-for="(item, index) in predictionResults"
              :key="index"
              class="abnormality-item"
            >
              <div class="abnormality-header">
                <div class="abnormality-name">{{ item.label }}</div>
                <div class="abnormality-score">
                  {{ Math.round(item.score * 100) }}%
                </div>
              </div>
              <div class="abnormality-location">
                <span class="location-label">Location:</span>
                <span class="location-value">{{ formatBoundingBox(item.bbox) }}</span>
              </div>
            </div>
          </div>
          
          <div class="actions-container">
            <button 
              class="action-button download-btn"
              @click="downloadPdfReport"
            >
              <i class="bi bi-file-pdf"></i> Download PDF Report
            </button>
            
            <button 
              class="action-button new-analysis-btn"
              @click="startNewAnalysis"
            >
              <i class="bi bi-arrow-repeat"></i> New Analysis
            </button>
          </div>
        </div>
      </div>
    </div>
  </page-layout>
</template>

<script>
import { apiUrl, logout } from "../utils/api";
import { runNetworkTest } from "../utils/network-test";
import ModelService from "@/services/modelService";
import PageLayout from "@/components/PageLayout.vue";

export default {
  name: "UploadCXRView",
  components: {
    PageLayout
  },
  data() {
    return {
      apiUrl: apiUrl,
      username: "User",
      isLoading: false,
      isAnalyzing: false,
      analyzeProgress: 0,
      connectionStatus: "Connected",
      hasError: false,
      errorMessage: "",
      errorDetails: null,
      showErrorDetails: false,
      hasToken: true,
      // Image upload related
      imageFile: null,
      currentImage: null,
      isDragging: false,
      isUsingMockModel: false,
      // Analysis options
      selectedModel: "SSD300_VGG16-CXR6plus3 v1",
      displayType: "Show Annotations",
      // Results
      hasResults: false,
      predictionResults: []
    };
  },
  created() {
    this.$emit("loading-start");
    this.loadUserData();
    this.checkModelStatus();
    this.$emit("loading-end");
  },
  mounted() {
    document.addEventListener("dragover", this.preventDefaults);
    document.addEventListener("drop", this.preventDefaults);
  },
  beforeUnmount() {
    document.removeEventListener("dragover", this.preventDefaults);
    document.removeEventListener("drop", this.preventDefaults);
  },
  methods: {
    loadUserData() {
      // Get user info from token
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          const payload = token.split(".")[1];
          const decoded = JSON.parse(atob(payload));
          this.username = decoded.username || "User";
          
          // Check for offline mode token
          if (decoded.offline_mode === true) {
            console.log("[Upload] Offline mode detected");
            this.isUsingMockModel = true;
          }
          
          this.hasToken = true;
        } catch (e) {
          console.error("[Upload] Error parsing token:", e);
          this.username = "User";
        }
      }
    },
    async checkModelStatus() {
      try {
        const modelStatus = await ModelService.checkModelStatus();
        if (modelStatus && modelStatus.using_mock_models) {
          this.isUsingMockModel = true;
        }
      } catch (error) {
        console.error("[Upload] Error checking model status:", error);
        // Default to mock model if we can't check status
        this.isUsingMockModel = true;
      }
    },
    triggerFileUpload() {
      if (this.isAnalyzing) return;
      this.$refs.fileInput.click();
    },
    preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    },
    handleFileDrop(e) {
      this.isDragging = false;
      
      if (this.isAnalyzing) return;
      
      const dt = e.dataTransfer;
      if (dt.files && dt.files.length > 0) {
        this.processUploadedFile(dt.files[0]);
      }
    },
    handleFileUpload(e) {
      if (e.target.files && e.target.files.length > 0) {
        this.processUploadedFile(e.target.files[0]);
      }
    },
    processUploadedFile(file) {
      // Check if file exists
      if (!file) {
        this.handleError(new Error("No file selected"), "Please select a file to upload");
        return;
      }
      
      // Check file type
      if (!file.type.match('image.*')) {
        this.handleError(new Error("Invalid file type"), "Please upload an image file (JPEG, PNG)");
        return;
      }
      
      // Check file size (max 10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        this.handleError(new Error("File too large"), "Please upload an image smaller than 10MB");
        return;
      }
      
      console.log("[UploadCXR] Processing file:", file.name, file.type, file.size);
      
      // Store file reference - create a new File object to ensure it's a proper File instance
      try {
        this.imageFile = new File([file], file.name, { 
          type: file.type,
          lastModified: file.lastModified
        });
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
          this.currentImage = e.target.result;
          // Auto-start analysis when image is loaded
          this.analyzeImage();
        };
        reader.onerror = (e) => {
          console.error("[UploadCXR] Error reading file:", e);
          this.handleError(new Error("Error reading file"), "Could not read the selected image file");
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error("[UploadCXR] Error processing file:", error);
        this.handleError(error, "Error processing the selected file");
      }
    },
    removeImage() {
      this.imageFile = null;
      this.currentImage = null;
      this.hasResults = false;
      this.predictionResults = [];
    },
    async analyzeImage() {
      if (!this.imageFile || this.isAnalyzing) return;
      
      // Validate the image file
      if (!(this.imageFile instanceof File)) {
        this.handleError(new Error("Invalid image file"), "The selected file is not a valid image");
        return;
      }
      
      this.isAnalyzing = true;
      this.analyzeProgress = 0;
      this.hasResults = false;
      this.predictionResults = [];
      
      // Simulate progress (this would normally come from the real API)
      const progressInterval = setInterval(() => {
        if (this.analyzeProgress < 90) {
          this.analyzeProgress += Math.random() * 10;
        }
      }, 300);
      
      try {
        console.log("[UploadCXR] Starting image analysis with file:", this.imageFile.name);
        
        let results;
        let usedMockResults = false;
        
        // Always try the real prediction first unless explicitly using mock model
        if (!this.isUsingMockModel) {
          try {
            // Try to use real model service
            console.log("[UploadCXR] Attempting to use real model service");
            results = await ModelService.predict(this.imageFile, {
              model_type: this.selectedModel
            });
            
            console.log("[UploadCXR] Received prediction results:", results);
            
            // Transform the results to match the expected format
            if (results && results.predictions) {
              results = results.predictions.map(pred => ({
                label: pred.class || 'Unknown',
                score: pred.score || 0,
                bbox: pred.box || [0, 0, 0, 0]
              }));
            } else {
              // If we got an empty response, fall back to mock results
              console.log("[UploadCXR] Empty results from server, falling back to mock results");
              results = this.generateMockResults();
              usedMockResults = true;
            }
          } catch (predictionError) {
            // If the real prediction fails, fall back to mock results
            console.warn("[UploadCXR] Real prediction failed, using mock results instead:", predictionError);
            await new Promise(resolve => setTimeout(resolve, 1000)); // Short delay
            results = this.generateMockResults();
            usedMockResults = true;
          }
        } else {
          // Explicitly using mock model
          console.log("[UploadCXR] Using mock model as configured");
          await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate delay
          results = this.generateMockResults();
          usedMockResults = true;
        }
        
        // Process results
        this.analyzeProgress = 100;
        setTimeout(() => {
          this.predictionResults = results;
          this.hasResults = true;
          this.isAnalyzing = false;
          clearInterval(progressInterval);
          
          // Show a notification if we fell back to mock results
          if (usedMockResults && !this.isUsingMockModel) {
            this.$emit('show-notification', {
              type: 'warning',
              message: 'Server prediction failed. Using simulated results instead.',
              duration: 5000
            });
          }
        }, 500);
      } catch (error) {
        console.error("[Upload] Analysis error:", error);
        this.handleError(error, "Error analyzing image");
        clearInterval(progressInterval);
        this.isAnalyzing = false;
      }
    },
    generateMockResults() {
      // Generate realistic-looking mock results for demo purposes
      console.log("[UploadCXR] Generating mock results");
      
      // Define possible findings with realistic positions and confidence ranges
      const possibleFindings = [
        {
          label: "Cardiomegaly",
          scoreRange: [0.75, 0.95],
          bboxRange: [[70, 110, 190, 180], [80, 120, 210, 190]]
        },
        {
          label: "Pleural Effusion",
          scoreRange: [0.70, 0.90],
          bboxRange: [[170, 230, 120, 90], [180, 240, 140, 100]]
        },
        {
          label: "Nodule/Mass",
          scoreRange: [0.55, 0.75],
          bboxRange: [[240, 160, 40, 35], [260, 180, 50, 45]]
        },
        {
          label: "Infiltration",
          scoreRange: [0.60, 0.85],
          bboxRange: [[120, 150, 100, 80], [140, 160, 110, 90]]
        },
        {
          label: "Atelectasis",
          scoreRange: [0.65, 0.80],
          bboxRange: [[90, 200, 80, 70], [100, 210, 90, 80]]
        },
        {
          label: "Pneumothorax",
          scoreRange: [0.70, 0.85],
          bboxRange: [[50, 130, 60, 150], [60, 140, 70, 160]]
        }
      ];
      
      // Randomly determine how many findings to show (1-3)
      const numFindings = Math.floor(Math.random() * 3) + 1;
      
      // Randomly select findings without duplicates
      const selectedIndices = [];
      while (selectedIndices.length < numFindings && selectedIndices.length < possibleFindings.length) {
        const randomIndex = Math.floor(Math.random() * possibleFindings.length);
        if (!selectedIndices.includes(randomIndex)) {
          selectedIndices.push(randomIndex);
        }
      }
      
      // Generate the results
      const results = selectedIndices.map(index => {
        const finding = possibleFindings[index];
        
        // Generate random score within the defined range
        const scoreRange = finding.scoreRange;
        const score = scoreRange[0] + Math.random() * (scoreRange[1] - scoreRange[0]);
        
        // Select one of the possible bounding box positions
        const bboxIndex = Math.floor(Math.random() * finding.bboxRange.length);
        const bbox = finding.bboxRange[bboxIndex];
        
        // Add slight randomness to bbox coordinates
        const randomizedBbox = bbox.map(coord => {
          const variation = coord * 0.05; // 5% variation
          return Math.round(coord + (Math.random() * variation * 2 - variation));
        });
        
        return {
          label: finding.label,
          score: score,
          bbox: randomizedBbox
        };
      });
      
      console.log("[UploadCXR] Generated mock results:", results);
      return results;
    },
    formatBoundingBox(bbox) {
      if (!bbox || !Array.isArray(bbox) || bbox.length !== 4) {
        return "Unknown";
      }
      
      const [x, y, width, height] = bbox;
      return `(${x}, ${y}), ${width}×${height}`;
    },
    downloadPdfReport() {
      alert("PDF Report download functionality will be implemented in the production version.");
    },
    startNewAnalysis() {
      this.removeImage();
      this.triggerFileUpload();
    },
    async logout() {
      try {
        this.isLoading = true;
        await logout();
        this.backToLogin();
      } catch (error) {
        console.error("[Upload] Logout error:", error);
        // Even if logout API fails, we should still redirect to login
        this.backToLogin();
      } finally {
        this.isLoading = false;
      }
    },
    handleError(error, customMessage = null) {
      console.error("[Upload] Error:", error);
      
      // Collect detailed error info for diagnostics
      this.errorDetails = JSON.stringify(
        {
          message: error.message,
          code: error.code,
          status: error.response?.status,
          statusText: error.response?.statusText,
          url: error.config?.url,
          time: new Date().toISOString(),
        },
        null,
        2
      );
      
      // Set error state and message
      this.hasError = true;
      
      if (customMessage) {
        this.errorMessage = customMessage;
      } else if (error.code === "ERR_NETWORK") {
        this.errorMessage = "Network connection error. The server is unreachable.";
      } else {
        this.errorMessage = error.message || "An unexpected error occurred.";
      }
    },
    runDiagnostics() {
      // Run network diagnostics and log results
      runNetworkTest();
      console.log("[Upload] Network diagnostics completed");
    },
    retryLoading() {
      this.hasError = false;
      this.checkModelStatus();
    },
    backToLogin() {
      // Always clear token before going back to login
      try {
        localStorage.removeItem("authToken");
      } catch (e) {
        console.error("[Upload] Error removing token:", e);
      }
      this.$router.push("/login");
    }
  }
};
</script>

<style scoped>
/* Import Bootstrap Icons */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");

.highlight {
  color: #e5e7eb;
  font-weight: 400;
}

/* Main annotation container */
.annotation-container {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 1.5rem;
  width: 100%;
  height: calc(100vh - 150px);
  min-height: 600px;
}

/* Image container styles */
.image-container {
  background: rgba(13, 18, 30, 0.95);
  border-radius: 0.5rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.9);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  font-size: 0.85rem;
  color: #94a3b8;
}

.upload-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.4rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
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
  padding: 1rem;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  background: #0f172a;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  border: 2px dashed rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.upload-placeholder:hover,
.upload-placeholder.dragging {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.05);
}

.upload-placeholder i {
  font-size: 3rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.upload-placeholder p {
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
  line-height: 1.6;
}

.xray-image-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.xray-image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.remove-image-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(15, 23, 42, 0.8);
  border: none;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #f87171;
}

.remove-image-btn:hover {
  background: rgba(15, 23, 42, 0.95);
  color: #ef4444;
}

.hidden-file-input {
  display: none;
}

/* Abnormality type container */
.abnormality-type-container {
  margin-top: auto;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.95);
  border-top: 1px solid rgba(59, 130, 246, 0.2);
}

.abnormality-type-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.abnormality-type-row:last-child {
  margin-bottom: 0;
}

.abnormality-label {
  font-size: 0.9rem;
  color: #e5e7eb;
  font-weight: 500;
}

.select-wrapper {
  flex: 1;
  max-width: 300px;
  margin-left: 1rem;
}

.custom-select {
  width: 100%;
  background: rgba(15, 23, 42, 0.8);
  color: #e5e7eb;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-size: 0.9rem;
  appearance: none;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 4L6 8L10 4" stroke="%233b82f6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>');
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  cursor: pointer;
}

.custom-select:focus {
  outline: none;
  border-color: #3b82f6;
}

/* Results container */
.results-container {
  background: rgba(13, 18, 30, 0.95);
  border-radius: 0.5rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.results-header {
  padding: 1rem 1.5rem;
  background: rgba(15, 23, 42, 0.9);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.results-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #f8fafc;
}

.results-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.ai-icon {
  font-size: 3.5rem;
  color: #475569;
  margin-bottom: 1rem;
}

.results-placeholder p {
  color: #94a3b8;
  text-align: center;
  font-size: 1rem;
}

/* Analyzing indicator */
.analyzing-indicator {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.analyzing-spinner {
  font-size: 3rem;
  color: #3b82f6;
  margin-bottom: 1rem;
  animation: spin 1.5s infinite linear;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.analyzing-indicator p {
  color: #e5e7eb;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.progress-bar {
  width: 80%;
  height: 0.5rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 1rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 1rem;
  transition: width 0.3s ease;
}

/* AI Results content */
.ai-results-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  overflow-y: auto;
}

.abnormality-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.abnormality-item {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  border-left: 3px solid #3b82f6;
}

.abnormality-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.abnormality-name {
  font-size: 1rem;
  font-weight: 600;
  color: #f8fafc;
}

.abnormality-score {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.abnormality-location {
  font-size: 0.85rem;
  color: #94a3b8;
}

.location-label {
  margin-right: 0.5rem;
  font-weight: 500;
}

.location-value {
  font-family: monospace;
}

/* Action buttons */
.actions-container {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-size: 0.95rem;
}

.download-btn {
  background: #3b82f6;
  color: white;
}

.download-btn:hover {
  background: #2563eb;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

.new-analysis-btn {
  background: rgba(15, 23, 42, 0.5);
  color: #e5e7eb;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.new-analysis-btn:hover {
  background: rgba(15, 23, 42, 0.7);
  border-color: rgba(59, 130, 246, 0.5);
}

/* Make layout responsive */
@media (max-width: 1200px) {
  .annotation-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .image-container {
    min-height: 300px;
  }
  
  .results-container {
    min-height: 300px;
  }
}
</style>
