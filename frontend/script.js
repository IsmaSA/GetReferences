/**
 * Citation Extractor - Frontend JavaScript
 * Handles file uploads, drag-and-drop, and API communication
 */

// =============================================================================
// DOM Elements
// =============================================================================

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const keywordInput = document. getElementById('keyword-input');
const extractBtn = document.getElementById('extract-btn');
const resultsSection = document. getElementById('results-section');
const resultsInfo = document. getElementById('results-info');
const resultsContainer = document.getElementById('results-container');
const copyBtn = document.getElementById('copy-btn');
const errorMessage = document. getElementById('error-message');

// =============================================================================
// State
// =============================================================================

let uploadedFiles = [];

// =============================================================================
// File Upload Handling
// =============================================================================

/**
 * Handle file selection from input or drop
 * @param {FileList} files - Selected files
 */
function handleFiles(files) {
    const validExtensions = ['.docx', '. txt'];
    
    for (const file of files) {
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        
        if (! validExtensions.includes(ext)) {
            showError(`Unsupported file type: ${file.name}.  Only .docx and .txt files are supported.`);
            continue;
        }
        
        // Check for duplicates
        if (uploadedFiles.some(f => f. name === file.name && f.size === file.size)) {
            continue;
        }
        
        uploadedFiles.push(file);
    }
    
    updateFileList();
    updateExtractButton();
    hideError();
}

/**
 * Update the displayed file list
 */
function updateFileList() {
    fileList.innerHTML = '';
    
    uploadedFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        
        const icon = file.name.endsWith('.docx') ? '📄' : '📝';
        const size = formatFileSize(file. size);
        
        item.innerHTML = `
            <div class="file-item-info">
                <span class="file-item-icon">${icon}</span>
                <span class="file-item-name">${escapeHtml(file.name)}</span>
                <span class="file-item-size">(${size})</span>
            </div>
            <button class="file-item-remove" data-index="${index}" title="Remove file">×</button>
        `;
        
        fileList.appendChild(item);
    });
    
    // Add remove handlers
    fileList.querySelectorAll('.file-item-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.dataset.index);
            uploadedFiles.splice(index, 1);
            updateFileList();
            updateExtractButton();
        });
    });
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// =============================================================================
// Drag and Drop Handling
// =============================================================================

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone. classList.add('drag-over');
});

dropZone. addEventListener('dragleave', (e) => {
    e. preventDefault();
    dropZone.classList. remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
    }
});

// Click on drop zone triggers file input
dropZone. addEventListener('click', (e) => {
    if (e. target. tagName !== 'LABEL' && e.target. tagName !== 'INPUT') {
        fileInput.click();
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target. files.length > 0) {
        handleFiles(e. target.files);
        fileInput.value = ''; // Reset input
    }
});

// =============================================================================
// Form Validation
// =============================================================================

/**
 * Update extract button state based on form validity
 */
function updateExtractButton() {
    const hasFiles = uploadedFiles.length > 0;
    const hasKeyword = keywordInput.value.trim().length > 0;
    
    extractBtn.disabled = !(hasFiles && hasKeyword);
}

keywordInput.addEventListener('input', updateExtractButton);

// =============================================================================
// API Communication
// =============================================================================

/**
 * Extract references from uploaded files
 */
async function extractReferences() {
    const keyword = keywordInput. value.trim();
    
    if (uploadedFiles.length === 0 || ! keyword) {
        return;
    }
    
    // Update UI to loading state
    setLoading(true);
    hideError();
    hideResults();
    
    try {
        // Build form data
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });
        formData.append('keyword', keyword);
        
        // Send request to backend
        const response = await fetch('/extract', {
            method: 'POST',
            body: formData
        });
        
        if (! response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response. status}`);
        }
        
        const data = await response.json();
        displayResults(data. references, keyword);
        
    } catch (error) {
        showError(error.message || 'An error occurred while processing your request.');
    } finally {
        setLoading(false);
    }
}

extractBtn.addEventListener('click', extractReferences);

// Allow Enter key to trigger extraction
keywordInput. addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !extractBtn. disabled) {
        extractReferences();
    }
});

// =============================================================================
// Results Display
// =============================================================================

/**
 * Display extracted references
 * @param {string[]} references - List of extracted references
 * @param {string} keyword - The keyword used for extraction
 */
function displayResults(references, keyword) {
    resultsSection.hidden = false;
    
    if (references.length === 0) {
        resultsInfo. textContent = `No references found near "${keyword}"`;
        resultsContainer.innerHTML = `
            <div class="no-results">
                <p>No citations were found in proximity to your keyword.</p>
                <p>Try a different keyword or check your documents. </p>
            </div>
        `;
        copyBtn.hidden = true;
        return;
    }
    
    resultsInfo.textContent = `Found ${references.length} reference${references.length !== 1 ? 's' : ''} linked to "${keyword}"`;
    
    resultsContainer. innerHTML = references.map((ref, index) => `
        <div class="reference-item">
            <span class="reference-number">${index + 1}.</span>
            <span class="reference-text">${escapeHtml(ref)}</span>
        </div>
    `).join('');
    
    copyBtn. hidden = false;
}

/**
 * Hide results section
 */
function hideResults() {
    resultsSection.hidden = true;
    resultsContainer.innerHTML = '';
    copyBtn.hidden = true;
}

// =============================================================================
// Copy to Clipboard
// =============================================================================

copyBtn.addEventListener('click', async () => {
    const references = Array.from(resultsContainer.querySelectorAll('.reference-text'))
        .map(el => el.textContent)
        .join('\n');
    
    try {
        await navigator.clipboard. writeText(references);
        
        // Visual feedback
        const originalText = copyBtn.textContent;
        copyBtn. textContent = '✓ Copied! ';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    } catch (err) {
        showError('Failed to copy to clipboard');
    }
});

// =============================================================================
// UI Helpers
// =============================================================================

/**
 * Set loading state
 * @param {boolean} loading - Whether loading is active
 */
function setLoading(loading) {
    extractBtn.disabled = loading;
    
    const btnText = extractBtn.querySelector('. btn-text');
    const btnLoading = extractBtn.querySelector('.btn-loading');
    
    btnText.hidden = loading;
    btnLoading.hidden = !loading;
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.hidden = false;
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.hidden = true;
}