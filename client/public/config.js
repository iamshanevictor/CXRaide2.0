// Global Configuration for CXRaide Application
// This file is loaded before Vue.js and provides global constants

(function () {
  // Global environment variables
  window.__ENV__ = {
    // Default Production API URL - can be overridden by environment variables at build time
    VITE_API_URL: "https://cxraide-backend.onrender.com",

    // Default base URL for the router
    VITE_BASE_URL: "/",
  };

  console.log("[Config] Using API URL:", window.__ENV__.VITE_API_URL);

  // Optional: You can add runtime detection to change the URL based on hostname
  if (window.location.hostname === "localhost") {
    window.__ENV__.VITE_API_URL = "http://localhost:8080";
    console.log("[Config] Development mode detected - using local API");
  }
})();

// Fix common issues
(function () {
  // Override fetch to add proper headers
  const originalFetch = window.fetch;
  window.fetch = function (url, options = {}) {
    // If URL is relative and starts with /api, prepend the API URL
    if (typeof url === "string" && url.startsWith("/api")) {
      url = window.__ENV__.VITE_API_URL + url.substring(4);
    }

    // If URL is relative but doesn't have protocol and we're making a request to the API
    if (
      typeof url === "string" &&
      !url.includes("://") &&
      (url.includes("/login") ||
        url.includes("/health") ||
        url.includes("/check-session"))
    ) {
      url = window.__ENV__.VITE_API_URL + url;
    }

    return originalFetch(url, options);
  };

  // Override XMLHttpRequest to fix local requests
  const originalOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (
    method,
    url,
    async,
    user,
    password
  ) {
    // If URL is a string and might be a backend API call
    if (
      typeof url === "string" &&
      !url.includes("://") &&
      (url.includes("/login") ||
        url.includes("/health") ||
        url.includes("/check-session"))
    ) {
      url = window.__ENV__.VITE_API_URL + url;
    }

    return originalOpen.call(this, method, url, async, user, password);
  };
})();
