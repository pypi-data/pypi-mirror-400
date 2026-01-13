---
title: Interactive Demo
description: "Test the social-links library directly in your browser using Pyodide. Try detecting platforms, validating URLs, and sanitizing social media links."
keywords:
  - interactive test
  - try it
  - demo
  - test social links
  - browser test
---

# Interactive Demo

Try the `social-links` library directly in your browser! This page uses [Pyodide](https://pyodide.org/) to run Python in the browser.

<div id="package-info" style="display: none; margin: 20px 0; padding: 15px; background: #e3f2fd; border-left: 4px solid #1976d2; border-radius: 4px;">
  <p style="margin: 0;"><strong>Installed package:</strong> <code>social-links</code> <span id="package-version"></span></p>
</div>

<div id="platforms-info" style="display: none; margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 4px;">
  <p style="margin: 0 0 10px 0;"><strong>Supports <span id="platform-count"></span> pre-defined platforms:</strong></p>
  <p style="margin: 0; color: #666; font-size: 0.9em;">The library comes with built-in support for these social media platforms. Each platform has pre-configured validation rules and URL patterns that are automatically applied when you use the library.</p>
  <div id="platforms-list" style="margin-top: 15px; display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px;"></div>
</div>

<div id="pyodide-loading" style="text-align: center; padding: 20px;">
  <p>Loading Pyodide...</p>
  <div class="spinner"></div>
</div>

<div id="test-interface" style="display: none;">
  <div class="test-section">
    <h3>1. Detect Platform</h3>
    <p>Enter a URL to detect which social media platform it belongs to:</p>
    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
      <input 
        type="text" 
        id="detect-input" 
        placeholder="Enter a URL to detect platform..."
        style="flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px;"
      />
      <button 
        id="detect-btn" 
        style="padding: 8px 16px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;"
      >
        Detect
      </button>
    </div>
    <div id="detect-result" style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px; min-height: 30px;"></div>
  </div>

  <div class="test-section" style="margin-top: 30px;">
    <h3>2. Validate URL</h3>
    <p>Check if a URL is valid for a specific platform:</p>
    <div style="display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
      <select 
        id="validate-platform" 
        style="flex: 0 0 180px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; background: white;"
      >
        <option value="">Select platform...</option>
      </select>
      <input 
        type="text" 
        id="validate-input" 
        placeholder="Enter a URL..."
        style="flex: 1; min-width: 200px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;"
      />
      <button 
        id="validate-btn" 
        style="padding: 8px 16px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;"
      >
        Validate
      </button>
    </div>
    <div id="validate-result" style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px; min-height: 30px;"></div>
  </div>

  <div class="test-section" style="margin-top: 30px;">
    <h3>3. Sanitize URL</h3>
    <p>Normalize a URL to its canonical format:</p>
    <div style="display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
      <select 
        id="sanitize-platform" 
        style="flex: 0 0 180px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; background: white;"
      >
        <option value="">Select platform...</option>
      </select>
      <input 
        type="text" 
        id="sanitize-input" 
        placeholder="Enter a URL..."
        style="flex: 1; min-width: 200px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;"
      />
      <button 
        id="sanitize-btn" 
        style="padding: 8px 16px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;"
      >
        Sanitize
      </button>
    </div>
    <div id="sanitize-result" style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px; min-height: 30px;"></div>
  </div>

</div>

<style>
  .test-section {
    border: 1px solid #e0e0e0;
    padding: 20px;
    border-radius: 8px;
    background: white;
  }
  
  .spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #1976d2;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 20px auto;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .result-success {
    color: #2e7d32;
    font-weight: bold;
  }
  
  .result-error {
    color: #c62828;
    font-weight: bold;
  }
  
  .result-info {
    color: #1976d2;
  }
  
  button:hover {
    background: #1565c0 !important;
  }
  
  button:active {
    background: #0d47a1 !important;
  }
  
  
  select {
    cursor: pointer;
  }
  
  select:focus {
    outline: 2px solid #1976d2;
    outline-offset: 2px;
  }
</style>

<script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>

<script type="text/javascript">
  let pyodide;
  let sl;

  async function main() {
    // Load Pyodide
    pyodide = await loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
    });
    
    // Update loading message
    document.getElementById("pyodide-loading").innerHTML = "<p>Installing social-links package...</p>";
    
    // Install social-links package
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("social-links");
    
    // Import and initialize SocialLinks
    pyodide.runPython(`
      from sociallinks import SocialLinks
      sl = SocialLinks()
      
      # Try to get package version
      try:
          import importlib.metadata
          package_version = importlib.metadata.version('social-links')
      except:
          try:
              import importlib_metadata
              package_version = importlib_metadata.version('social-links')
          except:
              package_version = "unknown"
    `);
    
    sl = pyodide.globals.get("sl");
    const packageVersion = pyodide.globals.get("package_version");
    
    // Display package version
    if (packageVersion && packageVersion !== "unknown") {
      document.getElementById("package-version").textContent = `v${packageVersion}`;
      document.getElementById("package-info").style.display = "block";
    }
    
    // Load platforms and populate dropdowns
    await populatePlatformDropdowns();
    
    // Display platforms info
    await displayPlatformsInfo();
    
    // Hide loading, show interface
    document.getElementById("pyodide-loading").style.display = "none";
    document.getElementById("test-interface").style.display = "block";
    
    // Setup event listeners
    setupEventListeners();
  }

  async function populatePlatformDropdowns() {
    try {
      const platforms = sl.list_platforms();
      const platformsList = platforms.toJs();
      const sortedPlatforms = platformsList.sort();
      
      const validateSelect = document.getElementById("validate-platform");
      const sanitizeSelect = document.getElementById("sanitize-platform");
      
      // Clear existing options (except the first placeholder)
      validateSelect.innerHTML = '<option value="">Select platform...</option>';
      sanitizeSelect.innerHTML = '<option value="">Select platform...</option>';
      
      // Add platform options
      sortedPlatforms.forEach(platform => {
        const option1 = document.createElement("option");
        option1.value = platform;
        option1.textContent = platform;
        validateSelect.appendChild(option1);
        
        const option2 = document.createElement("option");
        option2.value = platform;
        option2.textContent = platform;
        sanitizeSelect.appendChild(option2);
      });
    } catch (error) {
      console.error("Error loading platforms:", error);
    }
  }

  async function displayPlatformsInfo() {
    try {
      const platforms = sl.list_platforms();
      const platformsList = platforms.toJs();
      const sortedPlatforms = platformsList.sort();
      
      document.getElementById("platform-count").textContent = sortedPlatforms.length;
      
      const platformsListDiv = document.getElementById("platforms-list");
      platformsListDiv.innerHTML = sortedPlatforms.map(p => 
        `<code style="background: white; padding: 4px 8px; border-radius: 3px; display: inline-block; font-size: 0.9em;">${p}</code>`
      ).join('');
      
      document.getElementById("platforms-info").style.display = "block";
    } catch (error) {
      console.error("Error loading platforms info:", error);
    }
  }

  function setupEventListeners() {
    // Detect platform
    document.getElementById("detect-btn").addEventListener("click", async () => {
      const input = document.getElementById("detect-input").value;
      const resultDiv = document.getElementById("detect-result");
      
      if (!input.trim()) {
        resultDiv.innerHTML = '<span class="result-error">Please enter a URL</span>';
        return;
      }
      
      try {
        resultDiv.innerHTML = '<span class="result-info">Processing...</span>';
        const platform = sl.detect_platform(input);
        if (platform) {
          resultDiv.innerHTML = `<span class="result-success">Detected platform: <strong>${platform}</strong></span>`;
        } else {
          resultDiv.innerHTML = '<span class="result-info">No platform detected</span>';
        }
      } catch (error) {
        resultDiv.innerHTML = `<span class="result-error">Error: ${error.message}</span>`;
      }
    });
    
    // Validate URL
    document.getElementById("validate-btn").addEventListener("click", async () => {
      const platform = document.getElementById("validate-platform").value;
      const input = document.getElementById("validate-input").value;
      const resultDiv = document.getElementById("validate-result");
      
      if (!platform || !input.trim()) {
        resultDiv.innerHTML = '<span class="result-error">Please select a platform and enter a URL</span>';
        return;
      }
      
      try {
        resultDiv.innerHTML = '<span class="result-info">Processing...</span>';
        const isValid = sl.is_valid(platform, input);
        if (isValid) {
          resultDiv.innerHTML = `<span class="result-success">✓ Valid ${platform} URL</span>`;
        } else {
          resultDiv.innerHTML = `<span class="result-error">✗ Invalid ${platform} URL</span>`;
        }
      } catch (error) {
        resultDiv.innerHTML = `<span class="result-error">Error: ${error.message}</span>`;
      }
    });
    
    // Sanitize URL
    document.getElementById("sanitize-btn").addEventListener("click", async () => {
      const platform = document.getElementById("sanitize-platform").value;
      const input = document.getElementById("sanitize-input").value;
      const resultDiv = document.getElementById("sanitize-result");
      
      if (!platform || !input.trim()) {
        resultDiv.innerHTML = '<span class="result-error">Please select a platform and enter a URL</span>';
        return;
      }
      
      try {
        resultDiv.innerHTML = '<span class="result-info">Processing...</span>';
        const sanitized = sl.sanitize(platform, input);
        resultDiv.innerHTML = `<span class="result-success">Sanitized URL:</span><br><code style="background: white; padding: 5px; border-radius: 3px; display: inline-block; margin-top: 5px;">${sanitized}</code>`;
      } catch (error) {
        resultDiv.innerHTML = `<span class="result-error">Error: ${error.message}</span>`;
      }
    });
    
    
    // Allow Enter key to trigger actions
    document.getElementById("detect-input").addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        document.getElementById("detect-btn").click();
      }
    });
    
    document.getElementById("validate-input").addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        document.getElementById("validate-btn").click();
      }
    });
    
    document.getElementById("sanitize-input").addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        document.getElementById("sanitize-btn").click();
      }
    });
  }

  // Start loading Pyodide when page is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      main().catch(err => {
        document.getElementById("pyodide-loading").innerHTML = 
          `<p style="color: #c62828;">Error loading Pyodide: ${err.message}</p>`;
        console.error(err);
      });
    });
  } else {
    main().catch(err => {
      document.getElementById("pyodide-loading").innerHTML = 
        `<p style="color: #c62828;">Error loading Pyodide: ${err.message}</p>`;
      console.error(err);
    });
  }
</script>

