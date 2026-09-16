/* ============================================================================
   Font Recognition Page - JavaScript
   Handles image upload and font recognition
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    const removeImageBtn = document.getElementById('removeImage');
    const recognizeBtn = document.getElementById('recognizeBtn');
    const resultsSection = document.getElementById('results');
    const fontsList = document.getElementById('fontsList');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');

    let selectedFile = null;

    // ========================================================================
    // File Upload Handlers
    // ========================================================================

    uploadArea.addEventListener('click', () => imageInput.click());

    imageInput.addEventListener('change', handleFileSelect);

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            imageInput.files = files;
            handleFileSelect({ target: { files: files } });
        }
    });

    // ========================================================================
    // Image Selection Handler
    // ========================================================================

    function handleFileSelect(event) {
        const files = event.target.files;
        
        if (files.length === 0) {
            return;
        }

        const file = files[0];
        
        // Validate file type
        const validTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/webp', 'image/tiff', 'image/svg+xml'];
        if (!validTypes.includes(file.type)) {
            showError('Please select a valid image file (PNG, JPG, GIF, BMP, WEBP, TIFF, or SVG)');
            return;
        }

        // Validate file size (10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            showError('File size exceeds 10MB limit');
            return;
        }

        selectedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            uploadArea.style.display = 'none';
            imagePreview.style.display = 'block';
            recognizeBtn.disabled = false;
            resultsSection.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    // Remove/Change image
    removeImageBtn.addEventListener('click', () => {
        selectedFile = null;
        imageInput.value = '';
        previewImage.src = '';
        uploadArea.style.display = 'block';
        imagePreview.style.display = 'none';
        recognizeBtn.disabled = true;
        resultsSection.style.display = 'none';
        fontsList.innerHTML = '';
    });

    // ========================================================================
    // Font Recognition Handler
    // ========================================================================

    recognizeBtn.addEventListener('click', recognizeFonts);

    function recognizeFonts() {
        if (!selectedFile) {
            showError('Please select an image first');
            return;
        }

        showLoading();
        errorMessage.style.display = 'none';

        const formData = new FormData();
        formData.append('image', selectedFile);

        fetch('/api/recognize-font', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            if (data.fonts && data.fonts.length > 0) {
                displayResults(data.fonts);
                resultsSection.style.display = 'block';
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                showError('No fonts detected. Please try with a different image.');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Recognition error:', error);
            showError('Error recognizing fonts: ' + error.message);
        });
    }

    // ========================================================================
    // Display Results
    // ========================================================================

    function displayResults(fonts) {
        fontsList.innerHTML = '';

        fonts.forEach((font, index) => {
            const fontElement = createFontElement(font, index);
            fontsList.appendChild(fontElement);
        });
    }

    function createFontElement(font, index) {
        const div = document.createElement('div');
        div.className = 'font-result';
        
        const confidence = Math.round(font.confidence * 100);
        const confidenceColor = confidence > 80 ? '#4caf50' : confidence > 60 ? '#ff9800' : '#f44336';

        let sourcesHTML = '';
        if (font.sources && font.sources.length > 0) {
            sourcesHTML = '<div class="font-sources"><h4>Available in:</h4>';
            font.sources.forEach(source => {
                sourcesHTML += `
                    <a href="${source.url}" target="_blank" class="source-link">
                        ${source.name} <small>(${source.availability})</small>
                    </a>
                `;
            });
            sourcesHTML += '</div>';
        }

        div.innerHTML = `
            <h3>${font.name}</h3>
            <div class="font-info">
                <label>Type:</label>
                <span>${font.type || 'Unknown'}</span>
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

        return div;
    }

    // ========================================================================
    // UI Helpers
    // ========================================================================

    function showLoading() {
        loadingSpinner.style.display = 'block';
    }

    function hideLoading() {
        loadingSpinner.style.display = 'none';
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 6000);
    }

    // ========================================================================
    // Paste from Clipboard Support
    // ========================================================================

    document.addEventListener('paste', (e) => {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].kind === 'file' && items[i].type.startsWith('image/')) {
                e.preventDefault();
                const file = items[i].getAsFile();
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                imageInput.files = dataTransfer.files;
                handleFileSelect({ target: { files: dataTransfer.files } });
                return;
            }
        }
    });

    // ========================================================================
    // Screenshot Capture Support
    // ========================================================================

    // Check if browser supports Screenshot API
    if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
        const screenshotBtn = document.createElement('button');
        screenshotBtn.className = 'btn btn-secondary';
        screenshotBtn.textContent = '📸 Capture Screenshot';
        screenshotBtn.style.marginTop = '1rem';
        
        screenshotBtn.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({ 
                    video: { mediaSource: 'screen' } 
                });
                
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                
                video.onloadedmetadata = () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0);
                    
                    stream.getTracks().forEach(track => track.stop());
                    
                    canvas.toBlob((blob) => {
                        const file = new File([blob], 'screenshot.png', { type: 'image/png' });
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(file);
                        imageInput.files = dataTransfer.files;
                        handleFileSelect({ target: { files: dataTransfer.files } });
                    });
                };
            } catch (error) {
                console.log('Screenshot capture cancelled or failed:', error);
            }
        });
        
        // Add screenshot button after recognize button
        recognizeBtn.parentNode.insertBefore(screenshotBtn, recognizeBtn.nextSibling);
    }
});
