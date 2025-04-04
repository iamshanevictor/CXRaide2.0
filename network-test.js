// ============================================================
// CXRaide Network Test & Debugging Script
// ============================================================
// Instructions:
// 1. Save this file to client/public/network-test.js
// 2. Add the script tag to your index.html:
//    <script src="/network-test.js"></script>
// 3. Access your site and open the browser console
// ============================================================

(function () {
  console.log("CXRaide Network Test Script loaded");

  // Configuration
  const config = {
    endpoints: ["/health", "/"],
    timeout: 5000,
  };

  // Get API URL from environment or data attribute
  const apiUrl =
    document.querySelector('meta[name="api-url"]')?.getAttribute("content") ||
    window.__ENV__?.VITE_API_URL ||
    "https://cxraide-backend.onrender.com";

  // Display test info
  console.log("======= CXRaide Network Test =======");
  console.log("API URL:", apiUrl);
  console.log("Browser:", navigator.userAgent);
  console.log("Protocol:", window.location.protocol);
  console.log("Hostname:", window.location.hostname);

  // CORS test function
  async function testEndpoint(endpoint) {
    const url = `${apiUrl}${endpoint}`;
    console.log(`Testing endpoint: ${url}`);

    try {
      // Test without credentials first
      const noCredentials = await fetch(url, {
        method: "GET",
        mode: "cors",
        headers: {
          Accept: "application/json",
        },
        timeout: config.timeout,
      });

      console.log(`✅ Basic fetch successful for ${endpoint}`, {
        status: noCredentials.status,
        ok: noCredentials.ok,
        headers: [...noCredentials.headers.entries()],
      });

      // Now test with credentials
      const withCredentials = await fetch(url, {
        method: "GET",
        mode: "cors",
        credentials: "include",
        headers: {
          Accept: "application/json",
        },
        timeout: config.timeout,
      });

      console.log(`✅ Credentials fetch successful for ${endpoint}`, {
        status: withCredentials.status,
        ok: withCredentials.ok,
        headers: [...withCredentials.headers.entries()],
      });

      return true;
    } catch (error) {
      console.error(`❌ Fetch failed for ${endpoint}:`, error.message);
      return false;
    }
  }

  // Test CORS headers
  function testCorsHeaders(url) {
    const xhr = new XMLHttpRequest();
    xhr.open("OPTIONS", url, true);
    xhr.setRequestHeader("Access-Control-Request-Method", "GET");
    xhr.setRequestHeader(
      "Access-Control-Request-Headers",
      "Content-Type,Authorization,Accept"
    );
    xhr.onload = function () {
      console.log("CORS preflight response headers:", {
        "Access-Control-Allow-Origin": xhr.getResponseHeader(
          "Access-Control-Allow-Origin"
        ),
        "Access-Control-Allow-Methods": xhr.getResponseHeader(
          "Access-Control-Allow-Methods"
        ),
        "Access-Control-Allow-Headers": xhr.getResponseHeader(
          "Access-Control-Allow-Headers"
        ),
        "Access-Control-Allow-Credentials": xhr.getResponseHeader(
          "Access-Control-Allow-Credentials"
        ),
      });
    };
    xhr.onerror = function () {
      console.error("❌ CORS preflight request failed");
    };
    xhr.send();
  }

  // Fix common issues
  function applyFixes() {
    // 1. Add axios interceptors to debug network requests
    if (window.axios) {
      window.axios.interceptors.request.use((request) => {
        console.log("🚀 Request:", request.method, request.url, request);
        return request;
      });

      window.axios.interceptors.response.use(
        (response) => {
          console.log(
            "✅ Response:",
            response.status,
            response.config.url,
            response
          );
          return response;
        },
        (error) => {
          console.error(
            "❌ Response Error:",
            error.message,
            error.config?.url,
            error
          );
          return Promise.reject(error);
        }
      );
      console.log("✅ Axios interceptors installed");
    } else {
      console.warn("⚠️ Axios not found - interceptors not installed");
    }

    // 2. Workaround for CORS+credentials issues
    if (window.localStorage) {
      localStorage.setItem("network_test_completed", "true");
      console.log("✅ Local storage working");
    }
  }

  // Run tests
  async function runTests() {
    console.log("Running network tests...");

    // 1. Test CORS headers
    testCorsHeaders(`${apiUrl}/health`);

    // 2. Test each endpoint
    for (const endpoint of config.endpoints) {
      await testEndpoint(endpoint);
    }

    // 3. Apply fixes
    applyFixes();

    console.log("✅ Network tests completed");
    console.log("==================================");
  }

  // Run tests when page loads
  if (document.readyState === "complete") {
    runTests();
  } else {
    window.addEventListener("load", runTests);
  }
})();
