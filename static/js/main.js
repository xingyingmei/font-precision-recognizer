/* ============================================================================
   Main JavaScript - Utilities and Common Functions
   ============================================================================ */

// API Configuration
const API_BASE = '/api';

// ============================================================================
// API Helper Functions
// ============================================================================

async function apiCall(endpoint, options = {}) {
    /**
     * Make API calls with error handling
     */
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function uploadImage(file) {
    /**
     * Upload image for recognition
     */
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch(`${API_BASE}/recognize-font`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Upload Error:', error);
        throw error;
    }
}

// ============================================================================
// DOM Utilities
// ============================================================================

function showElement(selector) {
    const element = document.querySelector(selector);
    if (element) element.style.display = 'block';
}

function hideElement(selector) {
    const element = document.querySelector(selector);
    if (element) element.style.display = 'none';
}

function toggleElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

function clearElement(selector) {
    const element = document.querySelector(selector);
    if (element) element.innerHTML = '';
}

function setText(selector, text) {
    const element = document.querySelector(selector);
    if (element) element.textContent = text;
}

// ============================================================================
// Message Display Functions
// ============================================================================

function showMessage(message, type = 'info', duration = 5000) {
    /**
     * Show a temporary message to the user
     * Types: 'info', 'success', 'error', 'warning'
     */
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    messageDiv.textContent = message;
    messageDiv.style.position = 'fixed';
    messageDiv.style.top = '20px';
    messageDiv.style.right = '20px';
    messageDiv.style.zIndex = '10000';
    messageDiv.style.minWidth = '300px';
    messageDiv.style.padding = '1rem';
    messageDiv.style.borderRadius = '4px';
    messageDiv.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';

    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, duration);
}

function showError(message, duration = 6000) {
    showMessage(message, 'error', duration);
}

function showSuccess(message, duration = 5000) {
    showMessage(message, 'success', duration);
}

function showInfo(message, duration = 5000) {
    showMessage(message, 'info', duration);
}

// ============================================================================
// Loading/Spinner Functions
// ============================================================================

function showSpinner(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.id = `spinner-${containerId}`;
    container.appendChild(spinner);
}

function hideSpinner(containerId) {
    const spinner = document.getElementById(`spinner-${containerId}`);
    if (spinner) spinner.remove();
}

// ============================================================================
// Font Display Functions
// ============================================================================

function createFontCard(font) {
    /**
     * Create a formatted font card element
     */
    const card = document.createElement('div');
    card.className = 'font-result';

    const confidence = Math.round(font.confidence * 100);
    const confidenceColor = confidence > 80 ? '#4caf50' : confidence > 60 ? '#ff9800' : '#f44336';

    let sourcesHTML = '';
    if (font.sources && font.sources.length > 0) {
        sourcesHTML = '<div class="font-sources"><h4>Available in:</h4>';
        font.sources.slice(0, 5).forEach(source => {
            sourcesHTML += `
                <a href="${encodeURI(source.url)}" target="_blank" class="source-link">
                    ${escapeHtml(source.name)} 
                    <small>(${escapeHtml(source.availability)})</small>
                </a>
            `;
        });
        if (font.sources.length > 5) {
            sourcesHTML += `<small>+${font.sources.length - 5} more sources</small>`;
        }
        sourcesHTML += '</div>';
    }

    card.innerHTML = `
        <h3>${escapeHtml(font.name)}</h3>
        <div class="font-info">
            <label>Type:</label>
            <span>${escapeHtml(font.type || 'Unknown')}</span>
        </div>
        <div class="font-info">
            <label>Confidence:</label>
            <span>${confidence}%</span>
        </div>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${confidence}%; background-color: ${confidenceColor};"></div>
        </div>
        ${sourcesHTML}
    `;

    return card;
}

// ============================================================================
// Utility Functions
// ============================================================================

function escapeHtml(text) {
    /**
     * Escape HTML special characters to prevent XSS
     */
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatBytes(bytes) {
    /**
     * Format bytes to human readable format
     */
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function slugify(text) {
    /**
     * Convert text to URL-friendly format
     */
    return text
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '-')
        .replace(/^-+|-+$/g, '');
}

function debounce(func, wait) {
    /**
     * Debounce function calls
     */
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================================================
// Image Processing
// ============================================================================

function imageToBase64(file) {
    /**
     * Convert image file to base64
     */
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function validateImageFile(file) {
    /**
     * Validate image file type and size
     */
    const validTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/webp', 'image/tiff', 'image/svg+xml'];
    
    if (!validTypes.includes(file.type)) {
        return { valid: false, error: 'Invalid file type. Please use PNG, JPG, GIF, BMP, WEBP, TIFF, or SVG.' };
    }

    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        return { valid: false, error: `File size exceeds 10MB limit. Your file: ${formatBytes(file.size)}` };
    }

    return { valid: true };
}

// ============================================================================
// Browser Detection
// ============================================================================

function getBrowserInfo() {
    /**
     * Get browser information
     */
    const ua = navigator.userAgent;
    let browser = 'Unknown';
    let version = 'Unknown';

    if (ua.indexOf('Firefox') > -1) {
        browser = 'Firefox';
        version = ua.substring(ua.indexOf('Firefox') + 8);
    } else if (ua.indexOf('Chrome') > -1) {
        browser = 'Chrome';
        version = ua.substring(ua.indexOf('Chrome') + 7);
    } else if (ua.indexOf('Safari') > -1) {
        browser = 'Safari';
        version = ua.substring(ua.indexOf('Version') + 8);
    }

    return { browser, version };
}

function supportsScreenCapture() {
    /**
     * Check if browser supports Screen Capture API
     */
    return !!(navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia);
}

function supportsCopyPaste() {
    /**
     * Check if browser supports clipboard paste
     */
    return !!navigator.clipboard;
}

// ============================================================================
// Data Storage
// ============================================================================

function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('LocalStorage not available:', e);
    }
}

function getLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (e) {
        console.warn('LocalStorage not available:', e);
        return null;
    }
}

function removeLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (e) {
        console.warn('LocalStorage not available:', e);
    }
}

// ============================================================================
// URL Utilities
// ============================================================================

function getURLParameter(param) {
    /**
     * Get URL query parameter value
     */
    const params = new URLSearchParams(window.location.search);
    return params.get(param);
}

function buildQueryString(params) {
    /**
     * Build URL query string from object
     */
    const searchParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
            searchParams.append(key, params[key]);
        }
    });
    return searchParams.toString();
}

// ============================================================================
// Analytics/Logging
// ============================================================================

function logEvent(eventName, eventData = {}) {
    /**
     * Log event for analytics
     */
    console.log(`[Event] ${eventName}`, eventData);
    
    // Could be extended to send to analytics service
    // Example: sendToAnalytics(eventName, eventData);
}

function logError(error, context = {}) {
    /**
     * Log error for debugging
     */
    console.error(`[Error]`, error, context);
    
    // Could be extended to send to error tracking service
    // Example: sendToErrorTracking(error, context);
}

// ============================================================================
// Initialize on Document Ready
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Check browser capabilities and add warnings if needed
    if (!supportsCopyPaste() && !supportsScreenCapture()) {
        console.warn('Some advanced features may not be available in this browser');
    }

    // Add global error handler
    window.addEventListener('error', (event) => {
        logError(event.error, { type: 'uncaughtError' });
    });

    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        logError(event.reason, { type: 'unhandledPromiseRejection' });
    });
});

// ============================================================================
// Export for modules (if needed)
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        apiCall,
        uploadImage,
        showMessage,
        showError,
        showSuccess,
        escapeHtml,
        formatBytes,
        validateImageFile,
        imageToBase64
    };
}
