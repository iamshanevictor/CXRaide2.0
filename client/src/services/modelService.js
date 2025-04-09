import { apiUrl } from "../utils/api";

class ModelService {
  constructor() {
    this.isCheckingStatus = false;
    this.maxRetries = 3;
    this.modelInputSize = 512; // Model input size is 512x512
  }

  async checkModelStatus() {
    try {
      // Prevent multiple simultaneous status checks
      if (this.isCheckingStatus) {
        return { status: "checking" };
      }

      this.isCheckingStatus = true;

      const response = await fetch(`${apiUrl}/model-status`, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
        mode: "cors",
      });

      if (!response.ok) {
        console.error("Model status check failed:", response.status);
        return { status: "error", message: "Failed to check model status" };
      }

      const data = await response.json();

      // If using mock model, log a warning
      if (data.model_type === "mock") {
        console.warn("SERVER USING MOCK MODEL:", data.warning);
      }

      return data;
    } catch (error) {
      console.error("Error checking model status:", error);
      return { status: "error", message: error.message };
    } finally {
      this.isCheckingStatus = false;
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

      // Resize the image for the model - this is still needed for the request
      const { file: resizedFile } = await this.resizeImageForModel(imageFile);

      const formData = new FormData();
      formData.append("image", resizedFile);

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

      const response = await fetch(`${apiUrl}/predict`, {
        method: "POST",
        body: formData,
        credentials: "include",
        headers: headers,
        mode: "cors", // Explicitly set CORS mode
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
        const errorData = await response
          .json()
          .catch(() => ({ error: `HTTP error: ${response.status}` }));
        throw new Error(
          errorData.error || `Failed to get predictions: ${response.status}`
        );
      }

      const data = await response.json();
      console.log("Received response from server:", data);

      // The server now sends:
      // 1. The predictions (data.predictions)
      // 2. The clean image (data.clean_image) - without annotations
      // 3. The annotated image (data.annotated_image) - with pre-rendered boxes
      // 4. The image size (data.image_size) - always 512x512

      // Process the results to match our component's expected format
      const processedPredictions = data.predictions.map((pred) => ({
        box: pred.boxes, // Use the raw boxes (already in 512x512 coordinates)
        class: pred.label,
        score: pred.score,
      }));

      return {
        predictions: processedPredictions,
        cleanImage: data.clean_image,
        annotatedImage: data.annotated_image,
        imageSize: data.image_size || { width: 512, height: 512 },
      };
    } catch (error) {
      console.error("Error making prediction:", error);
      throw error;
    }
  }
}

export default new ModelService();
