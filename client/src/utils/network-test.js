/**
 * Network Testing Utility
 *
 * This file provides tools to diagnose network connectivity issues
 * between the frontend client and backend API.
 */

import { apiUrl } from "./api";

/**
 * Run a comprehensive network test to check connectivity
 * to the backend API and diagnose any issues.
 */
export async function runNetworkTest() {
  console.group("🔍 CXRaide Network Diagnostic Test");
  console.log("Starting network tests...");

  // Display environment information
  console.log("Environment Info:");
  console.log("- Protocol:", window.location.protocol);
  console.log("- Host:", window.location.host);
  console.log("- Origin:", window.location.origin);
  console.log("- API URL:", apiUrl);

  // Test basic connectivity with fetch
  console.log("\nTesting basic connectivity with fetch API...");
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${apiUrl}/health`, {
      method: "GET",
      mode: "cors",
      credentials: "include",
      signal: controller.signal,
      headers: {
        Accept: "application/json",
      },
    });

    clearTimeout(timeoutId);

    console.log("Fetch Status:", response.status);
    console.log("Fetch Status Text:", response.statusText);
    console.log("Response Headers:", Array.from(response.headers.entries()));

    const data = await response.json();
    console.log("Response Data:", data);
  } catch (error) {
    console.error("Fetch Error:", error.name, error.message);

    // Check for specific error types
    if (error.name === "AbortError") {
      console.error("🚨 Connection timed out after 5 seconds");
    } else if (
      error.name === "TypeError" &&
      error.message.includes("NetworkError")
    ) {
      console.error("🚨 CORS error or network failure");
      console.log("Possible causes:");
      console.log("1. Backend CORS not configured correctly");
      console.log("2. Backend server not running");
      console.log("3. Network/firewall blocking the connection");
    }
  }

  // Test API URL resolution
  console.log("\nTesting DNS resolution...");
  try {
    const url = new URL(apiUrl);
    console.log("API hostname:", url.hostname);

    // Ping test (this will only work on browsers that support sendBeacon)
    const startTime = Date.now();
    const pingSuccess = navigator.sendBeacon(`${apiUrl}/health`);
    const pingTime = Date.now() - startTime;

    console.log(
      "Ping test:",
      pingSuccess ? `Success (${pingTime}ms)` : "Failed"
    );
  } catch (error) {
    console.error("URL parsing error:", error.message);
  }

  // Provide recommendations
  console.log("\nRecommendations:");
  console.log("1. Check that the backend server is running");
  console.log("2. Verify CORS is properly configured on the backend");
  console.log(`3. Confirm the API URL is correct: ${apiUrl}`);
  console.log("4. Check for network/firewall restrictions");

  console.log("\nNetwork test complete");
  console.groupEnd();

  return {
    apiUrl,
    browserInfo: {
      userAgent: navigator.userAgent,
      protocol: window.location.protocol,
      host: window.location.host,
    },
  };
}

// Export a function to inject the test into a Vue component
export function injectNetworkTest(component) {
  if (!component.methods) component.methods = {};
  component.methods.runNetworkTest = runNetworkTest;
  return component;
}

export default runNetworkTest;
