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
            <div class="nav-icon"><i class="bi bi-speedometer2"></i></div>
            <div class="nav-label">Dashboard</div>
          </div>
          <div class="nav-item">
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

        <!-- Demo mode warning - positioned under header -->
        <div v-if="isUsingMockModel" class="demo-mode-warning">
          <i class="bi bi-exclamation-triangle"></i>
          <span
            >Using demo predictions with mock model (actual model file not found
            on server)</span
          >
          <p class="demo-mode-details">
            The predictions shown are simulated examples and do not represent
            actual AI analysis of your uploaded image.
          </p>
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

            <!-- Abnormality Selection -->
            <div
              class="abnormality-section"
              :class="{ disabled: !activeTool || activeTool !== 'box' }"
            >
              <h3>Abnormality Type</h3>
              <select
                v-model="selectedAbnormality"
                class="select-dropdown"
                :disabled="!activeTool || activeTool !== 'box'"
              >
                <option value="Nodule/Mass">Nodule/Mass</option>
                <option value="Cardiomegaly">Cardiomegaly</option>
                <option value="Infiltration">Infiltration</option>
                <option value="Pleural Effusion">Pleural Effusion</option>
                <option value="Pleural Thickening">Pleural Thickening</option>
                <option value="Pulmonary Fibrosis">Pulmonary Fibrosis</option>
              </select>
            </div>

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

          <!-- Main image display area -->
          <div class="image-container">
            <div class="image-title">
              Raw CXRay Name: {{ currentImageName || "No file selected" }}
              <div class="upload-button">
                <label for="xray-upload" class="file-upload-label">
                  <i class="bi bi-upload"></i> Upload X-ray
                </label>
                <input
                  id="xray-upload"
                  type="file"
                  accept="image/*"
                  @change="handleFileUpload"
                  class="hidden-file-input"
                />
              </div>
            </div>
            <div
              class="xray-image"
              @mousedown="handleMouseDown"
              @mousemove="handleMouseMove"
              @mouseup="handleMouseUp"
              @click="handleClick"
              ref="imageContainer"
            >
              <img
                v-if="currentImage"
                :src="currentImage"
                alt="X-ray image"
                ref="xrayImage"
              />
              <div v-else class="placeholder-image">
                <i class="bi bi-image"></i>
                <p>Upload an X-ray image to begin annotation</p>
                <label
                  for="xray-upload-placeholder"
                  class="upload-placeholder-button"
                >
                  <i class="bi bi-cloud-upload"></i> Select X-ray Image
                </label>
                <input
                  id="xray-upload-placeholder"
                  type="file"
                  accept="image/*"
                  @change="handleFileUpload"
                  class="hidden-file-input"
                />
              </div>

              <!-- Current box being drawn or default box -->
              <div
                v-if="showDefaultBox"
                class="annotation-box"
                :class="[
                  currentBox.type &&
                    currentBox.type.toLowerCase().replace('/', '-') + '-box',
                ]"
                :style="getBoxStyle(currentBox)"
              >
                <div
                  class="annotation-label"
                  :style="{
                    backgroundColor: getBoxColor(currentBox.type || ''),
                  }"
                >
                  {{ currentBox.type || "Unknown" }}
                </div>
              </div>

              <!-- User created boxes -->
              <div
                v-for="(box, index) in boxes"
                :key="box.id || index"
                class="annotation-box"
                :class="{
                  selected: selectedBoxIndex === index,
                  [box.type &&
                  box.type.toLowerCase().replace('/', '-') + '-box']: true,
                }"
                :style="getBoxStyle(box)"
                @mousedown="selectBox(index, $event)"
              >
                <div
                  class="annotation-label"
                  :style="{ backgroundColor: getBoxColor(box.type || '') }"
                >
                  {{ box.type || "Unknown" }}
                  <span v-if="box.score" class="confidence-score">
                    {{ formatConfidence(box.score) }}
                  </span>
                </div>
                <!-- Delete button (always visible) -->
                <button class="delete-box-btn" @click.stop="removeBox(index)">
                  <i class="bi bi-trash"></i>
                </button>
                <!-- Resize handles when box is selected -->
                <div
                  v-if="selectedBoxIndex === index"
                  class="resize-handle top-left"
                  data-handle="top-left"
                  @mousedown.stop="startResize($event, 'top-left')"
                ></div>
                <div
                  v-if="selectedBoxIndex === index"
                  class="resize-handle top-right"
                  data-handle="top-right"
                  @mousedown.stop="startResize($event, 'top-right')"
                ></div>
                <div
                  v-if="selectedBoxIndex === index"
                  class="resize-handle bottom-left"
                  data-handle="bottom-left"
                  @mousedown.stop="startResize($event, 'bottom-left')"
                ></div>
                <div
                  v-if="selectedBoxIndex === index"
                  class="resize-handle bottom-right"
                  data-handle="bottom-right"
                  @mousedown.stop="startResize($event, 'bottom-right')"
                ></div>
              </div>

              <!-- Point markers -->
              <div
                v-for="(point, index) in points"
                :key="'point-' + index"
                class="point-marker"
                :style="{ left: point.x + 'px', top: point.y + 'px' }"
              ></div>
            </div>
          </div>

          <!-- Right sidebar with AI annotations -->
          <div class="ai-annotations">
            <div class="image-title">Chest X-ray Image (AI Annotated)</div>
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
              <div v-if="isModelLoading" class="ai-loading">
                <div class="loader"></div>
                <p>Processing image with AI model...</p>
              </div>

              <!-- Error state -->
              <div v-if="modelError" class="ai-error">
                <i class="bi bi-exclamation-triangle"></i>
                <p>{{ modelError }}</p>
                <button
                  v-if="modelError && modelError.includes('loading')"
                  @click="retryModelPrediction"
                  class="retry-btn"
                >
                  <i class="bi bi-arrow-clockwise"></i> Check Again
                </button>
              </div>

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
                <button @click="debugMode = !debugMode" class="debug-btn">
                  <i class="bi bi-bug"></i>
                  {{ debugMode ? "Hide" : "Show" }} Debug Info
                </button>
                <div v-if="debugMode" class="debug-info">
                  <p><strong>Last API Response:</strong></p>
                  <pre>{{ lastApiResponse }}</pre>
                  <button @click="reduceConfidenceThreshold" class="debug-btn">
                    <i class="bi bi-gear"></i> Try Lower Threshold
                  </button>
                </div>
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

            <!-- AI Confidence Summary -->
            <div v-if="aiPredictions.length > 0" class="ai-confidence-summary">
              <h3>AI Detection Results:</h3>
              <div class="confidence-list">
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
                  <span class="confidence-label"
                    >{{ prediction.class || "Unknown" }}:</span
                  >
                  <span
                    class="confidence-value"
                    :style="{ color: getBoxColor(prediction.class || '') }"
                  >
                    {{ formatConfidence(prediction.score) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="annotation-actions">
          <button class="action-button save-button">
            <i class="bi bi-save"></i> Save Now
          </button>
          <button class="action-button expert-button">
            <i class="bi bi-check-circle"></i> Save Expert Annotation
          </button>
        </div>
      </div>

      <!-- Loading overlay -->
      <div v-if="isLoading" class="loader-overlay">
        <div class="loader"></div>
        <p>Loading annotation data...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { apiUrl, logout } from "../utils/api";
import { runNetworkTest } from "../utils/network-test";
import ModelService from "../services/modelService";

export default {
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
      selectedColor: "#3b82f6",
      colors: [
        { value: "#3b82f6", name: "Blue" },
        { value: "#ef4444", name: "Red" },
        { value: "#10b981", name: "Green" },
        { value: "#f59e0b", name: "Orange" },
      ],

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
      // Deselect any box when changing tools
      this.selectedBoxIndex = null;
      this.activeTool = tool;

      if (tool === "box") {
        // Only update cursor, don't create box automatically
        document.body.style.cursor = "crosshair";
      } else if (tool === "point") {
        document.body.style.cursor = "crosshair";
      } else {
        document.body.style.cursor = "default";
      }
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
        this.lastApiResponse = { modelStatus };

        // Check if we're using a mock model
        if (modelStatus.model_type === "mock") {
          this.isUsingMockModel = true;
          console.warn(
            "Using demo predictions with mock model - real model file not found"
          );
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

        // Store the predictions response for debugging
        this.lastApiResponse = {
          modelStatus,
          result,
          timestamp: new Date().toISOString(),
        };

        // Update the display images from the server
        this.cleanImage = result.cleanImage;
        this.annotatedImage = result.annotatedImage;

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
      // Don't process if no image is loaded
      if (!this.currentImage) return;

      const rect = this.$refs.imageContainer.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      if (this.activeTool === "box") {
        // If we already have a default box shown, check if we're clicking on it
        if (this.showDefaultBox) {
          // Check if click is inside the current default box
          if (
            mouseX >= this.currentBox.x &&
            mouseX <= this.currentBox.x + this.currentBox.width &&
            mouseY >= this.currentBox.y &&
            mouseY <= this.currentBox.y + this.currentBox.height
          ) {
            // Start dragging the default box
            this.isDraggingBox = true;
            this.dragStartX = mouseX;
            this.dragStartY = mouseY;
            this.initialBoxState = { ...this.currentBox };
          } else {
            // Add the current default box to the boxes array
            this.boxes.push({ ...this.currentBox });

            // Create a new default box at the click position
            this.currentBox = {
              x: mouseX - 50, // Center the box on the click point
              y: mouseY - 50,
              width: 100,
              height: 100,
              type: this.selectedAbnormality,
            };
          }
        } else {
          // Start drawing a new box
          this.dragStartX = mouseX;
          this.dragStartY = mouseY;
          this.currentBox = {
            x: mouseX,
            y: mouseY,
            width: 0,
            height: 0,
            type: this.selectedAbnormality,
          };
          this.isDrawingBox = true;
        }
        e.preventDefault();
      }
    },

    handleMouseMove(e) {
      if (!this.currentImage) return;

      const rect = this.$refs.imageContainer.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      if (this.isDraggingBox) {
        // Dragging the default box
        const deltaX = mouseX - this.dragStartX;
        const deltaY = mouseY - this.dragStartY;

        this.currentBox.x = this.initialBoxState.x + deltaX;
        this.currentBox.y = this.initialBoxState.y + deltaY;

        // Keep the box within the image container
        const containerRect = this.$refs.imageContainer.getBoundingClientRect();
        if (this.currentBox.x < 0) this.currentBox.x = 0;
        if (this.currentBox.y < 0) this.currentBox.y = 0;
        if (this.currentBox.x + this.currentBox.width > containerRect.width) {
          this.currentBox.x = containerRect.width - this.currentBox.width;
        }
        if (this.currentBox.y + this.currentBox.height > containerRect.height) {
          this.currentBox.y = containerRect.height - this.currentBox.height;
        }
      } else if (this.isDrawingBox) {
        // Drawing a new box
        const currentX = mouseX;
        const currentY = mouseY;

        this.currentBox.width = currentX - this.dragStartX;
        this.currentBox.height = currentY - this.dragStartY;

        // Ensure positive width and height (handles direction of drag)
        if (this.currentBox.width < 0) {
          this.currentBox.x = currentX;
          this.currentBox.width = Math.abs(this.currentBox.width);
        }

        if (this.currentBox.height < 0) {
          this.currentBox.y = currentY;
          this.currentBox.height = Math.abs(this.currentBox.height);
        }
      } else if (this.isResizing && this.selectedBoxIndex !== null) {
        this.resizeBox(e);
      } else if (this.selectedBoxIndex !== null && e.buttons === 1) {
        // Dragging an existing box
        const deltaX = mouseX - this.dragStartX;
        const deltaY = mouseY - this.dragStartY;

        const box = this.boxes[this.selectedBoxIndex];
        box.x = this.initialBoxState.x + deltaX;
        box.y = this.initialBoxState.y + deltaY;

        // Keep the box within the image container
        const containerRect = this.$refs.imageContainer.getBoundingClientRect();
        if (box.x < 0) box.x = 0;
        if (box.y < 0) box.y = 0;
        if (box.x + box.width > containerRect.width) {
          box.x = containerRect.width - box.width;
        }
        if (box.y + box.height > containerRect.height) {
          box.y = containerRect.height - box.height;
        }
      }
    },

    // eslint-disable-next-line no-unused-vars
    handleMouseUp(e) {
      if (this.isDrawingBox) {
        // Only add the box if it has a minimum size
        if (this.currentBox.width > 10 && this.currentBox.height > 10) {
          const newBox = { ...this.currentBox };
          this.boxes.push(newBox);

          // Store initial position for zoom scaling
          if (!this.initialBoxPositions.length) {
            this.initialBoxPositions = [...this.boxes].map((box) => ({
              ...box,
              x: box.x / this.zoomLevel,
              y: box.y / this.zoomLevel,
              width: box.width / this.zoomLevel,
              height: box.height / this.zoomLevel,
            }));
          } else {
            this.initialBoxPositions.push({
              ...newBox,
              x: newBox.x / this.zoomLevel,
              y: newBox.y / this.zoomLevel,
              width: newBox.width / this.zoomLevel,
              height: newBox.height / this.zoomLevel,
            });
          }

          this.selectedBoxIndex = this.boxes.length - 1;

          // Create a new default box
          this.currentBox = {
            x: Math.max(10, this.currentBox.x + 20),
            y: Math.max(10, this.currentBox.y + 20),
            width: 100,
            height: 100,
            type: this.selectedAbnormality,
          };
          this.showDefaultBox = true;
        }
        this.isDrawingBox = false;
      } else if (this.isDraggingBox) {
        this.isDraggingBox = false;

        // Update the initialBoxPositions after dragging is complete
        if (this.showDefaultBox) {
          // No need to update initialBoxPositions as it's temporary
        } else if (this.selectedBoxIndex !== null) {
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
      if (this.activeTool === "point") {
        const rect = this.$refs.imageContainer.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        this.points.push({ x, y });
      }
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

      // If opacity is null, return solid color, otherwise return rgba
      switch (type) {
        case "Nodule/Mass":
          return opacity ? `rgba(59, 130, 246, ${opacity})` : "#3b82f6";
        case "Cardiomegaly":
          return opacity ? `rgba(239, 68, 68, ${opacity})` : "#ef4444";
        case "Infiltration":
          return opacity ? `rgba(16, 185, 129, ${opacity})` : "#10b981";
        case "Pleural Effusion":
          return opacity ? `rgba(245, 158, 11, ${opacity})` : "#f59e0b";
        case "Pleural Thickening":
          return opacity ? `rgba(139, 92, 246, ${opacity})` : "#8b5cf6";
        case "Pulmonary Fibrosis":
          return opacity ? `rgba(236, 72, 153, ${opacity})` : "#ec4899";
        default:
          return opacity ? `rgba(59, 130, 246, ${opacity})` : "#3b82f6";
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
  },
  watch: {
    selectedAbnormality(newValue) {
      // Update the type of the selected box when dropdown changes
      if (this.selectedBoxIndex !== null) {
        this.boxes[this.selectedBoxIndex].type = newValue;
      }
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

    // Set default tool but don't show default box
    this.activeTool = "box";
    this.showDefaultBox = false;
  },
  beforeUnmount() {
    document.removeEventListener("click", this.closeUserMenu);
    // Reset cursor
    document.body.style.cursor = "default";
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
  margin-bottom: 40px;
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
  margin-bottom: 1.5rem;
}

.annotate-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
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
.ai-annotations {
  flex: 1;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 1rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
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
  font-size: 0.875rem;
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
}

.annotation-box.selected {
  border-width: 3px;
  border-style: dashed;
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
  z-index: 10;
}

.delete-box-btn:hover {
  background-color: #d32f2f;
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
  width: 10px;
  height: 10px;
  background-color: #f59e0b;
  border: 2px solid white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
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
  background-color: rgba(239, 68, 68, 0.5);
}

.cardiomegaly-box .annotation-label {
  background-color: #ef4444;
}

.infiltration-box {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.5);
}

.infiltration-box .annotation-label {
  background-color: #10b981;
}

.pleural-effusion-box {
  border-color: #f59e0b;
  background-color: rgba(245, 158, 11, 0.5);
}

.pleural-effusion-box .annotation-label {
  background-color: #f59e0b;
}

.pleural-thickening-box {
  border-color: #8b5cf6;
  background-color: rgba(139, 92, 246, 0.5);
}

.pleural-thickening-box .annotation-label {
  background-color: #8b5cf6;
}

.pulmonary-fibrosis-box {
  border-color: #ec4899;
  background-color: rgba(236, 72, 153, 0.5);
}

.pulmonary-fibrosis-box .annotation-label {
  background-color: #ec4899;
}

.nodule-mass-box {
  border-color: #3b82f6;
  background-color: rgba(59, 130, 246, 0.5);
}

.nodule-mass-box .annotation-label {
  background-color: #3b82f6;
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
}

.action-button {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
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
  background-color: #000;
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
}

.ai-confidence-summary h3 {
  font-size: 0.9rem;
  color: #e5e7eb;
  margin-bottom: 0.75rem;
}

.confidence-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.confidence-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 4px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.confidence-item:hover {
  background: rgba(15, 23, 42, 0.8);
  transform: translateX(2px);
}

.confidence-label {
  font-size: 0.9rem;
  color: #e5e7eb;
  font-weight: 500;
}

.confidence-value {
  font-size: 0.9rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.2);
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
  background-color: rgba(254, 226, 226, 0.9);
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
</style>
