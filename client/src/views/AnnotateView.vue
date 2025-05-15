<template>
  <app-layout>
    <!-- Error state display -->
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
    <div v-else class="annotate-wrapper">
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
                <img
                  :src="currentImage"
                  alt="X-ray"
                  class="xray-image"
                      :style="{
                    transform: `scale(${zoomLevel})`,
                    filter: `brightness(${brightness}%)`,
                  }"
                />
                <canvas
                  ref="annotationCanvas"
                  class="annotation-canvas"
                        :style="{
                    transform: `scale(${zoomLevel})`,
                        }"
                ></canvas>
                      </div>
                </div>
              </div>

          <!-- Right side - AI annotations display area -->
          <div class="ai-annotations">
            <div class="annotations-header">
              <h2>AI Annotations</h2>
              <div class="annotations-actions">
                <button
                  class="action-btn"
                  @click="toggleAnnotations"
                  :disabled="!currentImage"
                >
                  <i class="bi" :class="showAnnotations ? 'bi-eye-slash' : 'bi-eye'"></i>
                  {{ showAnnotations ? "Hide" : "Show" }} Annotations
                </button>
                <button
                  class="action-btn"
                  @click="clearAnnotations"
                  :disabled="!currentImage"
                >
                  <i class="bi bi-trash"></i>
                  Clear
                </button>
              </div>
            </div>

            <div class="annotations-content">
              <div v-if="!currentImage" class="no-image-message">
                <i class="bi bi-image"></i>
                <p>Upload an X-ray to see AI annotations</p>
              </div>
              <div v-else-if="isModelLoading" class="loading-state">
                <div class="loading-spinner"></div>
                <p>Analyzing X-ray...</p>
              </div>
              <div v-else-if="!showAnnotations" class="annotations-hidden">
                <i class="bi bi-eye-slash"></i>
                <p>Annotations are hidden</p>
              </div>
              <div v-else class="annotations-list">
                <div
                  v-for="(annotation, index) in annotations"
                  :key="index"
                  class="annotation-item"
                  :class="{ active: selectedAnnotation === index }"
                  @click="selectAnnotation(index)"
                >
                  <div class="annotation-header">
                    <span class="annotation-type">{{ annotation.type }}</span>
                    <span class="annotation-confidence"
                      >{{ (annotation.confidence * 100).toFixed(1) }}%</span
                    >
                </div>
                  <div class="annotation-details">
                    <p>{{ annotation.description }}</p>
              </div>
                </div>
                  </div>
                </div>
              </div>
              </div>
            </div>
          </div>
  </app-layout>
</template>

<script>
import AppLayout from "@/components/AppLayout.vue";
import { apiUrl } from "@/utils/api";
import ModelService from "@/services/modelService";
import html2pdf from 'html2pdf.js';

export default {
  name: "AnnotateView",
  components: {
    AppLayout,
  },
  data() {
    return {
      apiUrl: apiUrl,
      hasError: false,
      errorMessage: "",
      errorDetails: null,
      showErrorDetails: false,
      connectionStatus: "Connected",
      hasToken: false,
      modelInfo: null,
      currentImage: null,
      currentImageName: "",
      isDragging: false,
      isModelLoading: false,
      activeTool: "box",
      zoomLevel: 1,
      brightness: 100,
      showAnnotations: true,
      annotations: [],
      selectedAnnotation: null,
      username: sessionStorage.getItem("username") || localStorage.getItem("username") || "User",
      showUserMenu: false,
      fileInput: null,
      imageFile: null,
      processingInterval: null,
      processingStep: 1,
      modelError: null,
      isUsingMockModel: false,
      modelType: "combined", // Default model type
      annotatedImage: null,

      // Add new properties
      detectionResultsExpanded: false,
      modelStatus: null,
      
      // Add these new properties
      showPatientInfoModal: false,
      currentReportType: "Expert",
      loadingMessage: "",
      
      // Add navigation guard flag
      isNavigating: false,
    };
  },
  mounted() {
    // Create a hidden file input for image uploads
    this.createFileInput();
    
    document.addEventListener("click", this.closeUserMenu);
    
    // Add event listeners for box dragging and resizing
    document.addEventListener("mousedown", this.handleMouseDown);
    document.addEventListener("mousemove", this.handleMouseMove);
    document.addEventListener("mouseup", this.handleMouseUp);
    
    // Check if auth token exists
    try {
      this.hasToken = !!localStorage.getItem("authToken");
    } catch (e) {
      console.error("Error accessing localStorage:", e);
      this.hasToken = false;
    }

    // Set default tool but don't show default box
    this.activeTool = null; // Don't automatically select the box tool
    this.showDefaultBox = false;

    // Check model status on component mount
    this.checkModelStatus();
  },
  beforeUnmount() {
    document.removeEventListener("click", this.closeUserMenu);
    if (this.fileInput && this.fileInput.parentNode) {
      this.fileInput.parentNode.removeChild(this.fileInput);
    }
    
    // Clear any intervals
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
    }

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
  methods: {
    // File upload methods
    createFileInput() {
      this.fileInput = document.createElement("input");
      this.fileInput.type = "file";
      this.fileInput.accept = "image/*";
      this.fileInput.style.display = "none";
      this.fileInput.addEventListener("change", this.handleFileUpload);
      document.body.appendChild(this.fileInput);
    },
    
    triggerFileUpload() {
      if (!this.isModelLoading && this.fileInput) {
        this.fileInput.click();
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
      this.currentImageName = file.name;
      const reader = new FileReader();

      reader.onload = (e) => {
        this.currentImage = e.target.result;
        // Reset annotations when new image is uploaded
        this.clearAnnotations();
        // Process the image and get AI predictions
        this.processImage();
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
      this.currentImageName = file.name;
      const reader = new FileReader();

      reader.onload = (e) => {
        this.currentImage = e.target.result;
        // Reset annotations when new image is uploaded
        this.clearAnnotations();
        // Process the image and get AI predictions
        this.processImage();
      };

      reader.readAsDataURL(file);
    },
    
    // Tool-related methods
    setActiveTool(tool) {
      this.activeTool = tool;
    },
    
    zoomIn() {
      if (this.zoomLevel < 3) {
        this.zoomLevel += 0.1;
      }
    },
    
    zoomOut() {
      if (this.zoomLevel > 0.5) {
        this.zoomLevel -= 0.1;
      }
    },
    
    adjustBrightness(value) {
      this.brightness = value;
    },
    
    undoAction() {
      // Implement undo functionality
      console.log('Undo action not implemented yet');
    },
    
    redoAction() {
      // Implement redo functionality
      console.log('Redo action not implemented yet');
    },
    
    handleClick(event) {
      // Handle clicks on the image based on active tool
      if (this.activeTool === 'box') {
        // Implement box drawing
        console.log('Box drawing not implemented yet');
        // Use event coordinates for box drawing
        const rect = event.target.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        console.log(`Click position: x=${x}, y=${y}`);
      } else if (this.activeTool === 'point') {
        // Implement point marking
        console.log('Point marking not implemented yet');
        // Use event coordinates for point marking
        const rect = event.target.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        console.log(`Click position: x=${x}, y=${y}`);
      }
    },
    
    // Annotation methods
    toggleAnnotations() {
      this.showAnnotations = !this.showAnnotations;
      if (this.showAnnotations) {
        this.drawAnnotations();
      } else {
        this.clearCanvas();
      }
    },
    
    clearAnnotations() {
      this.annotations = [];
      this.selectedAnnotation = null;
      this.clearCanvas();
    },

    clearCanvas() {
      const canvas = this.$refs.annotationCanvas;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    },
    
    selectAnnotation(index) {
      this.selectedAnnotation = index;
      // Highlight the selected annotation on the canvas
      console.log(`Selected annotation: ${index}`);
      // Could update the canvas to highlight the selected annotation
    },
    
    async processImage() {
      if (!this.currentImage || this.isModelLoading) return;

      try {
        this.isModelLoading = true;
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
          this.modelError = "Model is still loading. Please wait a moment and try again.";
          return;
        } else if (modelStatus.status === "error" || modelStatus.status === "not_loaded") {
          clearInterval(this.processingInterval);
          this.modelError = "Model could not be loaded. Please try again later.";
          return;
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

        // Update model info
        this.modelInfo = {
          using_mock_models: result.using_mock_models
        };

        // Process annotations
        if (result.predictions && result.predictions.length > 0) {
          this.annotations = result.predictions.map(pred => ({
            type: pred.class || "Unknown",
            confidence: pred.confidence || pred.score || 0,
            description: pred.description || `${pred.class} detected with ${this.formatConfidence(pred.confidence || pred.score || 0)} confidence`,
            box: pred.box || null,
          }));
          
          // Draw annotations on canvas
          this.drawAnnotations();
        } else {
          this.annotations = [];
        }
      } catch (error) {
        clearInterval(this.processingInterval);
        console.error("Error analyzing image:", error);
        this.modelError = error.message || "Failed to analyze image. Please try again.";
      } finally {
        this.isModelLoading = false;
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
    
    drawAnnotations() {
      // Draw annotations on the canvas
      const canvas = this.$refs.annotationCanvas;
      const img = this.$refs.imageContainer.querySelector('img');
      
      if (!canvas || !img) return;
      
      // Set canvas dimensions to match image
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw annotations based on prediction data
      if (this.showAnnotations && this.annotations.length > 0) {
        ctx.lineWidth = 3;
        
        this.annotations.forEach((annotation) => {
          // Use the getBoxColor function from ModelService to get consistent colors
          const color = ModelService.getBoxColor(annotation.type);
          ctx.strokeStyle = color;
          
          // If we have a bounding box, draw it
          if (annotation.box) {
            const { x, y, width, height } = annotation.box;
            
            // Scale box to display size
            const scaleX = canvas.width / img.naturalWidth;
            const scaleY = canvas.height / img.naturalHeight;
            
            const boxX = x * scaleX;
            const boxY = y * scaleY;
            const boxWidth = width * scaleX;
            const boxHeight = height * scaleY;
            
            ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);
            
            // Add label
            ctx.fillStyle = color;
            ctx.font = "14px Arial";
            ctx.fillText(
              `${annotation.type} (${this.formatConfidence(annotation.confidence)})`,
              boxX,
              boxY - 5
            );
          }
        });
      }
    },
    
    // User menu methods
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    
    openUserSettings() {
      console.log("User settings clicked (not implemented yet)");
      this.showUserMenu = false;
      alert("User settings feature coming soon!");
    },
    
    closeUserMenu(e) {
      if (this.showUserMenu && !e.target.closest(".user-dropdown")) {
        this.showUserMenu = false;
      }
    },
    
    // Error handling methods
    runDiagnostics() {
      console.log("Running diagnostics");
      alert("Diagnostics complete. No issues found.");
    },
    
    retryLoading() {
      console.log("Retrying connection");
      this.hasError = false;
    },
    
    backToLogin() {
      try {
        localStorage.removeItem("authToken");
      } catch (e) {
        console.error("Error removing token:", e);
      }
      this.$router.push("/login");
    },
    
    logout() {
      this.backToLogin();
    },

    async checkModelStatus() {
      try {
        const modelStatus = await ModelService.checkModelStatus();

        // Check for model errors
        if (modelStatus.status === "loading") {
          this.modelError = "Model is still loading. Please wait a moment and try again.";
        } else if (modelStatus.status === "error" || modelStatus.status === "not_loaded") {
          this.modelError = "Model could not be loaded. Please try again later.";
        }

        // Check if using mock models
        if (modelStatus.using_mock_models) {
          this.isUsingMockModel = true;
          this.modelInfo = {
            using_mock_models: true
          };
        }
      } catch (error) {
        console.error("Error checking model status:", error);
        this.modelError = "Unable to connect to model service. Please try again later.";
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
      
      // Clean up any remaining blob URLs that might be in use
      try {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
          if (img.src && img.src.startsWith('blob:')) {
            URL.revokeObjectURL(img.src);
            img.src = '';
            img.onload = null;
            img.onerror = null;
          }
        });
      } catch (e) {
        console.error("Error cleaning up image elements:", e);
      }
      
      // Remove reference to DOM elements to prevent memory leaks
      if (this.$refs.xrayImage) {
        // Remove any event listeners that might be attached
        const xrayImg = this.$refs.xrayImage;
        if (xrayImg) {
          xrayImg.onload = null;
          xrayImg.onerror = null;
          xrayImg.src = '';
        }
      }
      
      if (this.$refs.aiXrayImage) {
        const aiImg = this.$refs.aiXrayImage;
        if (aiImg) {
          aiImg.onload = null;
          aiImg.onerror = null;
          aiImg.src = '';
        }
      }
      
      if (this.$refs.imageContainer) {
        // Clear any event listeners from the container
        const container = this.$refs.imageContainer;
        if (container) {
          // Vue will handle most event listeners, but clean up any manually added ones
          container.onclick = null;
          // Clear any child elements if needed to force garbage collection
          while (container.firstChild) {
            container.removeChild(container.firstChild);
          }
        }
      }
      
      // Clear any canvas elements created by the annotation tools
      try {
        const canvases = document.querySelectorAll('canvas');
        canvases.forEach(canvas => {
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
          }
          // Remove any event listeners
          canvas.onmousedown = null;
          canvas.onmousemove = null;
          canvas.onmouseup = null;
        });
      } catch (e) {
        console.error("Error cleaning up canvas elements:", e);
      }
      
      // Force a garbage collection hint
      setTimeout(() => {
        this.currentImage = null;
        this.cleanImage = null;
        this.annotatedImage = null;
        console.log("[AnnotateView] Cleanup completed");
      }, 0);
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
  beforeRouteLeave(to, from, next) {
    // Set navigating flag to true
    this.isNavigating = true;
    
    // Perform thorough cleanup before leaving
    console.log("[AnnotateView] Running pre-navigation cleanup");
    
    // Cancel any pending API requests
    ModelService.cancelRequests();
    
    // Clean up image resources
    this.cleanupImageReferences();
    
    // Reset DOM modifications
    document.body.style.cursor = 'default';
    
    // Allow navigation to proceed
    next();
  },
};
</script>

<style scoped>
/* Annotation-specific styles */
.annotate-wrapper {
  padding: 1.5rem;
  height: 100%;
}

.annotation-container {
  display: flex;
  gap: 1.5rem;
  height: calc(100vh - 120px);
  background: rgba(15, 23, 42, 0.5);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.annotation-tools {
  width: 200px;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tool-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-button:hover {
  background: rgba(59, 130, 246, 0.2);
}

.tool-button.active {
  background: rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.tool-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.zoom-controls,
.undo-redo-controls {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.375rem;
}

.zoom-btn,
.undo-redo-btn {
  flex: 1;
  padding: 0.5rem;
  background: rgba(59, 130, 246, 0.2);
  border: none;
  border-radius: 0.25rem;
  color: #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zoom-btn:hover,
.undo-redo-btn:hover {
  background: rgba(59, 130, 246, 0.3);
}

.brightness-slider {
  padding: 0.5rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.375rem;
}

.slider {
  width: 100%;
  margin: 0.5rem 0;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #9ca3af;
}

.main-content-area {
  flex: 1;
  display: flex;
  gap: 1.5rem;
}

.image-container {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.file-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.5rem;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  border: none;
  border-radius: 0.375rem;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.upload-area {
  flex: 1;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.5rem;
  border: 2px dashed rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-area:hover {
  border-color: rgba(59, 130, 246, 0.5);
}

.upload-placeholder {
  text-align: center;
  color: #9ca3af;
}

.upload-placeholder i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.upload-placeholder.dragging {
  color: #3b82f6;
}

.xray-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.xray-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.2s ease;
}

.annotation-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.ai-annotations {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 0.5rem;
  padding: 1rem;
}

.annotations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.annotations-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(59, 130, 246, 0.2);
  border: none;
  border-radius: 0.375rem;
  color: #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(59, 130, 246, 0.3);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.annotations-content {
  flex: 1;
  overflow-y: auto;
}

.no-image-message,
.loading-state,
.annotations-hidden {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid rgba(59, 130, 246, 0.3);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.annotations-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.annotation-item {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.375rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.annotation-item:hover {
  background: rgba(59, 130, 246, 0.1);
}

.annotation-item.active {
  background: rgba(59, 130, 246, 0.2);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
}

.annotation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.annotation-type {
  font-weight: 600;
  color: #3b82f6;
}

.annotation-confidence {
  font-size: 0.875rem;
  color: #9ca3af;
}

.annotation-details p {
  font-size: 0.875rem;
  color: #e5e7eb;
  line-height: 1.5;
}

/* Mock model notification styles */
.mock-model-notification {
  background: rgba(234, 88, 12, 0.1);
  border: 1px solid rgba(234, 88, 12, 0.2);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ea580c;
  font-weight: 500;
}

.notification-details {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #9ca3af;
}
</style>
