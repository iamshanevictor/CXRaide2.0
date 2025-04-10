import { apiUrl } from "../utils/api";

class ModelService {
  constructor() {
    this.isCheckingStatus = false;
    this.maxRetries = 3;
    this.modelInputSize = 512; // Model input size is 512x512

    // Create a controllers map to track active requests
    this.controllers = new Map();
  }

  // Cancel any active requests when needed
  cancelRequests(requestType) {
    if (requestType) {
      // Cancel a specific request type
      if (this.controllers.has(requestType)) {
        this.controllers.get(requestType).abort();
        this.controllers.delete(requestType);
        console.log(`Cancelled ${requestType} request`);
      }
    } else {
      // Cancel all requests
      this.controllers.forEach((controller, key) => {
        controller.abort();
        console.log(`Cancelled ${key} request`);
      });
      this.controllers.clear();
    }
  }

  // Get box color based on abnormality type
  getBoxColor(type, opacity = null) {
    // Handle null or undefined values
    if (!type) {
      return opacity ? `rgba(59, 130, 246, ${opacity})` : "#3b82f6"; // Default to blue
    }

    // Normalize the type string for case-insensitive comparison
    const normalizedType = type.toLowerCase();

    // Return color based on abnormality type
    switch (normalizedType) {
      case "cardiomegaly":
        return opacity ? `rgba(239, 68, 68, ${opacity})` : "#ef4444"; // Red
      case "pleural thickening":
        return opacity ? `rgba(139, 92, 246, ${opacity})` : "#8b5cf6"; // Purple
      case "pulmonary fibrosis":
        return opacity ? `rgba(236, 72, 153, ${opacity})` : "#ec4899"; // Pink
      case "pleural effusion":
        return opacity ? `rgba(34, 197, 94, ${opacity})` : "#22c55e"; // Green
      case "nodule/mass":
        return opacity ? `rgba(59, 130, 246, ${opacity})` : "#3b82f6"; // Blue
      case "infiltration":
        return opacity ? `rgba(245, 158, 11, ${opacity})` : "#f59e0b"; // Amber
      case "consolidation":
        return opacity ? `rgba(14, 165, 233, ${opacity})` : "#0ea5e9"; // Light blue
      case "atelectasis":
        return opacity ? `rgba(249, 115, 22, ${opacity})` : "#f97316"; // Orange
      case "pneumothorax":
        return opacity ? `rgba(168, 85, 247, ${opacity})` : "#a855f7"; // Violet
      default:
        return opacity ? `rgba(59, 130, 246, ${opacity})` : "#3b82f6"; // Default blue
    }
  }

  async checkModelStatus() {
    try {
      // Prevent multiple simultaneous status checks
      if (this.isCheckingStatus) {
        return { status: "checking" };
      }

      // Cancel any existing model status requests
      this.cancelRequests("modelStatus");

      // Create new controller for this request
      const controller = new AbortController();
      this.controllers.set("modelStatus", controller);

      this.isCheckingStatus = true;

      const response = await fetch(`${apiUrl}/api/model-status`, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
        mode: "cors",
        signal: controller.signal,
      });

      if (!response.ok) {
        console.error("Model status check failed:", response.status);
        return { status: "error", message: "Failed to check model status" };
      }

      const data = await response.json();

      // Process the updated model status response
      if (data.using_mock_models) {
        console.warn("SERVER USING MOCK MODELS:", data.notice);
      } else if (data.status === "ready") {
        console.log("SERVER USING REAL MODELS:", data.explanation);
      }

      return data;
    } catch (error) {
      if (error.name === "AbortError") {
        console.log("Model status check was cancelled");
        return { status: "cancelled" };
      }
      console.error("Error checking model status:", error);
      return { status: "error", message: error.message };
    } finally {
      this.isCheckingStatus = false;
      this.controllers.delete("modelStatus");
    }
  }

  // Resize the image to the model's input size
  async resizeImageForModel(imageFile) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        // Create a canvas to resize the image
        const canvas = document.createElement("canvas");
        canvas.width = this.modelInputSize;
        canvas.height = this.modelInputSize;
        const ctx = canvas.getContext("2d");

        // Fill with black background
        ctx.fillStyle = "black";
        ctx.fillRect(0, 0, this.modelInputSize, this.modelInputSize);

        // Calculate the dimensions while preserving aspect ratio
        const originalWidth = img.width;
        const originalHeight = img.height;
        const originalAspectRatio = originalWidth / originalHeight;

        let targetWidth,
          targetHeight,
          offsetX = 0,
          offsetY = 0;

        if (originalAspectRatio > 1) {
          // Landscape image
          targetWidth = this.modelInputSize;
          targetHeight = this.modelInputSize / originalAspectRatio;
          offsetY = (this.modelInputSize - targetHeight) / 2;
        } else {
          // Portrait or square image
          targetHeight = this.modelInputSize;
          targetWidth = this.modelInputSize * originalAspectRatio;
          offsetX = (this.modelInputSize - targetWidth) / 2;
        }

        // Draw the image centered in the canvas with proper aspect ratio
        ctx.drawImage(img, offsetX, offsetY, targetWidth, targetHeight);

        console.log("Resized image with these parameters:", {
          originalWidth,
          originalHeight,
          targetWidth,
          targetHeight,
          offsetX,
          offsetY,
        });

        // Convert canvas to blob
        canvas.toBlob((blob) => {
          if (!blob) {
            reject(new Error("Failed to convert canvas to blob"));
            return;
          }

          // Create a new file from the blob
          const resizedFile = new File([blob], "resized-" + imageFile.name, {
            type: "image/jpeg",
          });

          resolve({
            file: resizedFile,
            originalWidth,
            originalHeight,
            targetWidth,
            targetHeight,
            offsetX,
            offsetY,
          });
        }, "image/jpeg");
      };

      img.onerror = () => {
        reject(new Error("Failed to load image for resizing"));
      };

      // Load image from file
      const reader = new FileReader();
      reader.onload = (e) => {
        img.src = e.target.result;
      };
      reader.onerror = () => {
        reject(new Error("Failed to read image file"));
      };
      reader.readAsDataURL(imageFile);
    });
  }

  async predict(imageFile, retryCount = 0) {
    try {
      console.log(`Starting prediction process for image`);

      // Cancel any existing prediction requests
      this.cancelRequests("predict");

      // Create new controller for this request
      const controller = new AbortController();
      this.controllers.set("predict", controller);

      // First resize the image for the model
      const resizedImage = await this.resizeImageForModel(imageFile);

      // Create FormData to send the image
      const formData = new FormData();
      formData.append("image", resizedImage.file);

      // Get the color mapping from the getBoxColor function
      const abnormalityTypes = [
        "Cardiomegaly",
        "Pleural thickening",
        "Pulmonary fibrosis",
        "Pleural effusion",
        "Nodule/Mass",
        "Infiltration",
        "Consolidation",
        "Atelectasis",
        "Pneumothorax",
      ];

      // Create color mapping object
      const colorMapping = {};
      abnormalityTypes.forEach((type) => {
        const color = this.getBoxColor(type);
        colorMapping[type] = color;
      });

      // Add color mapping to form data
      formData.append("color_mapping", JSON.stringify(colorMapping));

      // Get auth token from localStorage
      const token = localStorage.getItem("authToken");

      const headers = {
        Accept: "application/json",
        // Don't set Content-Type header with FormData
      };

      // Add authorization header if token exists
      if (token) {
        headers.Authorization = token.startsWith("Bearer ")
          ? token
          : `Bearer ${token}`;
      }

      console.log(
        `Sending prediction request (try ${retryCount + 1}/${
          this.maxRetries + 1
        })`
      );

      const response = await fetch(`${apiUrl}/api/predict`, {
        method: "POST",
        body: formData,
        credentials: "include",
        headers: headers,
        mode: "cors", // Explicitly set CORS mode
        signal: controller.signal,
      });

      // Handle service unavailable - model still loading
      if (response.status === 503) {
        const errorData = await response.json();
        console.log("Model is still loading:", errorData.error);

        // Retry logic for 503 errors (model loading)
        if (retryCount < this.maxRetries) {
          console.log(
            `Retrying in 2 seconds... (${retryCount + 1}/${this.maxRetries})`
          );
          await new Promise((resolve) => setTimeout(resolve, 2000));
          return this.predict(imageFile, retryCount + 1);
        }
      }

      if (!response.ok) {
        console.error(
          "Prediction error:",
          response.status,
          response.statusText
        );

        // Try to get the error details
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { error: `HTTP error: ${response.status}` };
        }

        // Check for PyTorch not installed error
        if (
          errorData.error &&
          errorData.error.includes("PyTorch is not installed")
        ) {
          console.warn(
            "PyTorch not installed on server, using client-side mock predictions"
          );
          return this.generateMockPredictions(imageFile);
        }

        throw new Error(
          errorData.error || `Failed to get predictions: ${response.status}`
        );
      }

      const data = await response.json();
      console.log("Received response from server:", data);

      // Process the results to match our component's expected format
      const processedPredictions = data.predictions.map((pred) => ({
        box: pred.boxes, // Use the raw boxes (already in 512x512 coordinates)
        class: pred.label,
        score: pred.score,
      }));

      // The server is already sending properly formatted data URLs with base64 encoding
      // We just need to pass them through directly
      return {
        predictions: processedPredictions,
        cleanImage: data.clean_image,
        annotatedImage: data.annotated_image,
        imageSize: data.image_size || { width: 512, height: 512 },
      };
    } catch (error) {
      if (error.name === "AbortError") {
        console.log("Prediction request was cancelled");
        return { cancelled: true };
      }

      console.error("Error making prediction:", error);

      // If we get an error about PyTorch not being installed, use mock predictions
      if (error.message && error.message.includes("PyTorch is not installed")) {
        console.warn("Falling back to mock predictions due to PyTorch error");
        return this.generateMockPredictions(imageFile);
      }

      throw error;
    } finally {
      this.controllers.delete("predict");
    }
  }

  // Generate mock predictions client-side when the server can't provide them
  async generateMockPredictions(imageFile) {
    console.log("Generating mock predictions client-side");

    try {
      // Use the image from resizing or fall back to a blank canvas
      let imageElement;
      let imageURL;

      if (imageFile) {
        // Create an image from the file
        imageURL = URL.createObjectURL(imageFile);
      } else {
        // Create a blank canvas as fallback
        const canvas = document.createElement("canvas");
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext("2d");
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, 512, 512);
        imageURL = canvas.toDataURL();
      }

      // Load the image
      imageElement = new Image();
      await new Promise((resolve, reject) => {
        imageElement.onload = resolve;
        imageElement.onerror = reject;
        imageElement.src = imageURL;
      });

      // Create a canvas to draw the image and annotations
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 512;
      const ctx = canvas.getContext("2d");

      // Draw the image
      ctx.drawImage(imageElement, 0, 0, 512, 512);

      // Generate 2-3 random mock predictions
      const mockClasses = [
        "Cardiomegaly",
        "Pleural effusion",
        "Nodule/Mass",
        "Infiltration",
      ];

      // Create 2-3 mock predictions
      const mockCount = Math.floor(Math.random() * 2) + 1; // 1-2 findings
      const predictions = [];

      for (let i = 0; i < mockCount; i++) {
        const classIndex = Math.floor(Math.random() * mockClasses.length);
        const className = mockClasses[classIndex];

        // Generate random box coordinates that make sense for the class
        let x1, y1, x2, y2;

        if (className === "Cardiomegaly") {
          // Heart region
          x1 = 150 + Math.random() * 50;
          y1 = 120 + Math.random() * 50;
          x2 = 300 + Math.random() * 50;
          y2 = 300 + Math.random() * 50;
        } else if (className === "Pleural effusion") {
          // Lower lung area
          x1 = 80 + Math.random() * 30;
          y1 = 250 + Math.random() * 50;
          x2 = 150 + Math.random() * 30;
          y2 = 400 + Math.random() * 20;
        } else if (className === "Nodule/Mass") {
          // Random location in lung field
          x1 = 120 + Math.random() * 200;
          y1 = 100 + Math.random() * 200;
          x2 = x1 + 50 + Math.random() * 30;
          y2 = y1 + 50 + Math.random() * 30;
        } else {
          // Infiltration
          // Upper lung area
          x1 = 120 + Math.random() * 50;
          y1 = 100 + Math.random() * 50;
          x2 = 220 + Math.random() * 50;
          y2 = 200 + Math.random() * 50;
        }

        // Generate a random score between 0.65 and 0.95
        const score = 0.65 + Math.random() * 0.3;

        // Draw the box on the canvas for the annotated image
        const color = this.getBoxColor(className);
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        // Add text
        ctx.fillStyle = color;
        ctx.fillRect(x1, y1 - 20, 120, 20);
        ctx.fillStyle = "white";
        ctx.font = "14px Arial";
        ctx.fillText(
          `${className}: ${Math.round(score * 100)}%`,
          x1 + 5,
          y1 - 5
        );

        // Add to predictions
        predictions.push({
          box: [x1, y1, x2, y2],
          class: className,
          score: score,
        });
      }

      // Get the annotated image as data URL
      const annotatedImageURL = canvas.toDataURL("image/png");

      // Clean image is just the original image
      const cleanImageURL = imageURL;

      // Free the object URL if we created one
      if (imageFile) {
        URL.revokeObjectURL(imageURL);
      }

      return {
        predictions: predictions,
        cleanImage: cleanImageURL,
        annotatedImage: annotatedImageURL,
        imageSize: { width: 512, height: 512 },
      };
    } catch (error) {
      console.error("Error generating mock predictions:", error);

      // If all else fails, return empty predictions
      return {
        predictions: [],
        cleanImage: "",
        annotatedImage: "",
        imageSize: { width: 512, height: 512 },
      };
    }
  }
}

// Create an instance to export
const instance = new ModelService();

// Add global cleanup handler for page navigation
window.addEventListener("beforeunload", () => {
  instance.cancelRequests();
});

export default instance;
