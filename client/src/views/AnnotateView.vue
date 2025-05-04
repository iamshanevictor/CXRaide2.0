<template>
  <div class="annotate-container">
    <!-- Error state display (reused from HomeView) -->
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
      v-if="modelInfo && modelInfo.using_mock_models"
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
      <!-- Left Navigation Bar (reused from HomeView) -->
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
          <div class="nav-item" @click="$router.push('/upload-cxr')">
            <div class="nav-icon"><i class="bi bi-cloud-upload"></i></div>
            <div class="nav-label">Upload CXR</div>
          </div>
          <div class="nav-item active">
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
            Annotation :
            <span class="highlight"
              >Edited by Radiologist | Annotated by AI</span
            >
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
                {{ username.charAt(0) }}
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
          <!-- Left sidebar with annotation tools -->
          <div class="annotation-tools">
            <div
              class="tool-button"
              :class="{ active: activeTool === 'box' }"
              @click="setActiveTool('box')"
            >
              <i class="bi bi-grid"></i>
              <span>BOX</span>
            </div>
            <div
              class="tool-button"
              :class="{ active: activeTool === 'point' }"
              @click="setActiveTool('point')"
            >
              <i class="bi bi-plus-circle"></i>
              <span>POINT</span>
            </div>
            <div class="tool-group">
              <div
                class="tool-button"
                :class="{ active: activeTool === 'zoom' }"
                @click="setActiveTool('zoom')"
              >
                <i class="bi bi-search"></i>
                <span>ZOOM</span>
              </div>
              <div class="zoom-controls">
                <button class="zoom-btn" @click="zoomIn">IN</button>
                <button class="zoom-btn" @click="zoomOut">OUT</button>
              </div>
            </div>
            <div
              class="tool-button"
              :class="{ active: activeTool === 'light' }"
              @click="setActiveTool('light')"
            >
              <i class="bi bi-brightness-high"></i>
              <span>LIGHT</span>
            </div>

            <!-- Removing Abnormality Selection from sidebar -->

            <div class="brightness-slider" v-if="activeTool === 'light'">
              <input
                type="range"
                min="50"
                max="150"
                v-model="brightness"
                @input="adjustBrightness(brightness)"
                class="slider"
              />
              <div class="slider-labels">
                <span>50%</span>
                <span>150%</span>
              </div>
            </div>
            <div class="tool-group">
              <div class="tool-button">
                <i class="bi bi-arrow-counterclockwise"></i>
                <span>UNDO and REDO</span>
              </div>
              <div class="undo-redo-controls">
                <button class="undo-redo-btn" @click="undoAction">UNDO</button>
                <button class="undo-redo-btn" @click="redoAction">REDO</button>
              </div>
            </div>
          </div>

          <!-- Main content area with both original image and AI annotations -->
          <div class="main-content-area">
            <!-- Left side - Original image display area -->
            <div class="image-container">
              <div class="file-info-bar">
                <span
                  >Raw CXRay Name:
                  {{ currentImageName || "No file selected" }}</span
                >
                <button
                  class="upload-btn"
                  @click="triggerFileUpload"
                  :disabled="isModelLoading"
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
                  ref="imageContainer"
                  @click="handleClick"
                >
                  <img :src="currentImage" alt="X-ray image" ref="xrayImage" />
                  <div class="annotation-overlays">
                    <!-- Box annotations -->
                    <div
                      v-for="(box, index) in boxes"
                      :key="`box-${index}`"
                      class="annotation-box"
                      :class="{ selected: selectedBoxIndex === index }"
                      :style="{
                        left: `${box.x}px`,
                        top: `${box.y}px`,
                        width: `${box.width}px`,
                        height: `${box.height}px`,
                        borderColor: box.color || getBoxColor(box.type),
                        backgroundColor: `${
                          box.color || getBoxColor(box.type)
                        }33`, // Add transparency
                      }"
                      @mousedown.stop="selectBox(index, $event)"
                    >
                      <button
                        v-if="selectedBoxIndex === index"
                        @click.stop="deleteBox(index)"
                        class="delete-box-btn"
                      >
                        <i class="bi bi-x"></i>
                      </button>
                      <div
                        class="annotation-label"
                        :style="{
                          backgroundColor: box.color || getBoxColor(box.type),
                        }"
                      >
                        {{ box.label || box.type }}
                      </div>
                      <!-- Add resize handles -->
                      <div
                        v-if="selectedBoxIndex === index"
                        class="resize-handle top-left"
                        @mousedown.stop="startResize($event, 'top-left')"
                      ></div>
                      <div
                        v-if="selectedBoxIndex === index"
                        class="resize-handle top-right"
                        @mousedown.stop="startResize($event, 'top-right')"
                      ></div>
                      <div
                        v-if="selectedBoxIndex === index"
                        class="resize-handle bottom-left"
                        @mousedown.stop="startResize($event, 'bottom-left')"
                      ></div>
                      <div
                        v-if="selectedBoxIndex === index"
                        class="resize-handle bottom-right"
                        @mousedown.stop="startResize($event, 'bottom-right')"
                      ></div>
                    </div>

                    <!-- Point markers -->
                    <div
                      v-for="(point, index) in points"
                      :key="`point-${index}`"
                      class="point-marker"
                      :style="{
                        left: `${point.x}px`,
                        top: `${point.y}px`,
                      }"
                      @click.stop="removePoint(index)"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- Abnormality Selection Panel moved below image -->
              <div class="abnormality-type-container" @click.stop>
                <div class="abnormality-type-row">
                  <div class="abnormality-label">Abnormality Type:</div>
                  <select
                    class="abnormality-select"
                    v-model="selectedAbnormality"
                    @change="updateSelectedBoxType"
                    @click.stop
                  >
                    <option value="Nodule/Mass">Nodule/Mass</option>
                    <option value="Pleural Effusion">Pleural Effusion</option>
                    <option value="Cardiomegaly">Cardiomegaly</option>
                    <option value="Infiltration">Infiltration</option>
                    <option value="Pleural Thickening">Pleural Thickening</option>
                    <option value="Pulmonary Fibrosis">Pulmonary Fibrosis</option>
                    <option value="Consolidation">Consolidation</option>
                    <option value="Atelectasis">Atelectasis</option>
                    <option value="Pneumothorax">Pneumothorax</option>
                  </select>
                </div>
                
                <div class="abnormality-type-row">
                  <div class="abnormality-label">Subtype:</div>
                  <select
                    class="abnormality-select"
                    v-model="selectedSubtype"
                    @change="updateSelectedBoxSubtype"
                    @click.stop
                  >
                    <option value="No Subtype-Abnormality">No Subtype-Abnormality</option>
                    <option value="Subtype 1">Subtype 1</option>
                    <option value="Subtype 2">Subtype 2</option>
                    <option value="Subtype 3">Subtype 3</option>
                  </select>
                </div>
              </div>
              
              <!-- Download button moved to bottom -->
              <div v-if="currentImage" class="download-print-container">
                <button class="download-print-btn" @click="downloadExpertReport">
                  Download and Print
                </button>
              </div>

              <!-- Hidden file input for image upload -->
              <input
                type="file"
                id="xray-upload"
                ref="fileInput"
                accept="image/*"
                @change="handleFileUpload"
                class="hidden-file-input"
              />
            </div>

            <!-- Right side - AI annotations with vertical layout -->
            <div class="ai-annotations-container">
              <!-- Add AI Results header to match UploadCXRView -->
              <div class="results-header">
                <h2>AI Results</h2>
              </div>

              <!-- Mock model banner -->
              <div
                v-if="isUsingMockModel || modelStatus?.using_mock_models"
                class="model-status-banner"
              >
                <i class="bi bi-info-circle-fill"></i>
                <span>Using mock AI predictions (server is using lightweight model)</span>
              </div>

              <!-- PyTorch not installed notification -->
              <div
                v-if="modelError && modelError.includes('PyTorch')"
                class="model-status-banner"
              >
                <i class="bi bi-info-circle-fill"></i>
                <span>Server note: Using client-side mock predictions (PyTorch not installed)</span>
              </div>

              <!-- AI annotated image -->
              <div class="xray-image ai-image">
                <!-- Use the pre-rendered annotated image with bounding boxes -->
                <img
                  v-if="annotatedImage"
                  :src="annotatedImage"
                  alt="AI annotated X-ray"
                  ref="aiXrayImage"
                  class="standardized-image"
                />
                <!-- Use the clean image without annotations -->
                <img
                  v-else-if="cleanImage"
                  :src="cleanImage"
                  alt="X-ray without annotations"
                  ref="aiXrayImage"
                  class="standardized-image"
                />
                <!-- Fallback to the original image if no images from server yet -->
                <img
                  v-else-if="currentImage"
                  :src="currentImage"
                  alt="X-ray"
                  ref="aiXrayImage"
                />

                <!-- Loading state -->
                <transition name="fade">
                  <a-i-model-loader v-if="isModelLoading" />
                </transition>

                <!-- Error state - don't show PyTorch errors with warning icon -->
                <transition name="fade">
                  <model-error-overlay
                    v-if="modelError && !modelError.includes('PyTorch')"
                    :title="'Model could not be loaded'"
                    :message="modelError || 'Please try again later.'"
                    :show-retry="modelError && modelError.includes('loading')"
                    @retry="retryModelPrediction"
                  />
                </transition>

                <!-- No abnormalities message -->
                <div
                  v-if="
                    !isModelLoading &&
                    !modelError &&
                    aiPredictions.length === 0 &&
                    (cleanImage || currentImage)
                  "
                  class="no-abnormalities"
                >
                  <i class="bi bi-exclamation-triangle"></i>
                  <p>No abnormalities detected in the image</p>
                  <button @click="retryModelPrediction" class="retry-btn">
                    <i class="bi bi-arrow-clockwise"></i> Retry Detection
                  </button>
                </div>

                <!-- Empty state -->
                <div
                  v-if="!currentImage && !cleanImage && !annotatedImage"
                  class="placeholder-ai-message"
                >
                  <i class="bi bi-robot"></i>
                  <p>AI annotations will appear here</p>
                </div>
              </div>

              <!-- AI Confidence Summary - now below the image -->
              <div
                v-if="aiPredictions.length > 0"
                class="ai-detection-results"
              >
                <div class="summary-header" @click="toggleDetectionResults">
                  <h3>AI Detection Results:</h3>
                  <button class="toggle-btn">
                    <i
                      :class="
                        detectionResultsExpanded
                          ? 'bi bi-chevron-up'
                          : 'bi bi-chevron-down'
                      "
                    ></i>
                  </button>
                </div>
                <div v-show="detectionResultsExpanded" class="confidence-list">
                  <div
                    v-for="prediction in aiPredictions"
                    :key="prediction.id"
                    class="confidence-item"
                    :style="{
                      borderLeft: `4px solid ${getBoxColor(
                        prediction.class || ''
                      )}`,
                    }"
                  >
                    <span class="confidence-label">{{ prediction.class || "Unknown" }}:</span>
                    <span
                      class="confidence-value"
                      :style="{ color: getBoxColor(prediction.class || '') }"
                    >
                      {{ formatConfidence(prediction.score) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Download button -->
              <div class="download-print-container">
                <button class="download-print-btn" @click="generatePDF">
                  <i class="bi bi-file-earmark-pdf"></i> Download PDF Report
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading overlay -->
      <loading-overlay v-if="isLoading" message="Loading annotation data..." />
      <!-- Loading overlay -->
      <div v-if="isModelLoading" class="loader-overlay">
        <div class="loader"></div>
        <div>{{ loadingMessage || "Loading..." }}</div>
      </div>
    </div>
  </div>

  <!-- Add this at the end, right before the closing </template> tag -->
  <patient-info-modal 
    :show="showPatientInfoModal" 
    :reportType="currentReportType"
    @close="showPatientInfoModal = false"
    @submit="handlePatientSubmit"
  />
</template>

<script>
import { logout, health, runNetworkTest } from "../utils/api";
import LoadingOverlay from "../components/LoadingOverlay.vue";
import AIModelLoader from "../components/AIModelLoader.vue";
import ModelErrorOverlay from "../components/ModelErrorOverlay.vue";
import ModelService from "@/services/modelService";
import PatientInfoModal from "@/components/PatientInfoModal.vue";
import html2pdf from 'html2pdf.js';
import html2canvas from 'html2canvas';

export default {
  components: {
    LoadingOverlay,
    AIModelLoader,
    ModelErrorOverlay,
    PatientInfoModal
  },
  data() {
    return {
      apiUrl: apiUrl,
      username: "User",
      isLoading: false,
      isAuthenticated: false,
      connectionStatus: "Connected",
      hasError: false,
      errorMessage: "",
      errorDetails: null,
      retryCount: 0,
      showErrorDetails: false,
      hasToken: false,
      showUserMenu: false,
      currentImage: null,
      currentImageName: "",
      showSampleAnnotation: false,

      // Annotation tools
      activeTool: null, // 'box', 'point', 'zoom', 'light'
      boxes: [],
      points: [],
      isDrawingBox: false,
      isDraggingBox: false,
      showDefaultBox: false,
      currentBox: { x: 0, y: 0, width: 100, height: 100, type: "Nodule/Mass" },
      selectedBoxIndex: null,
      isResizing: false,
      resizeHandle: null,
      dragStartX: 0,
      dragStartY: 0,
      initialBoxState: null,

      // Annotation properties
      selectedAbnormality: "Nodule/Mass",
      selectedSubtype: "Select Subtype Abnormality",

      // Tool state
      zoomLevel: 1,
      brightness: 100,
      initialBoxPositions: [], // Store original box positions for zoom scaling
      aiPredictions: [],
      isModelLoading: false,
      modelError: null,
      originalImageWidth: 0,
      originalImageHeight: 0,
      isUsingMockModel: false,
      debugMode: false,
      lastApiResponse: null,
      aiDisplayImage: null,
      cleanImage: null,
      annotatedImage: null,

      // Add this new property
      detectionResultsExpanded: false,

      // Add modelStatus to store the response from model status check
      modelStatus: null,
      isDragging: false,
      
      // Add these new properties
      showPatientInfoModal: false,
      currentReportType: "Expert",
      loadingMessage: "",
    };
  },
  created() {
    try {
      this.hasToken = !!localStorage.getItem("authToken");

      // Extract username from token if available
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          const payload = token.split(".")[1];
          const decodedData = JSON.parse(atob(payload));
          this.username = decodedData.username || "User";
        } catch (e) {
          console.error("[Annotate] Error parsing token:", e);
          this.username = "User";
        }
      }
    } catch (e) {
      console.error("[Annotate] Error accessing localStorage:", e);
      this.hasToken = false;
    }
  },
  methods: {
    goToDashboard() {
      this.$router.push("/home");
    },
    async logout() {
      try {
        this.isLoading = true;
        await logout();
        this.backToLogin();
      } catch (error) {
        console.error("[Annotate] Logout error:", error);
        this.backToLogin();
      } finally {
        this.isLoading = false;
      }
    },
    runDiagnostics() {
      runNetworkTest();
      console.log("[Annotate] Network diagnostics completed");
    },
    retryLoading() {
      this.retryCount++;
      this.errorMessage = `Retrying connection (attempt ${this.retryCount})...`;
      console.log(`[Annotate] Retrying page load (attempt ${this.retryCount})`);
      this.loadData();
    },
    backToLogin() {
      try {
        localStorage.removeItem("authToken");
      } catch (e) {
        console.error("[Annotate] Error removing token:", e);
      }
      this.$router.push("/login");
    },
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    openUserSettings() {
      console.log("[Annotate] User settings clicked (not implemented yet)");
      this.showUserMenu = false;
      alert("User settings feature coming soon!");
    },
    // eslint-disable-next-line no-unused-vars
    closeUserMenu(e) {
      if (this.showUserMenu && !e.target.closest(".user-dropdown")) {
        this.showUserMenu = false;
      }
    },
    loadData() {
      // This would be where you load any necessary data
      console.log("[Annotate] Loading annotation data");
    },

    // Annotation Tool Methods
    setActiveTool(tool) {
      // If tool is 'box', create a new box when it's first selected
      if (tool === "box") {
        if (this.currentImage) {
          // Create a box in the center of the container
          const containerRect =
            this.$refs.imageContainer.getBoundingClientRect();
          const centerX = containerRect.width / 2;
          const centerY = containerRect.height / 2;

          // Create the new box and add it directly to boxes array
          const newBox = {
            x: centerX - 50,
            y: centerY - 50,
            width: 100,
            height: 100,
            type: this.selectedAbnormality,
            label: this.selectedAbnormality,
            color: this.getBoxColor(this.selectedAbnormality),
            subtype: "No Subtype-Abnormality",
          };

          this.boxes.push(newBox);

          // Store initial position for zoom scaling
          this.initialBoxPositions.push({
            ...newBox,
            x: newBox.x / this.zoomLevel,
            y: newBox.y / this.zoomLevel,
            width: newBox.width / this.zoomLevel,
            height: newBox.height / this.zoomLevel,
          });

          // Select the newly added box
          this.selectedBoxIndex = this.boxes.length - 1;

          // Don't show any default/preview box
          this.showDefaultBox = false;
        }
      } else {
        // Don't deselect box when changing tools - keep context for the panel
        // Only hide the default preview box when switching tools
        this.showDefaultBox = false;
      }

      this.activeTool = tool;

      // Set appropriate cursor
      if (tool === "box" || tool === "point") {
        document.body.style.cursor = "crosshair";
      } else {
        document.body.style.cursor = "default";
      }
    },

    // Add this new method to delete a box - completely rewritten for reliability
    deleteBox(index) {
      if (this.selectedBoxIndex === index) {
        this.selectedBoxIndex = null;
      }
      this.boxes.splice(index, 1);
      this.initialBoxPositions.splice(index, 1);
    },

    // File upload
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      // Check if the file is an image
      if (!file.type.match("image.*")) {
        alert("Please select an image file");
        return;
      }

      this.currentImageName = file.name;
      const reader = new FileReader();

      reader.onload = async (e) => {
        // Create an image element to get the natural dimensions
        const img = new Image();
        img.onload = async () => {
          // Store the original image dimensions
          this.originalImageWidth = img.naturalWidth;
          this.originalImageHeight = img.naturalHeight;

          // Set the current image
          this.currentImage = e.target.result;

          // Reset annotation state
          this.boxes = [];
          this.points = [];
          this.selectedBoxIndex = null;
          this.initialBoxPositions = [];
          this.zoomLevel = 1;

          // Don't show default box when loading a new image
          this.showDefaultBox = false;

          // Wait for the DOM to update with the new image
          await this.$nextTick();

          // Ensure both left and right display images have the same constraints
          if (this.$refs.xrayImage && this.$refs.aiXrayImage) {
            const leftImg = this.$refs.xrayImage;
            const rightImg = this.$refs.aiXrayImage;

            // Use the same styling for both images
            leftImg.style.maxWidth = "100%";
            leftImg.style.maxHeight = "100%";
            rightImg.style.maxWidth = "100%";
            rightImg.style.maxHeight = "100%";
          }

          // Get AI predictions
          await this.getAIPredictions();
        };

        img.src = e.target.result;
      };

      reader.readAsDataURL(file);
    },

    async getAIPredictions() {
      try {
        this.isModelLoading = true;
        this.modelError = null;
        this.isUsingMockModel = false;
        this.lastApiResponse = null;

        // First check if the model is ready
        const modelStatus = await ModelService.checkModelStatus();
        this.modelStatus = modelStatus; // Store the model status in data
        this.lastApiResponse = { modelStatus };

        // Check if we're using a mock model
        if (
          modelStatus.using_mock_models ||
          modelStatus.model_type === "mock"
        ) {
          this.isUsingMockModel = true;
          console.warn("Using mock model for predictions");
        }

        if (modelStatus.status === "loading") {
          this.modelError =
            "Model is still loading. Please wait a moment and try again.";
          this.isModelLoading = false;
          return;
        } else if (
          modelStatus.status === "error" ||
          modelStatus.status === "not_loaded"
        ) {
          this.modelError =
            "Model could not be loaded. Please try again later.";
          this.isModelLoading = false;
          return;
        }

        // Download the image from the URL
        const response = await fetch(this.currentImage);
        const blob = await response.blob();

        // Create a File object from the Blob
        const imageFile = new File([blob], "image.jpg", { type: "image/jpeg" });

        console.log(
          "Getting AI predictions for image:",
          imageFile.name,
          imageFile.size
        );

        // Get predictions from model service - includes pre-rendered annotated image
        const result = await ModelService.predict(imageFile);
        console.log("Received prediction result:", result);

        // Debug the image format
        if (result.annotatedImage) {
          console.log(
            "Annotated image format:",
            result.annotatedImage.substring(0, 100) + "..."
          );
        } else {
          console.warn("No annotated image received!");
        }

        // Store the predictions response for debugging
        this.lastApiResponse = {
          modelStatus,
          result,
          timestamp: new Date().toISOString(),
        };

        // Update the display images from the server
        this.cleanImage = result.cleanImage;
        this.annotatedImage = result.annotatedImage;

        // Make sure the annotated image is formatted as a data URL if not already
        if (this.annotatedImage && !this.annotatedImage.startsWith("data:")) {
          console.log("Converting annotated image to data URL format");
          this.annotatedImage = `data:image/png;base64,${this.annotatedImage}`;
        }

        if (!result.predictions || result.predictions.length === 0) {
          // Don't show an error message for empty predictions
          // Just set the aiPredictions array to empty
          this.aiPredictions = [];
          this.isModelLoading = false;
          return;
        }

        // Update AI predictions (still useful for displaying confidence summary)
        this.aiPredictions = result.predictions.map((pred) => ({
          ...pred,
          id: `ai-${Math.random().toString(36).substr(2, 9)}`,
          isAIPrediction: true,
          // Ensure class is always defined
          class: pred.class || "Unknown",
        }));

        // Do NOT add AI predictions to boxes array (left side manual annotations)
        // this.boxes.push(...this.aiPredictions);
      } catch (error) {
        console.error("Error getting AI predictions:", error);
        // Provide more detailed error message to the user
        this.modelError =
          error.message || "Failed to get AI predictions. Please try again.";

        // Store the error for debugging
        this.lastApiResponse = {
          error: error.message || "Unknown error",
          stack: error.stack,
          timestamp: new Date().toISOString(),
        };
      } finally {
        this.isModelLoading = false;
      }
    },

    // Helper method to format confidence scores
    formatConfidence(score) {
      return `${(score * 100).toFixed(0)}%`;
    },

    // Box drawing methods
    handleMouseDown(e) {
      // Don't process if no image is loaded or if not in box tool mode
      if (!this.currentImage || this.activeTool !== "box") return;

      // Skip if clicking on select elements or the abnormality panel
      if (
        e.target.tagName === "SELECT" ||
        e.target.tagName === "OPTION" ||
        e.target.closest(".abnormality-selection-container")
      ) {
        return;
      }

      // Get coordinates relative to the image container
      const rect = this.$refs.imageContainer.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      // Check if we clicked on an existing box
      let clickedOnBox = false;

      for (let i = 0; i < this.boxes.length; i++) {
        const box = this.boxes[i];
        if (
          mouseX >= box.x &&
          mouseX <= box.x + box.width &&
          mouseY >= box.y &&
          mouseY <= box.y + box.height
        ) {
          // We clicked on a box, select it
          this.selectedBoxIndex = i;
          this.isDraggingBox = true;
          this.dragStartX = mouseX;
          this.dragStartY = mouseY;
          this.initialBoxState = { ...box };
          clickedOnBox = true;
          break;
        }
      }

      // If we didn't click on a box, deselect the current box
      if (!clickedOnBox && !e.target.classList.contains("resize-handle")) {
        this.selectedBoxIndex = null;
      }
    },

    handleMouseMove(e) {
      if (!this.currentImage) return;

      const rect = this.$refs.imageContainer.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      if (this.isDraggingBox && this.selectedBoxIndex !== null) {
        // Dragging a selected box
        const deltaX = mouseX - this.dragStartX;
        const deltaY = mouseY - this.dragStartY;

        const box = this.boxes[this.selectedBoxIndex];
        box.x = this.initialBoxState.x + deltaX;
        box.y = this.initialBoxState.y + deltaY;

        // Keep the box within the image container
        if (box.x < 0) box.x = 0;
        if (box.y < 0) box.y = 0;
        if (box.x + box.width > rect.width) {
          box.x = rect.width - box.width;
        }
        if (box.y + box.height > rect.height) {
          box.y = rect.height - box.height;
        }
      } else if (this.isResizing && this.selectedBoxIndex !== null) {
        this.resizeBox(e);
      }
    },

    handleMouseUp() {
      if (this.isDraggingBox) {
        this.isDraggingBox = false;

        // Update the initialBoxPositions after dragging is complete
        if (this.selectedBoxIndex !== null) {
          this.initialBoxPositions[this.selectedBoxIndex] = {
            ...this.boxes[this.selectedBoxIndex],
            x: this.boxes[this.selectedBoxIndex].x / this.zoomLevel,
            y: this.boxes[this.selectedBoxIndex].y / this.zoomLevel,
            width: this.boxes[this.selectedBoxIndex].width / this.zoomLevel,
            height: this.boxes[this.selectedBoxIndex].height / this.zoomLevel,
          };
        }
      } else if (this.isResizing) {
        this.isResizing = false;
        this.resizeHandle = null;
        document.body.style.cursor = "default";

        // Update initialBoxPositions after resizing
        if (this.selectedBoxIndex !== null) {
          this.initialBoxPositions[this.selectedBoxIndex] = {
            ...this.boxes[this.selectedBoxIndex],
            x: this.boxes[this.selectedBoxIndex].x / this.zoomLevel,
            y: this.boxes[this.selectedBoxIndex].y / this.zoomLevel,
            width: this.boxes[this.selectedBoxIndex].width / this.zoomLevel,
            height: this.boxes[this.selectedBoxIndex].height / this.zoomLevel,
          };
        }
      }
    },

    // Box selection and manipulation
    selectBox(index, event) {
      if (this.activeTool !== "box") return;

      this.selectedBoxIndex = index;

      // Don't propagate if clicking on a resize handle
      if (event.target.classList.contains("resize-handle")) {
        event.stopPropagation();
        return;
      }

      // Start dragging
      const rect = this.$refs.imageContainer.getBoundingClientRect();
      this.dragStartX = event.clientX - rect.left;
      this.dragStartY = event.clientY - rect.top;

      // Set isDraggingBox flag to true
      this.isDraggingBox = true;

      // Store the initial box state for dragging
      this.initialBoxState = { ...this.boxes[index] };

      event.stopPropagation();
    },

    startResize(event, handle) {
      if (this.activeTool !== "box") return;

      this.isResizing = true;
      this.resizeHandle = handle;

      const rect = this.$refs.imageContainer.getBoundingClientRect();
      this.dragStartX = event.clientX - rect.left;
      this.dragStartY = event.clientY - rect.top;

      // Store initial box state for resizing
      this.initialBoxState = { ...this.boxes[this.selectedBoxIndex] };

      // Set cursor based on resize handle
      switch (handle) {
        case "top-left":
          document.body.style.cursor = "nwse-resize";
          break;
        case "top-right":
          document.body.style.cursor = "nesw-resize";
          break;
        case "bottom-left":
          document.body.style.cursor = "nesw-resize";
          break;
        case "bottom-right":
          document.body.style.cursor = "nwse-resize";
          break;
      }

      event.stopPropagation();
      event.preventDefault();
    },

    resizeBox(event) {
      if (!this.isResizing || this.selectedBoxIndex === null) return;

      const rect = this.$refs.imageContainer.getBoundingClientRect();
      const currentX = event.clientX - rect.left;
      const currentY = event.clientY - rect.top;

      const deltaX = currentX - this.dragStartX;
      const deltaY = currentY - this.dragStartY;

      const box = this.boxes[this.selectedBoxIndex];
      const initialBox = this.initialBoxState;

      switch (this.resizeHandle) {
        case "top-left":
          box.x = initialBox.x + deltaX;
          box.y = initialBox.y + deltaY;
          box.width = initialBox.width - deltaX;
          box.height = initialBox.height - deltaY;
          break;
        case "top-right":
          box.y = initialBox.y + deltaY;
          box.width = initialBox.width + deltaX;
          box.height = initialBox.height - deltaY;
          break;
        case "bottom-left":
          box.x = initialBox.x + deltaX;
          box.width = initialBox.width - deltaX;
          box.height = initialBox.height + deltaY;
          break;
        case "bottom-right":
          box.width = initialBox.width + deltaX;
          box.height = initialBox.height + deltaY;
          break;
      }

      // Ensure minimum size
      if (box.width < 10) {
        box.width = 10;
        box.x = initialBox.x + initialBox.width - 10;
      }

      if (box.height < 10) {
        box.height = 10;
        box.y = initialBox.y + initialBox.height - 10;
      }
    },

    // Point tool methods
    handleClick(e) {
      // Only process clicks for point tool
      if (this.activeTool !== "point") return;

      // Skip if clicking on select elements or the abnormality panel
      if (
        e.target.tagName === "SELECT" ||
        e.target.tagName === "OPTION" ||
        e.target.closest(".abnormality-selection-container") ||
        e.target.classList.contains("point-marker")
      ) {
        return;
      }

      const rect = this.$refs.imageContainer.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Add a new point at the click coordinates
      this.points.push({
        x,
        y,
        color: "#f59e0b", // Orange color for points
      });

      console.log("Added point at", x, y);
    },

    // Helper methods
    getBoxStyle(box) {
      if (!box) return {}; // Safety check

      // Handle predictions which have a different structure
      if (box.box && Array.isArray(box.box)) {
        // This is a prediction with box coordinates in array format
        // The box coordinates are already scaled to the display size by ModelService
        const boxType = box.class || "";
        const solidColor = this.getBoxColor(boxType);
        const transparentColor = this.getBoxColor(boxType, 0.5);

        return {
          left: `${Math.max(0, box.box[0] || 0)}px`,
          top: `${Math.max(0, box.box[1] || 0)}px`,
          width: `${Math.max(10, (box.box[2] || 0) - (box.box[0] || 0))}px`,
          height: `${Math.max(10, (box.box[3] || 0) - (box.box[1] || 0))}px`,
          border: `2px solid ${solidColor}`,
          backgroundColor: transparentColor,
        };
      }

      // Regular box format
      const boxType = box.type || "";
      const solidColor = this.getBoxColor(boxType);
      const transparentColor = this.getBoxColor(boxType, 0.5);

      return {
        left: `${box.x || 0}px`,
        top: `${box.y || 0}px`,
        width: `${box.width || 0}px`,
        height: `${box.height || 0}px`,
        border: `2px solid ${solidColor}`,
        backgroundColor: transparentColor,
      };
    },

    getBoxColor(type, opacity = null) {
      // Handle null or undefined values
      if (!type) {
        return opacity ? `rgba(59, 130, 246, ${opacity})` : "#3b82f6"; // Default to blue
      }

      // Normalize the type string for case-insensitive comparison
      const normalizedType = type.toLowerCase();

      // If opacity is null, return solid color, otherwise return rgba
      // Each abnormality gets its own distinct color
      if (normalizedType.includes("cardiomegaly")) {
        return opacity ? `rgba(239, 68, 68, ${opacity})` : "#ef4444"; // Red
      } else if (
        normalizedType.includes("pleural thickening") ||
        normalizedType.includes("pleural-thickening")
      ) {
        return opacity ? `rgba(139, 92, 246, ${opacity})` : "#8b5cf6"; // Purple
      } else if (
        normalizedType.includes("pulmonary fibrosis") ||
        normalizedType.includes("pulmonary-fibrosis")
      ) {
        return opacity ? `rgba(236, 72, 153, ${opacity})` : "#ec4899"; // Pink
      } else if (
        normalizedType.includes("pleural effusion") ||
        normalizedType.includes("pleural-effusion")
      ) {
        return opacity ? `rgba(245, 158, 11, ${opacity})` : "#f59e0b"; // Amber/Orange
      } else if (
        normalizedType.includes("nodule") ||
        normalizedType.includes("mass")
      ) {
        return opacity ? `rgba(59, 130, 246, ${opacity})` : "#3b82f6"; // Blue
      } else if (normalizedType.includes("infiltration")) {
        return opacity ? `rgba(16, 185, 129, ${opacity})` : "#10b981"; // Green
      } else if (normalizedType.includes("consolidation")) {
        return opacity ? `rgba(14, 165, 233, ${opacity})` : "#0ea5e9"; // Sky Blue
      } else if (normalizedType.includes("atelectasis")) {
        return opacity ? `rgba(249, 115, 22, ${opacity})` : "#f97316"; // Orange
      } else if (normalizedType.includes("pneumothorax")) {
        return opacity ? `rgba(168, 85, 247, ${opacity})` : "#a855f7"; // Violet
      } else {
        // Default color for unknown types
        return opacity ? `rgba(59, 130, 246, ${opacity})` : "#3b82f6"; // Default Blue
      }
    },

    // Zoom methods
    zoomIn() {
      if (this.zoomLevel < 3) {
        const oldZoom = this.zoomLevel;
        this.zoomLevel += 0.1;
        this.applyZoom(oldZoom);
      }
    },

    zoomOut() {
      if (this.zoomLevel > 0.5) {
        const oldZoom = this.zoomLevel;
        this.zoomLevel -= 0.1;
        this.applyZoom(oldZoom);
      }
    },

    applyZoom(oldZoom) {
      if (this.$refs.xrayImage) {
        this.$refs.xrayImage.style.transform = `scale(${this.zoomLevel})`;

        // If first time zooming, store initial positions
        if (!this.initialBoxPositions.length && this.boxes.length > 0) {
          this.initialBoxPositions = this.boxes.map((box) => ({ ...box }));
        }

        // Scale all boxes
        const zoomRatio = this.zoomLevel / (oldZoom || 1);

        // Update current boxes
        this.boxes = this.boxes.map((box, index) => {
          const initialBox = this.initialBoxPositions[index] || box;

          return {
            ...box,
            x: initialBox.x * this.zoomLevel,
            y: initialBox.y * this.zoomLevel,
            width: initialBox.width * this.zoomLevel,
            height: initialBox.height * this.zoomLevel,
          };
        });

        // Update current drawing box if applicable
        if (this.isDrawingBox || this.showDefaultBox) {
          const scaleFactor = zoomRatio;
          this.currentBox = {
            ...this.currentBox,
            x: this.currentBox.x * scaleFactor,
            y: this.currentBox.y * scaleFactor,
            width: this.currentBox.width * scaleFactor,
            height: this.currentBox.height * scaleFactor,
          };
        }
      }
    },

    // Brightness control (simplified implementation)
    adjustBrightness(value) {
      this.brightness = value;
      if (this.$refs.xrayImage) {
        this.$refs.xrayImage.style.filter = `brightness(${value}%)`;
      }
    },

    // UNDO/REDO methods (simplified)
    undoAction() {
      if (this.activeTool === "box" && this.boxes.length > 0) {
        this.boxes.pop();
        this.selectedBoxIndex = null;
      } else if (this.activeTool === "point" && this.points.length > 0) {
        this.points.pop();
      }
    },

    redoAction() {
      // Would need history state to implement properly
      console.log("Redo not implemented");
    },

    removeBox(index) {
      if (this.selectedBoxIndex === index) {
        this.selectedBoxIndex = null;
      }
      this.boxes.splice(index, 1);
      this.initialBoxPositions.splice(index, 1); // Also remove from initial positions
    },

    retryModelPrediction() {
      this.isModelLoading = true;
      this.modelError = null;
      this.getAIPredictions();
    },

    debugModeToggle() {
      this.debugMode = !this.debugMode;
    },

    reduceConfidenceThreshold() {
      // Implement logic to reduce confidence threshold
      console.log("Reducing confidence threshold");
    },

    // Add this new method
    toggleDetectionResults() {
      this.detectionResultsExpanded = !this.detectionResultsExpanded;
    },

    triggerFileUpload() {
      if (!this.isModelLoading) {
        this.$refs.fileInput.click();
      }
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

      this.currentImageName = file.name;
      const reader = new FileReader();

      reader.onload = async (e) => {
        // Create an image element to get the natural dimensions
        const img = new Image();
        img.onload = async () => {
          // Store the original image dimensions
          this.originalImageWidth = img.naturalWidth;
          this.originalImageHeight = img.naturalHeight;

          // Set the current image
          this.currentImage = e.target.result;

          // Reset annotation state
          this.boxes = [];
          this.points = [];
          this.selectedBoxIndex = null;
          this.initialBoxPositions = [];
          this.zoomLevel = 1;

          // Don't show default box when loading a new image
          this.showDefaultBox = false;

          // Wait for the DOM to update with the new image
          await this.$nextTick();

          // Ensure both left and right display images have the same constraints
          if (this.$refs.xrayImage && this.$refs.aiXrayImage) {
            const leftImg = this.$refs.xrayImage;
            const rightImg = this.$refs.aiXrayImage;

            // Use the same styling for both images
            leftImg.style.maxWidth = "100%";
            leftImg.style.maxHeight = "100%";
            rightImg.style.maxWidth = "100%";
            rightImg.style.maxHeight = "100%";
          }

          // Get AI predictions
          await this.getAIPredictions();
        };

        img.src = e.target.result;
      };

      reader.readAsDataURL(file);
    },
    async checkModelStatus() {
      try {
        const modelStatus = await ModelService.checkModelStatus();
        this.modelStatus = modelStatus;

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
    updateSelectedBoxType() {
      if (this.selectedBoxIndex !== null && this.boxes[this.selectedBoxIndex]) {
        // Update the type of the selected box
        this.boxes[this.selectedBoxIndex].type = this.selectedAbnormality;
        this.boxes[this.selectedBoxIndex].label = this.selectedAbnormality;

        // Always update the color based on the abnormality type
        this.boxes[this.selectedBoxIndex].color = this.getBoxColor(
          this.selectedAbnormality
        );
      }
      // Store the selection even if no box is selected, to use as default for new boxes
    },
    updateSelectedBoxSubtype() {
      if (this.selectedBoxIndex !== null && this.boxes[this.selectedBoxIndex]) {
        // Update the subtype of the selected box
        this.boxes[this.selectedBoxIndex].subtype = this.selectedSubtype;
      }
      // Store the selection even if no box is selected, to use as default for new boxes
    },
    setBoxColor(color) {
      this.selectedColor = color;

      if (this.selectedBoxIndex !== null) {
        // Update the color of the selected box
        this.boxes[this.selectedBoxIndex].color = color;
        this.boxes[this.selectedBoxIndex].customColor = true;
      }
    },
    removePoint(index) {
      this.points.splice(index, 1);
    },
    downloadAndPrint() {
      // Implement download and print functionality
      console.log("Download and print functionality not implemented yet");
    },
    downloadExpertReport() {
      this.currentReportType = "Expert";
      this.showPatientInfoModal = true;
    },
    downloadAIReport() {
      this.currentReportType = "AI";
      this.showPatientInfoModal = true;
    },
    handlePatientSubmit(data) {
      const { patientInfo, reportType } = data;
      
      // Close the modal
      this.showPatientInfoModal = false;
      
      // Show loading overlay
      this.isModelLoading = true;
      this.loadingMessage = "Generating PDF report...";
      
      try {
        // Get current date and time
        const currentDate = new Date().toISOString().split('T')[0];
        const currentTime = new Date().toTimeString().slice(0, 5);
        
        // Create a template with the patient information
        let templateHtml = `
          <!DOCTYPE html>
          <html lang="en">
          <head>
              <meta charset="UTF-8">
              <title>Radiographic Report</title>
              <style>
                  body {
                      font-family: 'Times New Roman', Times, serif;
                      margin: 0;
                      padding: 20px;
                      font-size: 12pt;
                  }
                  .header, .footer {
                      text-align: center;
                      margin-bottom: 20px;
                  }
                  .header img {
                      width: 150px; 
                  }
                  .header h1 {
                      margin: 0;
                      color: #d00000; 
                      font-size: 24pt;
                  }
                  .header h4{
                      margin-top: -10px;
                  }
                  .content {
                      margin-top: 20px;
                  }
                  .patient-info, .interpretation, .abnormalities {
                      margin-bottom: 20px;
                  }
                  .patient-info td {
                      padding: 2px 20px;
                  }
                  .signature {
                      margin-top: 80px;
                      text-align: right;
                  }
                  .signature img {
                      width: 100px; 
                  }
                  .interpretation h3{
                      text-align: center;
                      margin-top: 50px;
                  }
                  .findings h3 {
                      text-align: center;
                  }
                  .interpretation p{
                      margin-top: 30px;
                  }
                  .footer{
                      margin-top: 200px;
                  }
                  .images {
                      page-break-before: always;
                      text-align: center;
                  }
                  .images img{
                      width: 150mm;
                      height: 150mm;
                      display: block;
                      margin: 0 auto;
                  }
                  .radiologist-info{
                      text-align: right;
                  }
                  h3 {
                      text-align: center;
                  }
              </style>
          </head>
          <body>
              <div class="header">
                  <h4>CXRAide Annotation Tool</h4>
                  <h1>RADIOGRAPHIC REPORT</h1>
              </div>
              <div class="content">
                  <table class="patient-info">
                      <tr>
                          <hr>
                          <td>Patient Name:</td>
                          <td>${patientInfo.name || 'N/A'}</td>
                          <td>Patient ID No.:</td>
                          <td>${patientInfo.id || 'N/A'}</td>
                      </tr>
                      <tr>
                          <td>Gender:</td>
                          <td>${patientInfo.gender || 'N/A'}</td>
                          <td>Age:</td>
                          <td>${patientInfo.age || 'N/A'}</td>
                      </tr>
                      <tr>
                          <td>Exam Taken:</td>
                          <td>${patientInfo.examTaken || 'CHEST'}</td>
                          <td>Address:</td>
                          <td>${patientInfo.address || 'DAVAO CITY'}</td>
                      </tr>
                      <tr>
                          <td>Result Date:</td>
                          <td>${currentDate}</td>
                          <td>Result Time:</td>
                          <td>${currentTime}</td>
                      </tr>
                  </table>
                  <hr>
                  <div class="clinical-indication">
                      <h3>CLINICAL INDICATION</h3>
                      <p>${patientInfo.clinicalIndication || 'N/A'}</p>
                  </div>
              
                  <div class="findings">
                      <h3>FINDINGS</h3>
                      <p><strong>Lungs:</strong> ${patientInfo.findings.lungs || 'N/A'}</p>
                      <p><strong>Heart:</strong> ${patientInfo.findings.heart || 'N/A'}</p>
                      <p><strong>Mediastinum:</strong> ${patientInfo.findings.mediastinum || 'N/A'}</p>
                      <p><strong>Diaphragm and Pleura:</strong> ${patientInfo.findings.diaphragmPleura || 'N/A'}</p>
                      <p><strong>Soft Tissues and Bones:</strong> ${patientInfo.findings.softTissuesBones || 'N/A'}</p>
                      <p>${patientInfo.findings.additional || ''}</p>
                  </div>

                  <div class="abnormalities">
                      <h3>THE ABNORMALITY FOUND IS/ARE:</h3>
                      <p><strong>Main Abnormality:</strong> ${patientInfo.abnormalities.main || 'N/A'}</p>
                      <p><strong>Sub Abnormality:</strong> ${patientInfo.abnormalities.sub || 'N/A'}</p>
                  </div>
                  
                  <div class="impression">
                      <h3>IMPRESSION</h3>
                      <p>${patientInfo.impression || 'N/A'}</p>
                  </div>
              
                  <div class="recommendations">
                      <h3>RECOMMENDATIONS</h3>
                      <p>${patientInfo.recommendations || 'N/A'}</p>
                  </div>
              
                  <div class="radiologist-info">
                      <h3>REPORT PREPARED BY</h3>
                      <p><strong>Radiologist:</strong> Dr. ${patientInfo.radiologist || 'N/A'}</p>
                      <p><strong>Radiographer:</strong> ${patientInfo.radiographer || 'N/A'}</p>
                  </div>
              </div>

              <div class="images">
                  <h4>Chest X-ray Image (${reportType} Annotated)</h4>
                  <img src="${reportType === 'Expert' ? this.currentImage : this.annotatedImage}" alt="Annotated Chest X-ray">
              </div>
              
              <div class="footer">
                  <p>Not Valid without seal</p>
              </div>
          </body>
          </html>
        `;
        
        // Convert the HTML template to PDF
        const element = document.createElement('div');
        element.innerHTML = templateHtml;
        document.body.appendChild(element);
        
        // Configure PDF options
        const options = {
          margin: 10,
          filename: `CXRaide_Report_${patientInfo.id}_${currentDate}.pdf`,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };
        
        // Generate the PDF
        html2pdf().from(element).set(options).save();
        
        // Clean up the DOM
        document.body.removeChild(element);
        
        console.log("[PDF] Report generated successfully");
      } catch (error) {
        console.error("[PDF] Error generating report:", error);
        alert("Error generating PDF report. Please try again.");
      } finally {
        // Hide loading overlay
        this.isModelLoading = false;
        this.loadingMessage = "";
      }
    },
    cancelAction() {
      // Handle cancel action - could reset or do nothing
      console.log("Action cancelled");
    },
    // Add a new cleanup method for image references
    cleanupImageReferences() {
      // Release object URLs if we created any
      if (this.currentImage && this.currentImage.startsWith('blob:')) {
        try {
          URL.revokeObjectURL(this.currentImage);
        } catch (e) {
          console.error("Error revoking object URL:", e);
        }
      }
      
      if (this.cleanImage && this.cleanImage.startsWith('blob:')) {
        try {
          URL.revokeObjectURL(this.cleanImage);
        } catch (e) {
          console.error("Error revoking object URL:", e);
        }
      }
      
      if (this.annotatedImage && this.annotatedImage.startsWith('blob:')) {
        try {
          URL.revokeObjectURL(this.annotatedImage);
        } catch (e) {
          console.error("Error revoking object URL:", e);
        }
      }
      
      // Remove reference to DOM elements to prevent memory leaks
      if (this.$refs.xrayImage) {
        // Remove any event listeners that might be attached
        const xrayImg = this.$refs.xrayImage;
        if (xrayImg) {
          xrayImg.onload = null;
          xrayImg.onerror = null;
        }
      }
      
      if (this.$refs.aiXrayImage) {
        const aiImg = this.$refs.aiXrayImage;
        if (aiImg) {
          aiImg.onload = null;
          aiImg.onerror = null;
        }
      }
      
      if (this.$refs.imageContainer) {
        // Clear any event listeners from the container
        const container = this.$refs.imageContainer;
        if (container) {
          // Vue will handle most event listeners, but clean up any manually added ones
          container.onclick = null;
        }
      }
    },
    generatePDF() {
      this.currentReportType = "Expert";
      this.showPatientInfoModal = true;
    },
  },
  watch: {
    selectedBoxIndex(newValue) {
      if (newValue !== null && this.boxes[newValue]) {
        // Update form controls to match the selected box
        const selectedBox = this.boxes[newValue];
        this.selectedAbnormality = selectedBox.type || "Nodule/Mass";
        this.selectedSubtype = selectedBox.subtype || "No Subtype-Abnormality";
      }
      // If no box is selected, keep the current selections for new boxes
    },
    selectedAbnormality() {
      // Let the updateSelectedBoxType method handle the changes
      if (this.selectedBoxIndex !== null && this.boxes[this.selectedBoxIndex]) {
        this.updateSelectedBoxType();
      }
      // If no box is selected, the selection is stored for future use
    },
    activeTool(newValue) {
      // Reset cursor when tool changes
      if (newValue !== "point") {
        document.body.style.cursor = "default";
      } else {
        document.body.style.cursor = "crosshair";
      }
    },
  },
  mounted() {
    document.addEventListener("click", this.closeUserMenu);

    // Add event listeners for box dragging and resizing
    document.addEventListener("mousedown", this.handleMouseDown);
    document.addEventListener("mousemove", this.handleMouseMove);
    document.addEventListener("mouseup", this.handleMouseUp);

    // Set default tool but don't show default box
    this.activeTool = null; // Don't automatically select the box tool
    this.showDefaultBox = false;

    // Check model status
    this.checkModelStatus();
  },
  beforeUnmount() {
    document.removeEventListener("click", this.closeUserMenu);

    // Remove mouse event listeners
    document.removeEventListener("mousedown", this.handleMouseDown);
    document.removeEventListener("mousemove", this.handleMouseMove);
    document.removeEventListener("mouseup", this.handleMouseUp);

    // Reset cursor
    document.body.style.cursor = "default";
    
    // Cancel any pending API requests to prevent errors after component is unmounted
    ModelService.cancelRequests();
    
    // Clean up references to DOM elements
    this.cleanupImageReferences();
    
    // Reset all state to prevent memory leaks
    this.currentImage = null;
    this.cleanImage = null;
    this.annotatedImage = null;
    this.boxes = [];
    this.points = [];
    this.isModelLoading = false;
  },
};
</script>

<style scoped>
/* Import Bootstrap Icons */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css");

/* Reuse common styles from HomeView */
.annotate-container {
  min-height: 100vh;
}

/* App Layout with Sidebar */
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar Navigation Styles (from HomeView) */
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

/* Annotate specific styles */
.annotate-wrapper {
  flex: 1;
  padding: 1.5rem;
  margin-left: 240px;
  max-width: calc(100% - 240px);
}

.annotate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.annotate-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #f3f4f6;
  margin-bottom: 0;
}

.highlight {
  color: #e5e7eb;
  font-weight: 400;
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

.user-dropdown {
  position: relative;
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
}

.dropdown-item:not(:last-child) {
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

/* Annotation Layout */
.annotation-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  height: calc(100vh - 200px);
}

.annotation-tools {
  width: 120px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.tool-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-button:hover {
  background: rgba(59, 130, 246, 0.15);
}

.tool-button i {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
  color: #60a5fa;
}

.tool-button span {
  font-size: 0.7rem;
  font-weight: 600;
  color: #e5e7eb;
}

.tool-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.zoom-controls,
.undo-redo-controls {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.zoom-btn,
.undo-redo-btn {
  font-size: 0.6rem;
  padding: 0.35rem 0.5rem;
  background: rgba(59, 130, 246, 0.2);
  border: none;
  border-radius: 0.25rem;
  color: #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zoom-btn:hover,
.undo-redo-btn:hover {
  background: rgba(59, 130, 246, 0.4);
}

.image-container,
.ai-annotations-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  height: 100%;
}

.image-title {
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  color: #e5e7eb;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  background: rgba(15, 23, 42, 0.7);
  border-radius: 1rem 1rem 0 0;
}

.xray-image {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #000;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.xray-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}

.placeholder-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  padding: 2rem;
}

.placeholder-image i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.placeholder-image p {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
}

/* File upload styling */
.hidden-file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.file-upload-label {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  color: white;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.file-upload-label:hover {
  background: linear-gradient(90deg, #2563eb, #4f94ff);
  transform: translateY(-2px);
}

.upload-placeholder-button {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  color: white;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.upload-placeholder-button:hover {
  background: linear-gradient(90deg, #2563eb, #4f94ff);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
}

.upload-button {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.image-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.5rem 0.5rem 0 0;
  font-size: 0.9rem;
  color: #e5e7eb;
  margin-bottom: 0.25rem;
}

/* Annotation box styling */
.annotation-box {
  position: absolute;
  border-radius: 4px;
  cursor: move;
  touch-action: none;
  pointer-events: all;
  z-index: 5;
}

.annotation-box.selected {
  border-width: 3px;
  border-style: dashed;
  z-index: 10;
}

.delete-box-btn {
  position: absolute;
  top: -15px;
  right: -15px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  padding: 0;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 1000; /* Ensure this is higher than any other element */
  opacity: 1;
}

.delete-box-btn:hover {
  background-color: #d32f2f;
  transform: scale(1.1);
  opacity: 1;
}

.annotation-label {
  position: absolute;
  top: -24px;
  left: 0;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 3px;
  white-space: nowrap;
  z-index: 20;
}

.resize-handle {
  position: absolute;
  width: 12px;
  height: 12px;
  background-color: white;
  border: 2px solid #3b82f6;
  border-radius: 50%;
}

.resize-handle.top-left {
  top: -6px;
  left: -6px;
  cursor: nwse-resize;
}

.resize-handle.top-right {
  top: -6px;
  right: -6px;
  cursor: nesw-resize;
}

.resize-handle.bottom-left {
  bottom: -6px;
  left: -6px;
  cursor: nesw-resize;
}

.resize-handle.bottom-right {
  bottom: -6px;
  right: -6px;
  cursor: nwse-resize;
}

/* Point marker */
.point-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  background-color: #f59e0b;
  border: 2px solid white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s ease;
}

.point-marker:hover {
  transform: translate(-50%, -50%) scale(1.2);
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.7);
}

/* Tool button active state */
.tool-button.active {
  background: rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

/* Form section disabled state */
.abnormality-section.disabled {
  opacity: 0.6;
  pointer-events: none;
}

/* Image container */
.xray-image {
  position: relative;
  overflow: hidden;
}

.xray-image img {
  transition: transform 0.3s ease, filter 0.3s ease;
  transform-origin: center;
}

/* Brightness slider */
.brightness-slider {
  margin-top: 0.5rem;
  padding: 0 0.5rem;
}

.slider {
  width: 100%;
  appearance: none;
  height: 5px;
  border-radius: 5px;
  background: rgba(59, 130, 246, 0.2);
  outline: none;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.6rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

/* Type-specific box styling */
.cardiomegaly-box {
  border-color: #ef4444;
  background-color: rgba(239, 68, 68, 0.3);
}

.cardiomegaly-box .annotation-label {
  background-color: #ef4444;
}

.infiltration-box {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.3);
}

.infiltration-box .annotation-label {
  background-color: #10b981;
}

.pleural-effusion-box {
  border-color: #f59e0b;
  background-color: rgba(245, 158, 11, 0.3);
}

.pleural-effusion-box .annotation-label {
  background-color: #f59e0b;
}

.pleural-thickening-box {
  border-color: #8b5cf6;
  background-color: rgba(139, 92, 246, 0.3);
}

.pleural-thickening-box .annotation-label {
  background-color: #8b5cf6;
}

.pulmonary-fibrosis-box {
  border-color: #ec4899;
  background-color: rgba(236, 72, 153, 0.3);
}

.pulmonary-fibrosis-box .annotation-label {
  background-color: #ec4899;
}

.nodule-mass-box {
  border-color: #3b82f6;
  background-color: rgba(59, 130, 246, 0.3);
}

.nodule-mass-box .annotation-label {
  background-color: #3b82f6;
}

.consolidation-box {
  border-color: #0ea5e9;
  background-color: rgba(14, 165, 233, 0.3);
}

.consolidation-box .annotation-label {
  background-color: #0ea5e9;
}

.atelectasis-box {
  border-color: #f97316;
  background-color: rgba(249, 115, 22, 0.3);
}

.atelectasis-box .annotation-label {
  background-color: #f97316;
}

.pneumothorax-box {
  border-color: #a855f7;
  background-color: rgba(168, 85, 247, 0.3);
}

.pneumothorax-box .annotation-label {
  background-color: #a855f7;
}

/* Abnormality section styling */
.abnormality-section {
  padding: 1rem;
  border-top: 1px solid rgba(59, 130, 246, 0.2);
}

.abnormality-section h3 {
  font-size: 0.9rem;
  color: #e5e7eb;
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.subtype-label,
.color-label {
  margin-top: 1rem;
}

.select-dropdown {
  width: 100%;
  padding: 0.5rem;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  color: #e5e7eb;
  font-size: 0.85rem;
  cursor: pointer;
}

.color-picker {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.color-option {
  width: 2rem;
  height: 2rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.color-option.active {
  border-color: #ffffff;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

/* Action buttons */
.annotation-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
}

.action-button {
  padding: 12px 20px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 200px;
  border: none;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
}

.submit-btn:hover {
  background-color: #43A047;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
}

.cancel-btn:hover {
  background-color: #e53935;
}

.save-button {
  background: linear-gradient(90deg, #f92672, #ff5e98);
  color: white;
}

.expert-button {
  background: linear-gradient(90deg, #f92672, #ff5e98);
  color: white;
}

.action-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(249, 38, 114, 0.4);
}

.action-button i {
  font-size: 1.1rem;
}

/* Error Panel and Loader styles (reused from HomeView) */
.error-panel {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.error-panel h2 {
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-details {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
}

.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.error-trace {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 0.5rem;
  font-family: monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
  word-break: break-all;
  color: #f87171;
}

.loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.loader {
  width: 3rem;
  height: 3rem;
  border: 3px solid rgba(59, 130, 246, 0.3);
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .annotation-container {
    flex-direction: column;
    height: auto;
  }

  .annotation-tools {
    width: auto;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
  }

  .tool-button {
    flex-direction: row;
    gap: 0.5rem;
  }

  .tool-button i {
    margin-bottom: 0;
  }
}

@media (max-width: 768px) {
  .annotate-wrapper {
    padding: 0.75rem;
  }

  .annotate-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-actions {
    align-self: flex-end;
  }
}

.ai-image {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #0f172a;
  border-radius: 0.75rem;
}

/* Style for the image coming from the server (standardized 512x512) */
.standardized-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}

.ai-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(4px);
}

.ai-error {
  background-color: rgba(254, 226, 226, 0.9);
  border: 1px solid #ef4444;
  border-radius: 6px;
  padding: 15px;
  margin: 10px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.ai-error i {
  color: #ef4444;
  font-size: 24px;
  margin-bottom: 10px;
}

.ai-error p {
  margin: 5px 0 10px;
  color: #7f1d1d;
  font-weight: 500;
}

.retry-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background-color: #2563eb;
}

.retry-btn i {
  color: white;
  font-size: 14px;
  margin: 0;
}

.ai-confidence-summary {
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  margin: 1rem;
  transition: all 0.3s ease;
}

.ai-confidence-summary.collapsed {
  padding: 0.5rem 1rem;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.5rem;
  transition: background-color 0.2s ease;
}

.summary-header:hover {
  background: rgba(15, 23, 42, 0.8);
}

.summary-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.toggle-btn {
  background: none;
  border: none;
  color: #60a5fa;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background-color: rgba(59, 130, 246, 0.2);
  transform: translateY(-1px);
}

.toggle-btn i {
  transition: transform 0.2s ease;
}

.confidence-list {
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.4);
  margin-top: 0.25rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease-in-out;
  max-height: 300px;
  overflow-y: auto;
}

/* Add these new style classes */
.confidence-list-enter-active,
.confidence-list-leave-active {
  transition: all 0.3s ease;
  max-height: 300px;
  opacity: 1;
  overflow: hidden;
}

.confidence-list-enter-from,
.confidence-list-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0;
  margin: 0;
}

/* Style for the dropdown chevron rotation */
.toggle-btn i.bi-chevron-down {
  transform: rotate(0deg);
  transition: transform 0.3s ease;
}

.toggle-btn i.bi-chevron-up {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
}

.confidence-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.35rem;
  margin-bottom: 0.5rem;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.confidence-item:hover {
  background: rgba(15, 23, 42, 0.7);
  transform: translateX(2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.confidence-label {
  font-size: 0.85rem;
  color: #f3f4f6;
  font-weight: 500;
}

.confidence-value {
  font-size: 0.85rem;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
}

/* Ensure images have the same aspect ratio preservation */
.ai-image img {
  object-fit: contain;
}

.ai-prediction-box {
  position: absolute;
  pointer-events: none;
  box-sizing: border-box;
  z-index: 10;
}

.ai-prediction-box .annotation-label {
  display: flex !important;
  font-size: 14px !important;
  padding: 6px 12px !important;
  font-weight: bold !important;
  z-index: 20 !important;
  white-space: nowrap !important;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5) !important;
}

/* Demo mode warning - visible at top of page */
.demo-mode-warning {
  background-color: rgba(254, 226, 226, 0.25);
  border: 1px solid #ef4444;
  border-radius: 6px;
  padding: 15px;
  margin: 0 0 15px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
  }
}

.demo-mode-warning i {
  color: #ef4444;
  font-size: 24px;
  margin-bottom: 10px;
}

.demo-mode-warning span {
  margin: 5px 0 10px;
  color: #7f1d1d;
  font-weight: 700;
  font-size: 16px;
}

.demo-mode-details {
  font-size: 0.875rem;
  color: #7f1d1d;
  margin-top: 0.5rem;
}

.no-abnormalities {
  background-color: rgba(254, 226, 226, 0.9);
  border: 1px solid #ef4444;
  border-radius: 6px;
  padding: 15px;
  margin: 10px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.no-abnormalities i {
  color: #ef4444;
  font-size: 24px;
  margin-bottom: 10px;
}

.no-abnormalities p {
  margin: 5px 0 10px;
  color: #7f1d1d;
  font-weight: 500;
}

.debug-info {
  background-color: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 1rem;
}

.debug-btn {
  background-color: rgba(15, 23, 42, 0.5);
  border: none;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  color: #e5e7eb;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-left: 0.5rem;
}

.debug-btn:hover {
  background-color: rgba(59, 130, 246, 0.3);
}

.debug-btn i {
  margin-right: 0.25rem;
}

/* Styling for the new abnormality dropdown below the X-ray image */
.abnormality-selection-container {
  margin-top: 0;
  padding: 0.75rem 1rem;
  background: rgba(17, 24, 39, 0.7);
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  flex-direction: row;
  gap: 2rem;
  justify-content: flex-start;
}

.abnormality-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.selector-label {
  font-size: 0.9rem;
  color: #f9fafb;
  font-weight: 500;
  white-space: nowrap;
  min-width: 120px;
}

.selector-dropdown-container {
  min-width: 180px;
}

.select-dropdown {
  width: 100%;
  padding: 0.5rem 1rem;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  color: #f3f4f6;
  font-size: 0.9rem;
  cursor: pointer;
  appearance: auto;
  transition: all 0.2s ease;
}

.select-dropdown:hover,
.select-dropdown:focus {
  border-color: rgba(59, 130, 246, 0.7);
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}

.select-dropdown option {
  background-color: #1e293b;
  color: #f3f4f6;
}

/* Add these styles for the mock model banner */
.mock-model-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fff7ed;
  color: #9a3412;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 0.9rem;
}

.mock-model-banner i {
  font-size: 1.1rem;
}

.model-error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fff7ed;
  color: #9a3412;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 0.9rem;
}

.model-error-message i {
  font-size: 1.1rem;
}

/* Model Status Banner - used for mock model and PyTorch notifications */
.model-status-banner {
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 8px 12px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #495057;
}

.model-status-banner i {
  margin-right: 8px;
  color: #0d6efd;
  font-size: 16px;
}

/* Error container */
.error-container {
  margin-bottom: 12px;
  width: 100%;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.error-message i {
  font-size: 1.1rem;
  flex-shrink: 0;
}

/* Add transition animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Enhance image transitions */
.standardized-image {
  transition: all 0.3s ease-in-out;
}

/* Add these new styles */
.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(17, 24, 39, 0.7);
  border-radius: 0.5rem 0.5rem 0 0;
  padding: 0.75rem 1rem;
  color: #e5e7eb;
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-btn:hover:not(:disabled) {
  background: #2563eb;
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-area {
  border: 1px dashed rgba(59, 130, 246, 0.5);
  border-radius: 0.5rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  position: relative;
  background-color: rgba(13, 25, 42, 0.95);
  overflow: hidden;
  min-height: 300px;
  margin: 1rem;
  transition: all 0.3s ease;
}

.upload-area:hover {
  background-color: rgba(17, 30, 52, 0.95);
  border-color: rgba(59, 130, 246, 0.7);
}

.upload-placeholder.dragging {
  background-color: rgba(17, 34, 64, 0.95);
}

.upload-placeholder.dragging i {
  transform: scale(1.1);
  color: #60a5fa;
}

.upload-placeholder {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 2rem;
}

.upload-placeholder i {
  font-size: 3.5rem;
  color: #3b82f6;
  margin-bottom: 1.5rem;
  filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.5));
}

.upload-placeholder p {
  color: #b4c6ef;
  font-size: 0.95rem;
  line-height: 1.6;
  text-align: center;
}

.xray-image-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background-color: #000;
}

.abnormality-type-container {
  margin-top: 0;
  padding: 0.75rem 1rem;
  background: rgba(17, 24, 39, 0.7);
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  flex-direction: row;
  gap: 2rem;
  justify-content: flex-start;
}

.download-print-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem;
  background: rgba(17, 24, 39, 0.7);
  border-top: 1px solid rgba(59, 130, 246, 0.2);
}

.results-header {
  padding: 0.75rem 1rem;
  background: rgba(17, 24, 39, 0.7);
  border-radius: 0.5rem 0.5rem 0 0;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.results-header h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.model-status-banner {
  background-color: rgba(59, 130, 246, 0.15);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  margin: 0 1rem 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #e5e7eb;
}

.model-status-banner i {
  color: #60a5fa;
  font-size: 1rem;
}

.ai-image {
  flex: 1;
  min-height: 300px;
}

/* Download button styling */
.download-print-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  margin-top: 0.5rem;
}

.download-print-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(220, 38, 38, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.download-print-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(220, 38, 38, 0.3);
}

.ai-detection-results {
  background: transparent;
  border-radius: 0;
  border: none;
  margin: 0.5rem;
  overflow: hidden;
}

/* New main content area styles */
.main-content-area {
  display: flex;
  gap: 1rem;
  flex: 1;
  height: 100%;
}

.tool-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-button:hover {
  background: rgba(59, 130, 246, 0.15);
}

.tool-button i {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
  color: #60a5fa;
}

.tool-button span {
  font-size: 0.7rem;
  font-weight: 600;
  color: #e5e7eb;
}

.abnormality-type-container {
  margin-top: 0;
  padding: 0.75rem 1rem;
  background: rgba(17, 24, 39, 0.7);
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  flex-direction: row;
  gap: 2rem;
  justify-content: flex-start;
}

.abnormality-type-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.abnormality-label {
  font-size: 0.9rem;
  color: #f9fafb;
  font-weight: 500;
  white-space: nowrap;
  min-width: 120px;
}

.abnormality-select {
  min-width: 180px;
  padding: 0.5rem 1rem;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.25rem;
  color: #f3f4f6;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>');
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  padding-right: 35px;
}

.abnormality-select:hover,
.abnormality-select:focus {
  border-color: rgba(59, 130, 246, 0.7);
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}

.select-dropdown option {
  background-color: #1e293b;
  color: #f3f4f6;
}

.abnormality-label {
  font-size: 0.9rem;
  color: #f9fafb;
  font-weight: 500;
  white-space: nowrap;
}

.upload-area.has-image {
  border: none;
  padding: 0;
  margin: 0;
  background-color: #000;
  border-radius: 0;
}

.xray-image-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background-color: #000;
}

/* Make sure the image scales properly */
.xray-image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.download-print-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.download-print-btn {
  background: linear-gradient(90deg, #f92672, #ff5e98);
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.download-print-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(249, 38, 114, 0.3);
}
</style>
