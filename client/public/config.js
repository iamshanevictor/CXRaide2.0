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

  // Detect local development
  if (window.location.hostname === "localhost") {
    window.__ENV__.VITE_API_URL = "http://localhost:5000";
    console.log("[Config] Development mode detected - using local API");
  }
  
  // Add protocol if missing in API URL
  if (window.__ENV__.VITE_API_URL && !window.__ENV__.VITE_API_URL.startsWith('http')) {
    window.__ENV__.VITE_API_URL = window.location.protocol + '//' + window.__ENV__.VITE_API_URL;
    console.log("[Config] Added protocol to API URL:", window.__ENV__.VITE_API_URL);
  }
})();

// Fix CORS and path issues
(function () {
  // Override fetch to add proper headers
  const originalFetch = window.fetch;
  window.fetch = function (url, options = {}) {
    // Ensure options and headers exist
    options = options || {};
    options.headers = options.headers || {};
    
    // Add CORS headers
    options.credentials = options.credentials || 'include';
    options.mode = options.mode || 'cors';
    
    // Add content type if not present and method is POST
    if (options.method === 'POST' && !options.headers['Content-Type']) {
      options.headers['Content-Type'] = 'application/json';
    }
    
    // Handle API paths
    if (typeof url === "string") {
      // If URL starts with /api, prepend the API URL
      if (url.startsWith("/api")) {
        url = window.__ENV__.VITE_API_URL + url.substring(4);
      }
      // If URL doesn't have protocol and looks like an API call
      else if (
        !url.includes("://") &&
        (url.startsWith("/login") ||
          url.startsWith("/health") ||
          url.startsWith("/check-session"))
      ) {
        url = window.__ENV__.VITE_API_URL + url;
      }
    }

    console.log("[Fetch] Request to:", url);
    return originalFetch(url, options);
  };

  // Add error handler for uncaught promise rejections
  window.addEventListener('unhandledrejection', function(event) {
    console.error('[Config] Unhandled promise rejection:', event.reason);
    // We could add more detailed error reporting here
  });
})();
