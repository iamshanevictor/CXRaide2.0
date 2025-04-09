import { apiUrl } from "../utils/api";

class ModelService {
  constructor() {
    this.isCheckingStatus = false;
    this.maxRetries = 3;
    this.modelInputSize = 512; // Updated to match server's resizing (512x512)
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

  // Scale the bounding boxes back to the original image size
  scaleBoxesToDisplaySize(
    predictions,
    originalWidth,
    originalHeight,
    displayWidth,
    displayHeight
  ) {
    if (!predictions || !predictions.length) return [];

    console.log("Scaling predictions to display size:");
    console.log("Original dimensions:", originalWidth, "x", originalHeight);
    console.log("Display dimensions:", displayWidth, "x", displayHeight);
    console.log("Model input size:", this.modelInputSize);

    // Calculate the scale factors based on the actual displayed image size
    // Most importantly, we need to account for the aspect ratio preservation
    const originalAspectRatio = originalWidth / originalHeight;
    const displayAspectRatio = displayWidth / displayHeight;

    let scaledWidth,
      scaledHeight,
      offsetX = 0,
      offsetY = 0;

    // Determine how the image is fit within the container
    if (displayAspectRatio > originalAspectRatio) {
      // Container is wider than the image's aspect ratio - image is constrained by height
      scaledHeight = displayHeight;
      scaledWidth = displayHeight * originalAspectRatio;
      offsetX = (displayWidth - scaledWidth) / 2; // Center horizontally
    } else {
      // Container is taller than the image's aspect ratio - image is constrained by width
      scaledWidth = displayWidth;
      scaledHeight = displayWidth / originalAspectRatio;
      offsetY = (displayHeight - scaledHeight) / 2; // Center vertically
    }

    // Calculate the actual scale factors for the visible image part
    const scaleX = scaledWidth / this.modelInputSize;
    const scaleY = scaledHeight / this.modelInputSize;

    console.log("Calculated scaling factors:", {
      scaleX,
      scaleY,
      offsetX,
      offsetY,
      scaledWidth,
      scaledHeight,
    });

    return predictions.map((pred) => {
      // Scale the bounding box coordinates and apply offsets
      const scaledBox = [
        pred.box[0] * scaleX + offsetX,
        pred.box[1] * scaleY + offsetY,
        pred.box[2] * scaleX + offsetX,
        pred.box[3] * scaleY + offsetY,
      ];

      return {
        ...pred,
        box: scaledBox,
        // Store the original image dimensions and scaling factors for reference
        originalDimensions: {
          width: originalWidth,
          height: originalHeight,
          scaleX,
          scaleY,
          offsetX,
          offsetY,
        },
      };
    });
  }

  async predict(imageFile, displayWidth, displayHeight, retryCount = 0) {
    try {
      console.log(
        `Starting prediction with display dimensions: ${displayWidth}x${displayHeight}`
      );

      // Resize the image for the model
      const {
        file: resizedFile,
        originalWidth,
        originalHeight,
        targetWidth,
        targetHeight,
        offsetX: resizeOffsetX,
        offsetY: resizeOffsetY,
      } = await this.resizeImageForModel(imageFile);

      console.log(
        `Resized image from ${originalWidth}x${originalHeight} to fit within ${this.modelInputSize}x${this.modelInputSize}`
      );

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
          return this.predict(
            imageFile,
            displayWidth,
            displayHeight,
            retryCount + 1
          );
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

      // If no display dimensions provided, return raw predictions
      if (!displayWidth || !displayHeight) {
        return data.predictions.map((pred) => ({
          box: pred.boxes,
          class: pred.label,
          score: pred.score,
        }));
      }

      // Process the predictions to account for aspect ratio preservation and scaling
      const processedPredictions = data.predictions.map((pred) => {
        // First, adjust for the offset within the model's input square (due to aspect ratio preservation)
        const [x1, y1, x2, y2] = pred.boxes;

        // Adjust box coordinates to account for the centering offsets in the input image
        const adjustedBox = [
          x1 - resizeOffsetX,
          y1 - resizeOffsetY,
          x2 - resizeOffsetX,
          y2 - resizeOffsetY,
        ];

        // Now scale based on the display size while maintaining the same aspect ratio
        const imageAspectRatio = originalWidth / originalHeight;
        const containerAspectRatio = displayWidth / displayHeight;

        let scaledImageWidth,
          scaledImageHeight,
          displayOffsetX = 0,
          displayOffsetY = 0;

        if (containerAspectRatio > imageAspectRatio) {
          // Container is wider than image
          scaledImageHeight = displayHeight;
          scaledImageWidth = displayHeight * imageAspectRatio;
          displayOffsetX = (displayWidth - scaledImageWidth) / 2;
        } else {
          // Container is taller than image
          scaledImageWidth = displayWidth;
          scaledImageHeight = displayWidth / imageAspectRatio;
          displayOffsetY = (displayHeight - scaledImageHeight) / 2;
        }

        // Calculate scale factors based on the actual image size within target dimensions
        const scaleX = scaledImageWidth / targetWidth;
        const scaleY = scaledImageHeight / targetHeight;

        // Scale the box to the displayed dimensions
        const displayBox = [
          adjustedBox[0] * scaleX + displayOffsetX,
          adjustedBox[1] * scaleY + displayOffsetY,
          adjustedBox[2] * scaleX + displayOffsetX,
          adjustedBox[3] * scaleY + displayOffsetY,
        ];

        console.log(`Prediction ${pred.label}:`, {
          serverBox: pred.boxes,
          adjustedBox,
          displayBox,
          offsets: {
            resizeOffsetX,
            resizeOffsetY,
            displayOffsetX,
            displayOffsetY,
          },
          scales: { scaleX, scaleY },
          dimensions: { scaledImageWidth, scaledImageHeight },
        });

        return {
          box: displayBox,
          class: pred.label,
          score: pred.score,
          // Store details for debugging
          debug: {
            originalBox: pred.boxes,
            adjustedBox,
            resizeOffsets: { x: resizeOffsetX, y: resizeOffsetY },
            displayOffsets: { x: displayOffsetX, y: displayOffsetY },
            scales: { x: scaleX, y: scaleY },
            dimensions: { width: scaledImageWidth, height: scaledImageHeight },
            aspectRatios: {
              image: imageAspectRatio,
              container: containerAspectRatio,
            },
          },
        };
      });

      console.log("Processed predictions:", processedPredictions);
      return processedPredictions;
    } catch (error) {
      console.error("Error making prediction:", error);
      throw error;
    }
  }
}

export default new ModelService();
